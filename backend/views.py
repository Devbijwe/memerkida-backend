

import os
import json
import uuid
from flask import Flask,Blueprint,render_template,session,redirect,send_file, request,flash,jsonify,Response,url_for,make_response,abort
from datetime import datetime
from main import app, db
from models import *
from datetime import datetime
from functools import wraps
from sqlalchemy import or_,func
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity



import Endpoints.Orders
from helper import *
from Endpoints.auth import auth_bp
from Endpoints.address import address_bp
from Endpoints.user import user_bp
from Endpoints.tshirt import tshirt_bp
from Endpoints.Admin import admin_bp
from Endpoints.cart import cart_bp

app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(address_bp, url_prefix='/api/address')
app.register_blueprint(user_bp, url_prefix='/api/user')
app.register_blueprint(tshirt_bp, url_prefix='/api/tshirts')
app.register_blueprint(cart_bp, url_prefix='/api/carts')

with open("config.json","r") as c:
    params=json.load(c)['params']
    


@app.route('/api/files/<fileId>', methods=['GET'])
def get_file(fileId):
    file_entry = Files.query.get(fileId)

    if file_entry is None:
        return jsonify({"error": "File could not be found"}), 400
        # abort(404)

    try:
        return send_file(file_entry.filepath, mimetype=file_entry.fileType, as_attachment=False)
    except Exception as e:
        abort(500)

# from MLModels.imgPrediction import predict_image
@app.route("/",methods=["GET","POST"])
# @login_required
def home():
    Arr=[]
    tshirts=TShirts.query.all()
    for tshirt in tshirts:
        Arr.append(tshirt.toDict())
        
    return  jsonify({"message": "You have successfully access this endpoint","tshirts":Arr}), 200

# from MLModels.imgPrediction import predict_image
@app.route("/api/get/data/category")
# @login_required
def getCat():
    cat=TShirts.get_unique_categories()
    return  jsonify({"message": "You have successfully access this endpoint","category":cat}), 200

@app.route("/api/get/data/tshirts")
# @login_required
# @ip_rate_limit(limit=10, per=timedelta(days=1))
def get_tshirts():
    gender = request.args.get('gender')
    category = request.args.get('category')

    if gender is None and category is None:
        # Query all t-shirts limited to 24 items
        tshirts = TShirts.query.limit(24).all()
    else:
        # Query t-shirts based on the provided gender or category (case-insensitive)
        tshirts = TShirts.query.filter(
            or_(func.lower(TShirts.gender) == func.lower(gender), func.lower(TShirts.category) == func.lower(category))
        ).all()

    # Convert t-shirts to dictionary representation
    tshirts_dict = [tshirt.toDict() for tshirt in tshirts]

    return jsonify(tshirts_dict)





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

                                        

