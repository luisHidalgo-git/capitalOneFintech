from flask import Blueprint, request, jsonify
from api import NessieClient, NessieAPIError

application_bp = Blueprint("application", __name__, url_prefix="/api/nessie/applications")

nessie = NessieClient()

@application_bp.get("")
def get_all_applications():
    try:
        applications = nessie.get_applications()
        return jsonify(applications), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@application_bp.get("/<application_id>")
def get_application(application_id: str):
    try:
        application = nessie.get_application(application_id)
        return jsonify(application), 200
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code

@application_bp.post("")
def create_application():
    data = request.get_json(force=True)
    applicant_id = data.get("applicant_id")
    application_type = data.get("type")
    initial_deposit = data.get("initial_deposit")

    if not all([applicant_id, application_type, initial_deposit]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        application = nessie.create_application(
            applicant_id=applicant_id,
            application_type=application_type,
            initial_deposit=initial_deposit
        )
        return jsonify(application), 201
    except NessieAPIError as e:
        return jsonify({"error": e.message}), e.status_code
