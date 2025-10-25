from flask import Blueprint, request, jsonify
from api import NessieClient, NessieAPIError

branch_bp = Blueprint("branch", __name__, url_prefix="/api/nessie/branches")

nessie = NessieClient()

@branch_bp.get("")
def get_all_branches():
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)
    radius = request.args.get("radius", type=float)

    try:
        branches = nessie.get_branches(lat=lat, lng=lng, radius=radius)
        return jsonify(branches), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@branch_bp.get("/<branch_id>")
def get_branch(branch_id: str):
    try:
        branch = nessie.get_branch(branch_id)
        return jsonify(branch), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code
