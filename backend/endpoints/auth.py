
from flask import make_response,Blueprint
import uuid
from flask_bcrypt import Bcrypt
from main import app, db
from models import *
from datetime import datetime
import jwt
from sqlalchemy import or_
from helper import *

bcrypt = Bcrypt(app)

auth_bp = Blueprint('auth', __name__)

from google.oauth2 import id_token
from google.auth.transport import requests

@auth_bp.route('/validateToken', methods=['POST'])
def validate_token():
    token = request.headers.get("Authorization")

    if not token:
        return jsonify({"error": "Token is missing"}), 401

    try:
        decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        user_id = decoded_token['user_id']
        user = Users.query.filter_by(userId=user_id).first()

        if not user:
            return jsonify({"error": "Invalid token"}), 401

        return jsonify({"message": "Token is valid", "user_id": user.userId}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 401

    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    required_fields = ['password']
    email = data.get("email")
    mobile = data.get("mobile")
    google_token = data.get("google_token")  # Token received from Google login
    
    if email and mobile:
        return jsonify({"error": "Provide either email or mobile"}), 400
    
    
    if mobile:
        required_fields.append('mobile')
        user = Users.query.filter_by(mobile=mobile).first()
    elif email:
        required_fields.append('email')
        user = Users.query.filter_by(email=email).first()
        
    elif google_token:
        try:
            idinfo = id_token.verify_oauth2_token(google_token, requests.Request(), app.config['GOOGLE_CLIENT_ID'])
            email = idinfo['email']
            user = Users.query.filter_by(email=email).first()
        except ValueError:
            return jsonify({"error": "Invalid Google token"}), 401
    else:
        return jsonify({"error": "Required fields are missing"}), 400
    
    if not user:
        return jsonify({"error": "Invalid user credentials"}), 401
    
    password = data.get("password")
    
    if bcrypt.check_password_hash(user.password, password):
        token = generate_jwt_token(user)
        return jsonify({"message": "Logged in successfully", "token": token}), 200
    else:
        return jsonify({"error": "Invalid user credentials"}), 401

@auth_bp.route('/createUser', methods=['POST'])
def signup():
    data = request.get_json()
    required_fields = ['name', 'password']
    name = data.get("name")
    password = data.get("password")
    email = data.get("email")
    mobile = data.get("mobile")
    google_token = data.get("google_token")  # Token received from Google login
    
    if not all(field in data for field in required_fields):
        return make_response(jsonify({'error': 'Required fields are missing'}), 400)

    if not (email or mobile):
        return jsonify({"error": "Provide either email or mobile"}), 400

    if google_token:
        try:
            idinfo = id_token.verify_oauth2_token(google_token, requests.Request(), app.config['GOOGLE_CLIENT_ID'])
            email = idinfo['email']
        except ValueError:
            return jsonify({"error": "Invalid Google token"}), 401

    # Check if email or mobile already exists
    if email and mobile:
        user = Users.query.filter(or_(Users.email == email, Users.mobile == mobile)).first()
        existing_fields =['user'] #['email', 'mobile']
    elif mobile:
        user = Users.query.filter_by(mobile=mobile).first()
        existing_fields = ['user'] #['mobile']
    elif email:
        user = Users.query.filter_by(email=email).first()
        existing_fields = ['user'] #['email']
    else:
        return jsonify({"error": "Required fields are missing"}), 400

    if user:
        existing_fields_str = ", ".join(existing_fields)
        return jsonify({"error": f"{existing_fields_str.capitalize()} already exists"}), 409

    # Hash the password
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    # Create new user
    new_user = Users(
        userId=uuid.uuid4(),
        name=name,
        email=email,
        mobile=mobile,
        password=hashed_password
    )

    # Add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    # Generate JWT token for the new user
    token = generate_jwt_token(new_user)

    return jsonify({"message": "User created successfully", "token": token}), 201

@auth_bp.route('/logout')
@login_required
def logout():
    token = request.headers.get("Authorization")
    if  token:
        # revoke_token(token)
        session.pop('token', None)
        session.clear()
        return jsonify({"message": "Logged out successfully"}), 200

    return jsonify({"error": "Invalid token"}), 401
    
    
