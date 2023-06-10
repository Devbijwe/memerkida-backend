import jwt
from flask import session,request,jsonify,make_response,g
from models import Users,Admin
from main import app,db
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return make_response(jsonify({'error': 'Admin access denied'}), 401)
        try:
            # Verify and decode the JWT
            payload = jwt.decode(token, app.secret_key, algorithms=["HS256"])
            email = payload["email"]
            adminId = payload["adminId"]
            username=payload["username"]

            # Find the user by email
            admin = Admin.query.filter_by(adminId=adminId,email=email,username=username).first()

            
            if not admin:
                return make_response(jsonify({'error': 'Admin access denied'}), 401)

            # Attach the admin object to the request context
            request.admin = admin

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)
    return decorated_function




def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization")
        # token = session.get("token")
        if not token:
            # Save the current URL as the 'next' parameter in the login redirect URL
            return jsonify({"message": "Method not allowed"}), 405
            # login_url = url_for('login', redirect_url=request.url)
            # return redirect(login_url)
        try:
            # Verify and decode the JWT
            payload = jwt.decode(token, app.secret_key, algorithms=["HS256"])
            email = payload["email"]
            userId = payload["userId"]

            # Find the user by email
            user = Users.query.filter_by(userId=userId).first()

            # user = Users.query.filter_by(email=email).first()
            if not user:
                return jsonify({"error": "Invalid user email"}), 401

            # Attach the user object to the request context
            request.user = user

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated_function




class AuthenticationRequired(Exception):
    pass

class InvalidUserEmail(Exception):
    pass

class TokenExpired(Exception):
    pass

class InvalidToken(Exception):
    pass


def checkUser():
    token = session.get("token")
    if not token:
        raise AuthenticationRequired("Authentication required")

    try:
        # Verify and decode the JWT
        payload = jwt.decode(token, app.secret_key, algorithms=["HS256"])
        email = payload["email"]
        
        # Find the user by email
        user = Users.query.filter_by(email=email).first()
        if not user:
            raise InvalidUserEmail("Invalid user email")
        return user

    except jwt.ExpiredSignatureError:
        raise TokenExpired("Token expired")
    except jwt.InvalidTokenError:
        raise InvalidToken("Invalid token")
