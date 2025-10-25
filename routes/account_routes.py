from flask import Blueprint, request, jsonify
from api import NessieClient, NessieAPIError
from models import db
from models.nessie_account import NessieAccount

account_bp = Blueprint("account", __name__, url_prefix="/api/nessie/accounts")

nessie = NessieClient()

@account_bp.get("")
def get_all_accounts():
    try:
        accounts = nessie.get_accounts()
        return jsonify(accounts), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@account_bp.get("/<account_id>")
def get_account(account_id: str):
    try:
        account = nessie.get_account(account_id)
        return jsonify(account), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@account_bp.post("")
def create_account():
    data = request.get_json(force=True)
    user_id = data.get("idUser")
    account_type = data.get("type")
    nickname = data.get("nickname")
    rewards = data.get("rewards", 0)
    balance = data.get("balance", 0)
    account_number = data.get("account_number")

    if not all([user_id, account_type, nickname]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        account = nessie.create_account(
            account_type=account_type,
            nickname=nickname,
            rewards=rewards,
            balance=balance,
            account_number=account_number
        )

        nessie_account = NessieAccount.query.filter_by(idUser=user_id).first()
        if nessie_account:
            nessie_account.nessie_account_id = account.get("objectCreated", {}).get("_id")
            nessie_account.account_type = account_type
            nessie_account.nickname = nickname
        else:
            nessie_account = NessieAccount(
                idUser=user_id,
                nessie_account_id=account.get("objectCreated", {}).get("_id"),
                account_type=account_type,
                nickname=nickname
            )
            db.session.add(nessie_account)

        db.session.commit()

        return jsonify({
            "message": "Account created successfully",
            "account": account
        }), 201
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@account_bp.put("/<account_id>")
def update_account(account_id: str):
    data = request.get_json(force=True)

    try:
        updated = nessie.update_account(account_id, data)
        return jsonify(updated), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@account_bp.delete("/<account_id>")
def delete_account(account_id: str):
    try:
        nessie.delete_account(account_id)

        nessie_account = NessieAccount.query.filter_by(nessie_account_id=account_id).first()
        if nessie_account:
            db.session.delete(nessie_account)
            db.session.commit()

        return jsonify({"message": "Account deleted successfully"}), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@account_bp.get("/<account_id>/customer")
def get_account_customer(account_id: str):
    try:
        customer = nessie.get_account_customer(account_id)
        return jsonify(customer), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code
