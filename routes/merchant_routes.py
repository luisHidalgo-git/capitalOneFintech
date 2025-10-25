from flask import Blueprint, request, jsonify
from api import NessieClient, NessieAPIError

merchant_bp = Blueprint("merchant", __name__, url_prefix="/api/nessie/merchants")

nessie = NessieClient()

@merchant_bp.get("")
def get_all_merchants():
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)
    radius = request.args.get("radius", type=float)

    try:
        merchants = nessie.get_merchants(lat=lat, lng=lng, radius=radius)
        return jsonify(merchants), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@merchant_bp.get("/<merchant_id>")
def get_merchant(merchant_id: str):
    try:
        merchant = nessie.get_merchant(merchant_id)
        return jsonify(merchant), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@merchant_bp.post("")
def create_merchant():
    data = request.get_json(force=True)
    name = data.get("name")
    category = data.get("category")
    address = data.get("address")
    geocode = data.get("geocode")

    if not all([name, category, address]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        merchant = nessie.create_merchant(
            name=name,
            category=category,
            address=address,
            geocode=geocode
        )
        return jsonify(merchant), 201
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code
