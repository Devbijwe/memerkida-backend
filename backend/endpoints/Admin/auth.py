from flask import make_response, Blueprint, request, jsonify
import uuid
from flask_bcrypt import Bcrypt
from main import app, db
from models import *
from datetime import datetime,timedelta
import jwt
from helper import *
bcrypt = Bcrypt(app)

auth_bp = Blueprint('auth', __name__)
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    required_fields = ['email', 'password']
    if not all(field in data for field in required_fields):
        return make_response(jsonify({'error': 'Required fields are missing'}), 400)

    email = data.get("email")
    password = data.get("password")
    admin = Admin.query.filter_by(email=email).first()
    if not admin:
        return jsonify({"error": "Invalid admin email"}), 401

    if bcrypt.check_password_hash(admin.password, password):
        token = jwt.encode({"email": email,"username":admin.username ,"adminId": admin.adminId}, app.secret_key, algorithm="HS256")
        session["token"] = token
        return jsonify({"message": "Logged in successfully", "token": token}), 200
    else:
        return jsonify({"error": "Invalid password"}), 401

   
@auth_bp.route('/createAdmin', methods=['POST'])
def createAdmin():
    data = request.get_json()
    required_fields = ['username', 'password', 'email']
    if not all(field in data for field in required_fields):
        return make_response(jsonify({'error': 'Required fields are missing'}), 400)

    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    # Check if email already exists
    admin = Admin.query.filter_by(email=email).first()
    if admin:
        return jsonify({"error": "Email already exists"}), 409

    # Hash the password
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    # Create new admin
    new_admin = Admin(
        adminId=str(uuid.uuid4()),
        username=username,
        email=email,
        password=hashed_password,
        dateTime=datetime.utcnow()
    )

    # Add the new admin to the database
    db.session.add(new_admin)
    db.session.commit()

    return jsonify({"message": "Admin created successfully"}), 201

    

@auth_bp.route('/logout')
@admin_required
def logout():
    session.pop('token', None)
    session.clear()
    # Expire the token by setting an expiration time in the past
    expiration = datetime.utcnow() - timedelta(days=1)
    token = jwt.encode({"exp": expiration}, app.secret_key, algorithm="HS256")
    return jsonify({"message": "Admin Logged Out successfully", "expired_token": token}), 200