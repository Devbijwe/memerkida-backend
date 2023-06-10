
from flask import make_response,Blueprint
import uuid
from flask_bcrypt import Bcrypt
from main import app, db
from models import *
from datetime import datetime
from helper import *

tshirt_bp = Blueprint('tshirt', __name__)

# Create a new T-shirt
@tshirt_bp.route('/createTshirt', methods=['POST'])
# @admin_required
def create_tshirt():
    data = request.json
    required_fields = ['tshirtId', 'name', 'template_image', 'tshirt_image', 'price', 'color','size','stock_quantity', 'category']
    if not all(field in data for field in required_fields):
        return make_response(jsonify({'error': 'Required fields are missing'}), 400)
    tshirtId=uuid.uuid4()
    new_tshirt = TShirts(
        tshirtId=tshirtId,
        name=data['name'],
        description=data.get('description'),
        template_image=data['template_image'],
        tshirt_image=data['tshirt_image'],
        price=data['price'],
        brand=data.get('brand'),
        color=data.get('color'),
        size=data.get('size'),
        gender=data.get('gender'),
        stock_quantity=data['stock_quantity'],
        is_featured=data.get('is_featured', False),
        category=data['category'],
        keywords=data.get('keywords'),
        date=datetime.utcnow()
    )
    db.session.add(new_tshirt)
    db.session.commit()
    return make_response(jsonify({'message': 'T-shirt created successfully',"tshirtId": tshirtId}), 201)


# Get all T-shirts
@tshirt_bp.route('/getTshirtDetails', methods=['GET'])
# @admin_required
def get_all_tshirts():
    tshirts = TShirts.query.all()
    result = []
    for tshirt in tshirts:
        result.append(tshirt.toDict())
    return make_response(jsonify(result), 200)

# Get a specific T-shirt
@tshirt_bp.route('/getTshirtDetails/<string:tshirt_id>', methods=['GET'])
def get_tshirt(tshirt_id):
    tshirt = TShirts.query.get(tshirt_id)
    if not tshirt:
        return make_response(jsonify({'error': 'T-shirt not found'}), 404)
    return make_response(jsonify(tshirt.toDict()), 200)

# Update a specific T-shirt
@tshirt_bp.route('/Updateshirt/<string:tshirt_id>', methods=['PUT'])
# @admin_required
def update_tshirt(tshirt_id):
    tshirt = TShirts.query.get(tshirt_id)
    if not tshirt:
        return make_response(jsonify({'error': 'T-shirt not found'}), 404)
    data = request.json
    required_fields = ['tshirtId', 'name', 'template_image', 'tshirt_image', 'price', 'color','size','stock_quantity', 'category']
    if not all(field in data for field in required_fields):
        return make_response(jsonify({'error': 'Required fields are missing'}), 400)
    
    tshirt.name = data.get('name', tshirt.name)
    tshirt.description = data.get('description', tshirt.description)
    tshirt.template_image = data.get('template_image', tshirt.template_image)
    tshirt.tshirt_image = data.get('tshirt_image', tshirt.tshirt_image)
    tshirt.price = data.get('price', tshirt.price)
    tshirt.brand = data.get('brand', tshirt.brand)
    tshirt.color = data.get('color', tshirt.color)
    tshirt.size = data.get('size', tshirt.size)
    tshirt.gender = data.get('gender', tshirt.gender)
    tshirt.stock_quantity = data.get('stock_quantity', tshirt.stock_quantity)
    tshirt.is_featured = data.get('is_featured', tshirt.is_featured)
    tshirt.category = data.get('category', tshirt.category)
    tshirt.keywords = data.get('keywords', tshirt.keywords)
    db.session.commit()
    return make_response(jsonify({'message': 'T-shirt updated successfully',"updatedTshirt":tshirt.toDict()}), 200)


# Delete a specific T-shirt
@tshirt_bp.route('/deleteTshirts/<string:tshirt_id>', methods=['DELETE'])
# @admin_required
def delete_tshirt(tshirt_id):
    tshirt = TShirts.query.get(tshirt_id)
    if not tshirt:
        return make_response(jsonify({'error': 'T-shirt not found'}), 404)
    db.session.delete(tshirt)
    db.session.commit()
    return make_response(jsonify({'message': 'T-shirt deleted successfully'}), 204)

