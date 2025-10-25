from flask import Blueprint, request, jsonify
from api import NessieClient, NessieAPIError

purchase_bp = Blueprint("purchase", __name__, url_prefix="/api/nessie")

nessie = NessieClient()

@purchase_bp.get("/accounts/<account_id>/purchases")
def get_account_purchases(account_id: str):
    try:
        purchases = nessie.get_account_purchases(account_id)
        return jsonify(purchases), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@purchase_bp.get("/purchases/<purchase_id>")
def get_purchase(purchase_id: str):
    try:
        purchase = nessie.get_purchase(purchase_id)
        return jsonify(purchase), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@purchase_bp.post("/accounts/<account_id>/purchases")
def create_purchase(account_id: str):
    data = request.get_json(force=True)
    merchant_id = data.get("merchant_id")
    medium = data.get("medium")
    amount = data.get("amount")
    purchase_date = data.get("purchase_date")
    description = data.get("description")

    if not all([merchant_id, medium, amount, purchase_date]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        purchase = nessie.create_purchase(
            account_id=account_id,
            merchant_id=merchant_id,
            medium=medium,
            amount=amount,
            purchase_date=purchase_date,
            description=description
        )
        return jsonify(purchase), 201
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@purchase_bp.put("/purchases/<purchase_id>")
def update_purchase(purchase_id: str):
    data = request.get_json(force=True)
    try:
        updated = nessie.update_purchase(purchase_id, data)
        return jsonify(updated), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@purchase_bp.delete("/purchases/<purchase_id>")
def delete_purchase(purchase_id: str):
    try:
        nessie.delete_purchase(purchase_id)
        return jsonify({"message": "Purchase deleted successfully"}), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code
