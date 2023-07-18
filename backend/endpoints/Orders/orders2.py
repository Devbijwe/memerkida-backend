
from flask import Blueprint,request,jsonify
from main import app, db
from models import *
from datetime import timedelta
from helper import login_required,user_rate_limit
from Endpoints.Orders.helper import create_single_order

order_bp = Blueprint('orders', __name__)

# Endpoint to calculate order price
@order_bp.route('/calculate-order-price', methods=['POST'])
def calculate_order_price():
    # Assuming you have a TShirts model and a database session available
    
    # Retrieve tshirtId and quantity from the request's JSON payload
    data = request.get_json()
    tshirt_id = data.get('tshirtId')
    quantity = data.get('quantity')
    
    # Query the TShirts table based on the provided tshirt_id
    tshirt = TShirts.query.get(tshirt_id)
    
    if tshirt:
        tshirt_price = tshirt.price
        discount = tshirt.discount
        
        # Calculate the order price
        order_price = tshirt_price * quantity * (1 - discount)
        
        return jsonify({'order_price': order_price}),200
    else:
        # Handle the case when the T-shirt is not found
        return jsonify({'error': 'T-shirt not found'}), 404
# Orders
@order_bp.route('/get-my-orders', methods=['GET'])
@login_required
def get_orders():
    user=request.user
    orders = Orders.query.filter_by(userId=user.userId).all()
    orders_list = [order.toDictWithAllFields() for order in orders]
    return jsonify(orders_list)

@order_bp.route('/get-my-order/<orderId>', methods=['GET'])
@login_required
def get_order(orderId):
    user = request.user
    order = Orders.get_by_id(orderId)
    # Check if the order belongs to the user
    if not order or order.userId != user.userId:
        return jsonify({'error': 'Order not found or unauthorized access'}), 404

    order_details = order.toDictWithAllFields()
    return jsonify(order_details)

@order_bp.route('/create-orders', methods=['POST'])
@login_required
@user_rate_limit(limit=1, per=timedelta(seconds=20))
def create_order():
    data = request.get_json()
    user = request.user
    order_ids = []
    # Check if user exists
    user = Users.query.get(user.userId)
    if not user:
        return {'error': 'User not found'}, 404

    if isinstance(data, list):
        # Handle list data
        for item_data in data:
            try:
                create_single_order(item_data, user, order_ids)
            except Exception as e:
                # Rollback the session and handle the exception
                db.session.rollback()
                return {'error': str(e)}, 500
    elif isinstance(data, dict):
        # Handle single data
        try:
            create_single_order(data, user, order_ids)
        except Exception as e:
            # Rollback the session and handle the exception
            db.session.rollback()
            return {'error': str(e)}, 500
    else:
        return {'error': 'Invalid data format'}, 400

    return {'message': 'Orders created successfully', 'orderIds': order_ids}

@order_bp.route('/cancel-order/<orderId>', methods=['POST'])
@login_required
@user_rate_limit(limit=1, per=timedelta(seconds=20))
def cancel_order(orderId):
    user = request.user
    order = Orders.get_by_id(orderId)

    # Check if the order belongs to the user
    if not order or order.userId != user.userId:
        return jsonify({'error': 'Order not found or unauthorized access'}), 404

    # Check if the order is already canceled
    if order.status == 'canceled':
        return jsonify({'message': 'Order is already canceled'}), 200

    # Check if the order is within the cancellation window (8 hours)
    creation_time = order.order_date
    current_time = datetime.utcnow()
    cancellation_window = timedelta(minutes=20)
    if current_time - creation_time > cancellation_window:
        return jsonify({'error': 'Order cannot be canceled. Cancellation window has expired.'}), 400

    # Update the order status to 'canceled'
    order.status = 'canceled'
    
    try:
        db.session.commit()
        return jsonify({'message': 'Order canceled successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to cancel order'}), 500