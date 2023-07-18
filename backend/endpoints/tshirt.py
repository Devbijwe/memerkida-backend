
from flask import make_response,Blueprint
import uuid

from main import app, db
from models import TShirts
from datetime import datetime
from helper import *
from MLModels.relatedTShirts import get_related_tshirts
from MLModels.searchTshirts import search_products
tshirt_bp = Blueprint('tshirt', __name__)



@tshirt_bp.route('/getTshirts', methods=['GET'])
def get_all_tshirts():
    search_term = request.args.get('search', '')
    top_results = int(request.args.get('top', 12))
    max_price = float(request.args.get('max_price', -1))  # -1 to indicate no maximum price
    min_price = float(request.args.get('min_price', -1))  # -1 to indicate no minimum price
    category = request.args.get('category', None)  # None to indicate no category provided
    # print(category)
    search_results = search_products(search_term, top_results, max_price, min_price, category)
    
    results = []
    for product in search_results:
        results.append(
            product.toDict()
        )
    # print(results)
    return make_response(jsonify(results), 200)

    


# Get a specific T-shirt
@tshirt_bp.route('/getTshirts/<string:tshirt_id>', methods=['GET'])
def get_tshirt(tshirt_id):
    tshirt = TShirts.query.get(tshirt_id)
    if not tshirt:
        return make_response(jsonify({'error': 'T-shirt not found'}), 404)
    return make_response(jsonify(tshirt.toDict()), 200)


@tshirt_bp.route("/get_related_tshirts/<string:tshirtId>", methods=["GET", "POST"])
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

    total_results = len(related_tshirts_data)

    return jsonify({"related_tshirts": related_tshirts_data, "total_results": total_results}), 200



# @tshirt_bp.route("/get_related_tshirts/<string:tshirtId>", methods=["GET", "POST"])
# def get_related_tshirts_route(tshirtId):
#     target_tshirt_id = tshirtId
#     top_n = 10
#     related_tshirts = get_related_tshirts(target_tshirt_id, top_n)

#     # Retrieve the related T-shirts from the database using the IDs
#     with app.app_context():
#         tshirts = TShirts.query.filter(TShirts.tshirtId.in_([tshirt_id for tshirt_id, _ in related_tshirts])).all()

#     # Convert T-shirts to dictionary format with similarity score
#     related_tshirts_data = []
#     for tshirt, (_, score) in zip(tshirts, related_tshirts):
#         tshirt_data = tshirt.toDict()
#         tshirt_data['similarity_score'] = score
#         related_tshirts_data.append(tshirt_data)

#     return jsonify({"related_tshirts": related_tshirts_data}), 200
