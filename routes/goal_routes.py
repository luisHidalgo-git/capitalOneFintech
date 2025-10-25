from flask import Blueprint, request, jsonify
from api import NessieClient, NessieAPIError

goal_bp = Blueprint("goal", __name__, url_prefix="/api/nessie")

nessie = NessieClient()

@goal_bp.get("/accounts/<account_id>/goals")
def get_account_goals(account_id: str):
    try:
        goals = nessie.get_account_goals(account_id)
        return jsonify(goals), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@goal_bp.get("/goals/<goal_id>")
def get_goal(goal_id: str):
    try:
        goal = nessie.get_goal(goal_id)
        return jsonify(goal), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@goal_bp.post("/accounts/<account_id>/goals")
def create_goal(account_id: str):
    data = request.get_json(force=True)
    name = data.get("name")
    amount = data.get("amount")
    description = data.get("description")

    if not all([name, amount]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        goal = nessie.create_goal(
            account_id=account_id,
            name=name,
            amount=amount,
            description=description
        )
        return jsonify(goal), 201
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@goal_bp.put("/goals/<goal_id>")
def update_goal(goal_id: str):
    data = request.get_json(force=True)
    try:
        updated = nessie.update_goal(goal_id, data)
        return jsonify(updated), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@goal_bp.delete("/goals/<goal_id>")
def delete_goal(goal_id: str):
    try:
        nessie.delete_goal(goal_id)
        return jsonify({"message": "Goal deleted successfully"}), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code
