
from flask import make_response,Blueprint
import uuid
from flask_bcrypt import Bcrypt
from main import app, db
from models import *
from datetime import datetime

from helper import *
from .auth import auth_bp
from .banners import banner_bp
from .tshirt import tshirt_bp
admin_bp = Blueprint('admin', __name__)

admin_bp.register_blueprint(auth_bp, url_prefix='/auth')
admin_bp.register_blueprint(banner_bp, url_prefix='/banner')

admin_bp.register_blueprint(tshirt_bp, url_prefix='/tshirt')
