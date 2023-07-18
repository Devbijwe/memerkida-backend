from flask import request, jsonify, make_response, Blueprint
from datetime import datetime,timedelta
from models import Carts, TShirts
import uuid
from main import db
from helper import login_required, user_rate_limit

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/getCarts', methods=['GET'])
@login_required
# @user_rate_limit(limit=10, per=timedelta(minutes=1))
def get_all_carts():
    
    user = request.user
    carts = Carts.query.filter_by(userId=user.userId).all()

        
    cart_list = [cart.toDictWithTshirtDetails() for cart in carts]
    return jsonify(cart_list)


@cart_bp.route('/getCarts/<string:cart_id>', methods=['GET'])
@login_required
# @user_rate_limit(limit=10, per=timedelta(minutes=1))
def get_cart(cart_id):
    user = request.user
    cart = Carts.query.filter_by(userId=user.userId, cartId=cart_id).first()
    if not cart:
        return make_response(jsonify({'error': 'Cart not found'}), 404)
    return jsonify(cart.toDictWithTshirtDetails())

@cart_bp.route('/createCarts', methods=['POST'])
@login_required
def create_cart():
    user = request.user
    data = request.json
    required_fields = ['tshirtId', 'color', 'size']
    if not all(field in data for field in required_fields):
        return make_response(jsonify({'error': 'Required fields are missing'}), 400)

    tshirt_id = data['tshirtId']
    quantity = int(data.get('quantity', 1))
    if quantity < 1:
        return make_response(jsonify({'error': 'Invalid quantity'}), 400)

    tshirt = TShirts.query.filter_by(tshirtId=tshirt_id).first()
    if not tshirt:
        return make_response(jsonify({'error': 'T-Shirt not found'}), 404)

    # Check if color and size are within the available options
    color = data['color']
    size = data['size']
    if color not in tshirt.color:
        return make_response(jsonify({'error': 'Invalid color'}), 400)
    if size not in tshirt.size:
        return make_response(jsonify({'error': 'Invalid size'}), 400)

    existing_cart = Carts.query.filter_by(userId=user.userId, tshirtId=tshirt_id, color=color, size=size).first()
    if existing_cart:
        return make_response(jsonify({'error': 'Cart already exists'}), 400)

    if quantity > tshirt.stock_quantity:
        return make_response(jsonify({'error': 'Quantity exceeds available stock'}), 400)

    new_cart = Carts(
        cartId=str(uuid.uuid4()),
        userId=user.userId,
        tshirtId=tshirt_id,
        color=color,
        size=size,
        quantity=quantity,
        date=datetime.utcnow()
    )

    db.session.add(new_cart)
    db.session.commit()
    return jsonify(new_cart.toDictWithTshirtDetails()), 201


@cart_bp.route('/updateCarts/<string:cart_id>', methods=['PUT'])
@login_required
def update_cart(cart_id):
    
    user = request.user
    cart = Carts.query.filter_by(userId=user.userId, cartId=cart_id).first()

        
    if not cart:
        return make_response(jsonify({'error': 'Cart not found'}), 404)

    data = request.json
    tshirt_id = data.get('tshirtId', cart.tshirtId)
    tshirt = TShirts.query.filter_by(tshirtId=tshirt_id).first()
    if not tshirt:
        return make_response(jsonify({'error': 'T-Shirt not found'}), 404)

    # Check if color and size are within the available options
    color = data.get('color', cart.color)
    size = data.get('size', cart.size)
    if color not in tshirt.color:
        return make_response(jsonify({'error': 'Invalid color'}), 400)
    if size not in tshirt.size:
        return make_response(jsonify({'error': 'Invalid size'}), 400)

    # Check if the updated quantity exceeds available stock
    quantity = min(data.get('quantity', cart.quantity), tshirt.stock_quantity)
    if quantity < data.get('quantity', cart.quantity):
        return make_response(jsonify({'error': 'Quantity exceeds available stock'}), 400)

    cart.tshirtId = tshirt_id
    cart.color = color
    cart.size = size
    cart.quantity = quantity

    db.session.commit()
    return jsonify(cart.toDictWithTshirtDetails()), 200


@cart_bp.route('/deleteCarts/<string:cart_id>', methods=['DELETE'])
@login_required
def delete_cart(cart_id):
    
    user = request.user
    cart = Carts.query.filter_by(userId=user.userId, cartId=cart_id).first()
    
    if not cart:
        return make_response(jsonify({'error': 'Cart not found'}), 404)

    db.session.delete(cart)
    db.session.commit()
    return jsonify({'message': 'Cart deleted successfully'}), 200
