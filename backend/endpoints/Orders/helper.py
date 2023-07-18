from flask import make_response,Blueprint,request
import uuid
from main import app, db
from models import *
from datetime import datetime,timedelta
from helper import login_required,user_rate_limit,utc_to_ist,add_data_to_csv


def get_order_data_for_csv(orderId):
    with app.app_context():
        order = Orders.get_by_id(orderId)
        if order is None:
            return None
        orderId = order.orderId
        userId = order.userId
        addressId = order.addressId
        
         # Format the IST order_date as a string
        order_date = utc_to_ist( order.order_date)

        # order_date = order.order_date
        total_amount = order.total_amount
        
        order_item = OrderItems.get_by_id(order.itemId)
        if order_item is None:
            return None
        
        tshirtId = order_item.tshirtId
        quantity = order_item.quantity
        color = order_item.color
        size = order_item.size

        address = Addresses.get_by_id(addressId)
        if address is None:
            return None

        full_address = address.get_full_address()

        user = Users.get_by_id(userId)
        if user is None:
            return None

        name = user.name
        mobile = user.mobile

        order_data = {
            'srNo': 0,  # Placeholder value, will be updated later
            'orderId': orderId,
            'userId': userId,
            'name': name,
            'mobile': mobile,
            'full_address': full_address,
            'tshirtId': tshirtId,
            'quantity': quantity,
            'color': color,
            'size': size,
            'total_amount': total_amount,
            'order_date': order_date,
        }

        return order_data




def create_single_order(item_data, user, order_ids):
    # Check if address exists
    address = Addresses.query.get(item_data.get("addressId"))
    if not address:
        raise Exception('Address not found')

    # Generate new UUID for the order
    order_id = str(uuid.uuid4())

    # Create order
    order = Orders()
    order.userId = user.userId
    order.addressId = address.addressId
    order.total_amount = 0  # Set initial total amount
    order.orderId = order_id

    # Check if all required fields are present
    required_fields = ['tshirtId', 'color', 'size', 'quantity']
    missing_fields = [field for field in required_fields if field not in item_data]
    if missing_fields:
        raise Exception(f'Required fields are missing: {", ".join(missing_fields)}')

    for field in required_fields:
        setattr(order, field, item_data[field])

    # Create order item
    order_item = OrderItems()

    for field in required_fields:
        setattr(order_item, field, item_data[field])

    itemId = str(uuid.uuid4())
    order_item.itemId = itemId
    order.itemId=itemId
 
    # Retrieve the T-Shirt for price validation
    tshirt = TShirts.query.get(order_item.tshirtId)
    if not tshirt:
        raise Exception('T-Shirt not found')
    
    # Check if color and size are within the available options
    color = item_data['color']
    size = item_data['size']
    if color not in tshirt.color:
        raise Exception('Invalid color')
    if size not in tshirt.size:
        raise Exception('Invalid size')


    # Check if quantity and price fields have valid values
    if order_item.quantity is None:
        raise Exception('Quantity is not specified')

    if tshirt.price is None:
        raise Exception('T-Shirt price is not available')

    # Update total amount based on order item price and quantity
    order_item_price = tshirt.price
    order_item_total = order_item_price * order_item.quantity
    order.total_amount += order_item_total
    
    
    # Save order and order item
    db.session.add(order)
    db.session.add(order_item)
    db.session.commit()

    order_ids.append(order.orderId)  # Append orderId to the list

     # Add order data to CSV
    filepath = 'data/csv/order.csv'
    order_data = get_order_data_for_csv(order.orderId)
    try:
        add_data_to_csv(order_data, filepath)
    except Exception as e:
        raise Exception(f'Failed to add order data to CSV: {str(e)}')
    