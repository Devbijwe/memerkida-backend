

import os
import json
import uuid
from flask import Flask,Blueprint,render_template,session,redirect,send_file, request,flash,jsonify,Response,url_for,make_response
from datetime import datetime
from main import app, db
from models import *
from datetime import datetime
from functools import wraps


from helper import *
from endpoints.auth import auth_bp
from endpoints.address import address_bp
from endpoints.user import user_bp
from endpoints.tshirt import tshirt_bp
from endpoints.Admin import admin_bp

app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(address_bp, url_prefix='/api/address')
app.register_blueprint(user_bp, url_prefix='/api/user')
app.register_blueprint(tshirt_bp, url_prefix='/api/tshirt')


with open("config.json","r") as c:
    params=json.load(c)['params']
    
from MLModels.relatedTShirts import get_related_tshirts
# from MLModels.imgPrediction import predict_image
@app.route("/",methods=["GET","POST"])
# @login_required
def home():
    return  jsonify({"message": "You have successfully access this endpoint"}), 200


# @app.route("/get_related_tshirts/<string:tshirtId>",methods=["GET","POST"])
# def get_t_rel(tshirtId):# Example usage:
#     target_tshirt_id = tshirtId
#     top_n=10
#     related_tshirts = get_related_tshirts(target_tshirt_id,top_n)
#     for tshirt_id, score in related_tshirts:
        
#         print(f"T-Shirt ID: {tshirt_id}, Similarity Score: {score}")
#     return jsonify({}),200



@app.route("/get_related_tshirts/<string:tshirtId>", methods=["GET", "POST"])
def get_related_tshirts_route(tshirtId):
    target_tshirt_id = tshirtId
    top_n = 10
    related_tshirts = get_related_tshirts(target_tshirt_id, top_n)

    # Retrieve the related T-shirts from the database using the IDs
    with app.app_context():
        tshirts = TShirts.query.filter(TShirts.tshirtId.in_([tshirt_id for tshirt_id, _ in related_tshirts])).all()

    # Convert T-shirts to dictionary format with similarity score
    related_tshirts_data = []
    for tshirt, (_, score) in zip(tshirts, related_tshirts):
        tshirt_data = tshirt.toDict()
        tshirt_data['similarity_score'] = score
        related_tshirts_data.append(tshirt_data)

    return jsonify({"related_tshirts": related_tshirts_data}), 200

@app.route('/addAllTshirt', methods=['POST'])
def add_all_tshirt():
    # Read data from the JSON file
    with open('data.json') as json_file:
        tshirt_data = json.load(json_file)
    
    for tshirt in tshirt_data:
        required_fields = ['tshirtId', 'name', 'template_image', 'tshirt_image', 'price', 'color','size','stock_quantity', 'category']
        if not all(field in tshirt for field in required_fields):
            return make_response(jsonify({'error': 'Required fields are missing'}), 400)

        tshirtId = uuid.uuid4()
        existing_tshirt = TShirts.query.get(tshirtId)
        if existing_tshirt:
            return make_response(jsonify({'error': f'T-shirt with ID {tshirtId} already exists'}), 409)

        new_tshirt = TShirts(
            tshirtId=tshirtId,
            name=tshirt['name'],
            description=tshirt.get('description'),
            template_image=tshirt['template_image'],
            tshirt_image=tshirt['tshirt_image'],
            price=tshirt['price'],
            brand=tshirt.get('brand'),
            color=tshirt.get('color'),
            size=tshirt.get('size'),
            gender=tshirt.get('gender'),
            stock_quantity=tshirt['stock_quantity'],
            is_featured=tshirt.get('is_featured', False),
            category=tshirt['category'],
            keywords=tshirt.get('keywords'),
            date=datetime.utcnow()
        )
        db.session.add(new_tshirt)
    
    db.session.commit()
    return make_response(jsonify({'message': 'T-shirts created successfully'}), 201)

    


@app.context_processor
def inject_user():
    pass
    # try:
    #     user = checkUser()
    #     user = Users.query.get(user.userId)
    #     # Uncomment the following line if you want to attach the user object to the request context
    #     # request.user = cust
    #     return {"user": user,"params":params}  # Inject the user object into the template context
    # except (AuthenticationRequired, InvalidUserEmail, TokenExpired, InvalidToken) as e:
    #     print(f"Authentication error: {e}")
    #     return {"params":params}

                                        

