from flask import make_response, Blueprint, request, jsonify
import uuid

from main import app, db
from models import *


from helper import *


banner_bp = Blueprint('banner', __name__)

@banner_bp.route('/getBanners', methods=['GET'])
@admin_required
def get_banners():
    banners = Banners.query.all()
    banner_list = [banner.toDict() for banner in banners]
    return jsonify(banner_list),200


@banner_bp.route('/getBanner/<banner_id>', methods=['GET'])
@admin_required
def get_banner(banner_id):
    banner = Banners.query.get(banner_id)
    if not banner:
        return jsonify({'error': 'Banner not found'}), 404
    return jsonify(banner.toDict()),200

@banner_bp.route('/createBanner', methods=['POST'])
@admin_required
def create_banner():
    data = request.get_json()
    required_fields = [ 'link'] # ['title', 'description', 'image_url1', 'image_url2', 'link']
    if not all(field in data for field in required_fields):
        return make_response(jsonify({'error': 'Required fields are missing'}), 400)

    title = data.get("title")
    description = data.get("description")
    image_url1 = data.get("image_url1")
    image_url2 = data.get("image_url2")
    link = data.get("link")
    bannerId=str(uuid.uuid4())

    # Create new banner
    new_banner = Banners(
        bannerId=bannerId,
        title=title,
        description=description,
        image_url1=image_url1,
        image_url2=image_url2,
        link=link,
        date=datetime.utcnow()
    )

    # Add the new banner to the database
    db.session.add(new_banner)
    db.session.commit()

    return jsonify({"message": "Banner created successfully","bannerId":bannerId}), 201

@banner_bp.route('/updateBanner/<banner_id>', methods=['PUT'])
@admin_required
def update_banner(banner_id):
    banner = Banners.query.get(banner_id)
    if not banner:
        return jsonify({'error': 'Banner not found'}), 404
    data = request.get_json()
    for key, value in data.items():
        if key != 'bannerId':
            setattr(banner, key, value)
    banner.date=datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Banner updated successfully',"banner":banner.toDict()}),200

@banner_bp.route('/deleteBanner/<banner_id>', methods=['DELETE'])
@admin_required
def delete_banner(banner_id):
    banner = Banners.query.get(banner_id)
    if not banner:
        return jsonify({'error': 'Banner not found'}), 404
    db.session.delete(banner)
    db.session.commit()
    return jsonify({'message': 'Banner deleted successfully'}) ,204

