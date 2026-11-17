"""HTTP routes for /reports: call the service, return JSON."""
from flask import Blueprint, jsonify

import fines
import report_service

bp = Blueprint("reports", __name__)


@bp.route("/reports/overdue", methods=["GET"])
def report_overdue():
    report = report_service.overdue_report()
    items = []
    for item in report["items"]:
        items.append({**item, "fine": fines.money(item["fine"])})
    return jsonify({"items": items, "total_fines": fines.money(report["total_fines"])})


@bp.route("/reports/summary", methods=["GET"])
def report_summary():
    report = report_service.summary_report()
    return jsonify(
        {
            "total_books": report["total_books"],
            "on_loan": report["on_loan"],
            "fines_outstanding": fines.money(report["fines_outstanding"]),
        }
    )
