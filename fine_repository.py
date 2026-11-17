"""SQL needed to pay a fine. No HTTP, no library rules.

get_loan and get_member_email overlap with what the loan and member repositories
will need; when those domains are refactored, fine_service can call them instead.
"""
import db


def get_loan(loan_id):
    conn = db.connect()
    loan = conn.execute("SELECT * FROM loans WHERE id = ?", (loan_id,)).fetchone()
    conn.close()
    return loan


def get_member_email(member_id):
    conn = db.connect()
    row = conn.execute("SELECT email FROM members WHERE id = ?", (member_id,)).fetchone()
    conn.close()
    return row["email"]


def mark_fine_paid(loan_id):
    conn = db.connect()
    conn.execute("UPDATE loans SET fine_paid = 1 WHERE id = ?", (loan_id,))
    conn.commit()
    loan = conn.execute("SELECT * FROM loans WHERE id = ?", (loan_id,)).fetchone()
    conn.close()
    return loan
