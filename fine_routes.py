"""HTTP routes for paying fines: read the request, call the service, return JSON."""
from flask import Blueprint, jsonify

import fine_service
from loan_routes import loan_json

bp = Blueprint("fines", __name__)


@bp.route("/loans/<int:loan_id>/pay-fine", methods=["POST"])
def pay_fine(loan_id):
    return jsonify(loan_json(fine_service.pay_fine(loan_id)))
