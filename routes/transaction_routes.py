from flask import Blueprint, request, jsonify
from api import NessieClient, NessieAPIError

transaction_bp = Blueprint("transaction", __name__, url_prefix="/api/nessie")

nessie = NessieClient()

@transaction_bp.get("/accounts/<account_id>/transfers")
def get_account_transfers(account_id: str):
    try:
        transfers = nessie.get_account_transfers(account_id)
        return jsonify(transfers), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@transaction_bp.get("/transfers/<transfer_id>")
def get_transfer(transfer_id: str):
    try:
        transfer = nessie.get_transfer(transfer_id)
        return jsonify(transfer), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@transaction_bp.post("/accounts/<account_id>/transfers")
def create_transfer(account_id: str):
    data = request.get_json(force=True)
    medium = data.get("medium")
    payee_id = data.get("payee_id")
    amount = data.get("amount")
    transaction_date = data.get("transaction_date")
    description = data.get("description")

    if not all([medium, payee_id, amount, transaction_date]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        transfer = nessie.create_transfer(
            account_id=account_id,
            medium=medium,
            payee_id=payee_id,
            amount=amount,
            transaction_date=transaction_date,
            description=description
        )
        return jsonify(transfer), 201
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@transaction_bp.put("/transfers/<transfer_id>")
def update_transfer(transfer_id: str):
    data = request.get_json(force=True)
    try:
        updated = nessie.update_transfer(transfer_id, data)
        return jsonify(updated), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@transaction_bp.delete("/transfers/<transfer_id>")
def delete_transfer(transfer_id: str):
    try:
        nessie.delete_transfer(transfer_id)
        return jsonify({"message": "Transfer deleted successfully"}), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@transaction_bp.get("/accounts/<account_id>/bills")
def get_account_bills(account_id: str):
    try:
        bills = nessie.get_account_bills(account_id)
        return jsonify(bills), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@transaction_bp.get("/bills/<bill_id>")
def get_bill(bill_id: str):
    try:
        bill = nessie.get_bill(bill_id)
        return jsonify(bill), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@transaction_bp.post("/accounts/<account_id>/bills")
def create_bill(account_id: str):
    data = request.get_json(force=True)
    status = data.get("status")
    payee = data.get("payee")
    nickname = data.get("nickname")
    payment_date = data.get("payment_date")
    recurring_date = data.get("recurring_date")
    payment_amount = data.get("payment_amount")

    if not all([status, payee, nickname, payment_date]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        bill = nessie.create_bill(
            account_id=account_id,
            status=status,
            payee=payee,
            nickname=nickname,
            payment_date=payment_date,
            recurring_date=recurring_date,
            payment_amount=payment_amount
        )
        return jsonify(bill), 201
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@transaction_bp.put("/bills/<bill_id>")
def update_bill(bill_id: str):
    data = request.get_json(force=True)
    try:
        updated = nessie.update_bill(bill_id, data)
        return jsonify(updated), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@transaction_bp.delete("/bills/<bill_id>")
def delete_bill(bill_id: str):
    try:
        nessie.delete_bill(bill_id)
        return jsonify({"message": "Bill deleted successfully"}), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@transaction_bp.get("/accounts/<account_id>/deposits")
def get_account_deposits(account_id: str):
    try:
        deposits = nessie.get_account_deposits(account_id)
        return jsonify(deposits), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@transaction_bp.get("/deposits/<deposit_id>")
def get_deposit(deposit_id: str):
    try:
        deposit = nessie.get_deposit(deposit_id)
        return jsonify(deposit), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@transaction_bp.post("/accounts/<account_id>/deposits")
def create_deposit(account_id: str):
    data = request.get_json(force=True)
    medium = data.get("medium")
    amount = data.get("amount")
    transaction_date = data.get("transaction_date")
    description = data.get("description")

    if not all([medium, amount, transaction_date]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        deposit = nessie.create_deposit(
            account_id=account_id,
            medium=medium,
            amount=amount,
            transaction_date=transaction_date,
            description=description
        )
        return jsonify(deposit), 201
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@transaction_bp.put("/deposits/<deposit_id>")
def update_deposit(deposit_id: str):
    data = request.get_json(force=True)
    try:
        updated = nessie.update_deposit(deposit_id, data)
        return jsonify(updated), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@transaction_bp.delete("/deposits/<deposit_id>")
def delete_deposit(deposit_id: str):
    try:
        nessie.delete_deposit(deposit_id)
        return jsonify({"message": "Deposit deleted successfully"}), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@transaction_bp.get("/accounts/<account_id>/withdrawals")
def get_account_withdrawals(account_id: str):
    try:
        withdrawals = nessie.get_account_withdrawals(account_id)
        return jsonify(withdrawals), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@transaction_bp.get("/withdrawals/<withdrawal_id>")
def get_withdrawal(withdrawal_id: str):
    try:
        withdrawal = nessie.get_withdrawal(withdrawal_id)
        return jsonify(withdrawal), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@transaction_bp.post("/accounts/<account_id>/withdrawals")
def create_withdrawal(account_id: str):
    data = request.get_json(force=True)
    medium = data.get("medium")
    amount = data.get("amount")
    transaction_date = data.get("transaction_date")
    description = data.get("description")

    if not all([medium, amount, transaction_date]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        withdrawal = nessie.create_withdrawal(
            account_id=account_id,
            medium=medium,
            amount=amount,
            transaction_date=transaction_date,
            description=description
        )
        return jsonify(withdrawal), 201
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@transaction_bp.put("/withdrawals/<withdrawal_id>")
def update_withdrawal(withdrawal_id: str):
    data = request.get_json(force=True)
    try:
        updated = nessie.update_withdrawal(withdrawal_id, data)
        return jsonify(updated), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@transaction_bp.delete("/withdrawals/<withdrawal_id>")
def delete_withdrawal(withdrawal_id: str):
    try:
        nessie.delete_withdrawal(withdrawal_id)
        return jsonify({"message": "Withdrawal deleted successfully"}), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code
