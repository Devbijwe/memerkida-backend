import jwt
from flask import session,request,jsonify,make_response,g
from models import Users,Admin
from main import app,db
from functools import wraps,update_wrapper
from  datetime import datetime,timedelta
from functools import wraps
from flask import request, jsonify
import os,csv


blacklisted_tokens=set()
# Store request timestamps per user for rate limiting
user_request_timestamps = {}

def generate_jwt_token(user):
    payload = {
        'userId': user.userId,
        'exp': datetime.utcnow() + timedelta(days=100)  # Token expiration time
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token



# Add a token to the blacklist
def revoke_token(token):
    blacklisted_tokens.add(token)

# Check if a token is blacklisted
def is_token_revoked(token):
    print(blacklisted_tokens)
    return token in blacklisted_tokens

# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         token = request.headers.get("Authorization")
#         if not token:
#             return jsonify({"error": "Unauthorized"}), 401

#         if is_token_revoked(token):
#             return jsonify({"error": "Token revoked"}), 401

#         try:
#             payload = jwt.decode(token, app.secret_key, algorithms=["HS256"])
#             userId = payload["userId"]
#             user = Users.query.filter_by(userId=userId).first()

#             if not user:
#                 return jsonify({"error": "Unauthorized"}), 401

#             request.user = user

#         except jwt.ExpiredSignatureError:
#             return jsonify({"error": "Token expired"}), 401
#         except jwt.InvalidTokenError:
#             return jsonify({"error": "Invalid token"}), 401

#         return f(*args, **kwargs)

#     return decorated_function
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        authorization_header = request.headers.get("Authorization")
        if not authorization_header:
            return jsonify({"error": "Unauthorized"}), 401

        token = authorization_header.replace("Bearer ", "")
        if is_token_revoked(token):
            return jsonify({"error": "Token revoked"}), 401

        try:
            payload = jwt.decode(token, app.secret_key, algorithms=["HS256"])
            userId = payload["userId"]
            user = Users.query.filter_by(userId=userId).first()

            if not user:
                return jsonify({"error": "Unauthorized"}), 401

            request.user = user

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated_function

# Decorator for rate limiting per user
def user_rate_limit(limit, per):
    def decorator(f):
        request_counts = {}

        @wraps(f)
        def wrapper(*args, **kwargs):
            user = request.user

            # If user is not authenticated, allow the request without rate limiting
            if user is None:
                return f(*args, **kwargs)

            # Get the current timestamp
            now = datetime.now()

            # Get the timestamp of the last request from this user for this specific endpoint
            last_request_timestamp = user_request_timestamps.get(user.userId)

            # If there was a previous request, check if it's within the rate limit window
            if last_request_timestamp is not None and now - last_request_timestamp < per:
                request_count = request_counts.get(user.userId, 0) + 1
                request_counts[user.userId] = request_count

                # Check if the request count exceeds the limit
                if request_count > limit:
                    # Calculate the time remaining until the next allowed request
                    remaining_time = per - (now - last_request_timestamp)

                    # Return a 429 Too Many Requests error response with the remaining time
                    response = make_response(jsonify({'error': 'Too many requests', 'retry-after': str(int(remaining_time.total_seconds()))+" seconds"}), 429)
                    response.headers['Retry-After'] = str(int(remaining_time.total_seconds()))
                    return response

            # Update the timestamp and request count for this user's request
            user_request_timestamps[user.userId] = now
            request_counts[user.userId] = request_counts.get(user.userId, 0) + 1

            # Call the decorated function
            return f(*args, **kwargs)

        return update_wrapper(wrapper, f)

    return decorator


def ip_rate_limit(limit, per):
    def decorator(f):
        request_counts = {}

        @wraps(f)
        def wrapper(*args, **kwargs):
            ip = request.remote_addr
            print(id)
            # Get the current timestamp
            now = datetime.now()

            # Get the timestamp of the last request from this IP for this specific endpoint
            last_request_timestamp = user_request_timestamps.get(ip)

            # If there was a previous request, check if it's within the rate limit window
            if last_request_timestamp is not None and now - last_request_timestamp < per:
                request_count = request_counts.get(ip, 0) + 1
                request_counts[ip] = request_count

                # Check if the request count exceeds the limit
                if request_count > limit:
                    # Calculate the time remaining until the next allowed request
                    remaining_time = per - (now - last_request_timestamp)

                    # Return a 429 Too Many Requests error response with the remaining time
                    response = make_response(jsonify({'error': 'Too many requests', 'retry-after': str(int(remaining_time.total_seconds()))+" seconds"}), 429)
                    response.headers['Retry-After'] = str(int(remaining_time.total_seconds()))
                    return response

            # Update the timestamp and request count for this user's request
            user_request_timestamps[ip] = now
            request_counts[ip] = request_counts.get(ip, 0) + 1

            # Call the decorated function
            return f(*args, **kwargs)

        return update_wrapper(wrapper, f)
        return wrapper

    return decorator




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


def utc_to_ist(utc_date):
        ist_offset = timedelta(hours=5, minutes=30)
        ist_date = utc_date + ist_offset
        ist_date = ist_date.strftime('%Y-%m-%d %H:%M:%S')
        return ist_date
    

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
            raise InvalidUserEmail("Unauthorized")
        return user

    except jwt.ExpiredSignatureError:
        raise TokenExpired("Token expired")
    except jwt.InvalidTokenError:
        raise InvalidToken("Invalid token")


def process_list_field(field_value):
    if field_value:
        field_list = [item.strip() for item in field_value.split(',') if item.strip()]
        return field_list
    return []

def add_data_to_csv(data, filepath):
    if data is None:
        return
    # Check if the file exists, create it if necessary
    is_file_exist = os.path.isfile(filepath)

    # Get the current number of rows in the CSV file
    current_row_count = 0

    if is_file_exist:
        with open(filepath, 'r') as file:
            reader = csv.reader(file)
            # Subtract 1 from the row count to exclude the header row
            current_row_count = sum(1 for _ in reader) - 1

    # Increment the serial number for the order data
    data['srNo'] = current_row_count + 1

    # Append the order data to the CSV file
    with open(filepath, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())

        # Write header if the file is newly created
        if not is_file_exist:
            writer.writeheader()

        # Append the order data to the CSV file
        writer.writerow(data)
        return True
    return False
    