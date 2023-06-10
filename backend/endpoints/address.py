
from flask import make_response,Blueprint
import uuid
from main import app, db
from models import *
from datetime import datetime
from helper import *



address_bp = Blueprint('address', __name__)





@address_bp.route("/getUserAddresses",methods=["GET"])
@login_required
def getUserAddresses():
    user = checkUser()
    addrArr=[]
    addresses = Addresses.query.filter_by(userId=user.userId).all()
    if addresses:
        for addr in addresses:
            addrArr.append(addr.toDict())
        return  jsonify({"message": "success","addresses":addrArr}), 200
    return jsonify({"error": "Address not found"}), 404


@address_bp.route("/createUserAddress",methods=["POST"])
@login_required
def createUserAddress():
    user = checkUser()
    data = request.get_json()
    required_fields = ['address1', 'city','state','zipcode']
    if not all(field in data for field in required_fields):
        return  make_response(jsonify({'error': 'Required fields are missing'}), 400)

    address1 = data.get("address1")
    address2 = data.get("address2")
    city = data.get("city")
    state= data.get("state")
    zipcode= data.get("zipcode")
    check_address=Addresses.query.filter_by(userId=user.userId,address1=address1,address2=address2, city = city ,state=state,  zipcode=  zipcode).all()
    if check_address:
        return jsonify({"error": "Address already exits"}), 409
    
    new_address = Addresses(
        addressId=uuid.uuid4(),
        userId=user.userId,
        address1=address1,
        address2=address2,
        city=city,
        state=state,
        zipcode=zipcode
    )
    db.session.add(new_address)
    db.session.commit()

    return jsonify({"message": "Address created successfully"}), 201

@address_bp.route("/updateUserAddress/<string:addressId>",methods=["PUT"])
@login_required
def updateUserAddress(addressId):
    user = checkUser()
    data = request.get_json()
    required_fields = ['address1', 'city','state','zipcode']
    if not all(field in data for field in required_fields):
        return  make_response(jsonify({'error': 'Required fields are missing'}), 400)
    
    address1 = data.get("address1")
    address2 = data.get("address2")
    city = data.get("city")
    state= data.get("state")
    zipcode= data.get("zipcode")
    check_address=Addresses.query.filter_by(userId=user.userId,address1=address1,address2=address2, city = city ,state=state,  zipcode=  zipcode).all()
    if check_address:
        return jsonify({"error": "Address already exits"}), 409
    
    address=Addresses.query.filter_by(userId=user.userId,addressId=addressId).first()
    if address is None:
        return jsonify({"error": "Address does not exists"}), 404
    
    address.address1 = data.get("address1")
    address.address2 = data.get("address2")
    address.city = data.get("city")
    address.state= data.get("state")
    address.zipcode= data.get("zipcode")
    address.date=datetime.now()
    db.session.commit()

    return jsonify({"message": "Address updated successfully","address":address.toDict()}), 200


@address_bp.route("/deleteUserAddress/<string:addressId>",methods=["DELETE"])
@login_required
def deleteUserAddress(addressId):
    user = checkUser()
    
    address=Addresses.query.filter_by(userId=user.userId,addressId=addressId).first()
    if address is None:
        return jsonify({"error": "Address does not exists"}), 404
    
    db.session.delete(address)
    db.session.commit()

    return jsonify({"message": "Address deleted successfully"}), 204


