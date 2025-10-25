from flask import Blueprint, request, jsonify
from api import NessieClient, NessieAPIError
from models import db
from models.user import User
from models.nessie_account import NessieAccount

customer_bp = Blueprint("customer", __name__, url_prefix="/api/nessie/customers")

nessie = NessieClient()

@customer_bp.get("")
def get_all_customers():
    try:
        customers = nessie.get_customers()
        return jsonify(customers), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@customer_bp.get("/<customer_id>")
def get_customer(customer_id: str):
    try:
        customer = nessie.get_customer(customer_id)
        return jsonify(customer), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@customer_bp.post("")
def create_customer():
    data = request.get_json(force=True)
    user_id = data.get("idUser")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    address = data.get("address")

    if not all([user_id, first_name, last_name, address]):
        return jsonify({"error": "Missing required fields"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        customer = nessie.create_customer(first_name, last_name, address)

        nessie_account = NessieAccount(
            idUser=user_id,
            nessie_customer_id=customer.get("objectCreated", {}).get("_id")
        )
        db.session.add(nessie_account)
        db.session.commit()

        return jsonify({
            "message": "Customer created successfully",
            "customer": customer
        }), 201
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@customer_bp.put("/<customer_id>")
def update_customer(customer_id: str):
    data = request.get_json(force=True)

    try:
        updated = nessie.update_customer(customer_id, data)
        return jsonify(updated), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@customer_bp.delete("/<customer_id>")
def delete_customer(customer_id: str):
    try:
        nessie.delete_customer(customer_id)

        nessie_account = NessieAccount.query.filter_by(nessie_customer_id=customer_id).first()
        if nessie_account:
            db.session.delete(nessie_account)
            db.session.commit()

        return jsonify({"message": "Customer deleted successfully"}), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code
