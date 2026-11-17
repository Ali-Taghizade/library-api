"""HTTP routes for paying fines: read the request, call the service, return JSON."""
from flask import Blueprint, jsonify

import fine_service
import fines

bp = Blueprint("fines", __name__)


def loan_json(loan):
    return {
        "id": loan["id"],
        "book_id": loan["book_id"],
        "member_id": loan["member_id"],
        "due_date": loan["due_date"],
        "returned": bool(loan["returned"]),
        "fine": fines.money(loan["fine"]),
        "fine_paid": bool(loan["fine_paid"]),
        "renewals": loan["renewals"],
        "checked_out": loan["checked_out"],
    }


@bp.route("/loans/<int:loan_id>/pay-fine", methods=["POST"])
def pay_fine(loan_id):
    return jsonify(loan_json(fine_service.pay_fine(loan_id)))
