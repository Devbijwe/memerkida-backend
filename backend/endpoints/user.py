
from flask import make_response,Blueprint
import uuid
from flask_bcrypt import Bcrypt
from main import app, db
from models import *
from datetime import datetime
from helper import *

user_bp = Blueprint('user', __name__)

@user_bp.route("/getUserDetails",methods=["GET"])
@login_required
def getUserDetails():
    user = checkUser()
    user = Users.query.get(user.userId).toDictExceptPassword()
    return  jsonify({"message": "success","user":user}), 200
