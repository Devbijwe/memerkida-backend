
from flask import make_response,Blueprint
import uuid
from flask_bcrypt import Bcrypt
from main import app, db
from models import *
from datetime import datetime
import jwt
from helper import *

bcrypt = Bcrypt(app)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        data = request.get_json()
        required_fields = ['email', 'password']
        if not all(field in data for field in required_fields):
            return  make_response(jsonify({'error': 'Required fields are missing'}), 400)
        
        email = data.get("email")
        password = data.get("password")
        user = Users.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "Invalid user email"}), 401

        if bcrypt.check_password_hash(user.password, password):
            token = jwt.encode({"email": email,"userId":user.userId}, app.secret_key, algorithm="HS256")
            session["token"] = token
            return jsonify({"message": "Logged in successfully", "token": token}), 200
        else:
            return jsonify({"error": "Invalid password"}), 401
    
    redirect_url = request.args.get('redirect_url') or "/"
    return jsonify({"message": "Method not allowed"}), 405

    return render_template("login2.html", auth_type="login",redirect_url=redirect_url)


@auth_bp.route('/createUser', methods=['GET','POST'])
def signup():
    if request.method=="POST":
        data = request.get_json()
        required_fields = ['name', 'password','email','mobile']
        if not all(field in data for field in required_fields):
            return  make_response(jsonify({'error': 'Required fields are missing'}), 400)

        name = data.get("name")
        password = data.get("password")
        email = data.get("email")
        mobile = data.get("mobile")
        
        

        # Check if email already exists
        user = Users.query.filter_by(email=email).first()
        if user:
            return jsonify({"error": "Email already exists"}), 409

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

        return jsonify({"message": "User created successfully"}), 201
    
    # elif request.method == 'GET':
    #     return jsonify({"message": "Method not allowed"}), 405
    #     return render_template("login2.html", auth_type="signup")

    return jsonify({"message": "Method not allowed"}), 405


        
    # return render_template("login2.html",auth_type="signup")


@auth_bp.route('/logout')
@login_required
def logout():
    session.pop('token', None)
    session.clear()
    return jsonify({"message": "User Logged Out successfully"}), 200
  
