import os

from flask import Flask, jsonify

import book_routes
import db
import fine_routes
import fines
import loan_routes
import member_routes
from db import init_db
from errors import LibraryError

app = Flask(__name__)
app.register_blueprint(book_routes.bp)
app.register_blueprint(member_routes.bp)
app.register_blueprint(loan_routes.bp)
app.register_blueprint(fine_routes.bp)


@app.errorhandler(LibraryError)
def handle_library_error(error):
    return jsonify({"error": error.message}), error.status


# ---------- reports ----------


@app.route("/reports/overdue", methods=["GET"])
def report_overdue():
    conn = db.connect()
    rows = conn.execute(
        """
        SELECT loans.id, books.title, members.name, loans.due_date
        FROM loans
        JOIN books ON books.id = loans.book_id
        JOIN members ON members.id = loans.member_id
        WHERE loans.returned = 0
        """
    ).fetchall()
    conn.close()
    items = []
    total = 0
    for r in rows:
        if fines.is_overdue(r[3]):
            fine = fines.late_fine(r[3])
            total += fine
            items.append(
                {"loan_id": r[0], "title": r[1], "member": r[2], "days_late": fines.days_late(r[3]), "fine": fines.money(fine)}
            )
    return jsonify({"items": items, "total_fines": fines.money(total)})


@app.route("/reports/summary", methods=["GET"])
def report_summary():
    conn = db.connect()
    total_books = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    rows = conn.execute("SELECT * FROM loans").fetchall()
    conn.close()
    on_loan = 0
    outstanding = 0
    for loan in rows:
        if loan[4] == 0:
            on_loan += 1
        outstanding += fines.balance_owed(loan[3], loan[4], loan[5], loan[6])
    return jsonify({"total_books": total_books, "on_loan": on_loan, "fines_outstanding": fines.money(outstanding)})


if not os.path.exists("library.db"):
    init_db()
