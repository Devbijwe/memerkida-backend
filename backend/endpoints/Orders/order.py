from flask import make_response,Blueprint,request,jsonify
import uuid
from main import app, db
from models import *
from datetime import datetime
from helper import login_required

# order_bp = Blueprint('orders', __name__)


# Orders
@app.route('/orders', methods=['GET'])
@login_required
def get_orders():
    orders = Orders.query.all()
    orders_list = [order.to_dict() for order in orders]
    return jsonify(orders_list)


@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    try:
        # Check if user and address exist
        user = Users.query.get(data['userId'])
        address = Addresses.query.get(data['addressId'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
        if not address:
            return jsonify({'error': 'Address not found'}), 404

        new_order = Orders(**data)
        db.session.add(new_order)
        db.session.commit()
        return jsonify(new_order.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@app.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    order = Orders.query.get(order_id)
    if order:
        return jsonify(order.to_dict())
    return jsonify({'error': 'Order not found'}), 404


@app.route('/orders/<order_id>', methods=['PUT'])
def update_order(order_id):
    order = Orders.query.get(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    data = request.get_json()
    try:
        for key, value in data.items():
            setattr(order, key, value)
        db.session.commit()
        return jsonify(order.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@app.route('/orders/<order_id>', methods=['DELETE'])
def delete_order(order_id):
    order = Orders.query.get(order_id)
    if order:
        db.session.delete(order)
        db.session.commit()
        return jsonify({'message': 'Order deleted'})
    return jsonify({'error': 'Order not found'}), 404


# Order Items
@app.route('/order-items', methods=['GET'])
def get_order_items():
    order_items = OrderItems.query.all()
    order_items_list = [item.to_dict() for item in order_items]
    return jsonify(order_items_list)


@app.route('/order-items', methods=['POST'])
def create_order_item():
    data = request.get_json()
    try:
        # Check if order and t-shirt exist
        order = Orders.query.get(data['orderId'])
        tshirt = TShirts.query.get(data['tshirtId'])
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        if not tshirt:
            return jsonify({'error': 'T-Shirt not found'}), 404

        new_item = OrderItems(**data)
        db.session.add(new_item)
        db.session.commit()
        return jsonify(new_item.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@app.route('/order-items/<item_id>', methods=['GET'])
def get_order_item(item_id):
    item = OrderItems.query.get(item_id)
    if item:
        return jsonify(item.to_dict())
    return jsonify({'error': 'Order Item not found'}), 404


@app.route('/order-items/<item_id>', methods=['PUT'])
def update_order_item(item_id):
    item = OrderItems.query.get(item_id)
    if not item:
        return jsonify({'error': 'Order Item not found'}), 404

    data = request.get_json()
    try:
        for key, value in data.items():
            setattr(item, key, value)
        db.session.commit()
        return jsonify(item.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@app.route('/order-items/<item_id>', methods=['DELETE'])
def delete_order_item(item_id):
    item = OrderItems.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': 'Order Item deleted'})
    return jsonify({'error': 'Order Item not found'}), 404
