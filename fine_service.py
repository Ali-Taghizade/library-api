"""Paying fines: checks the rules, saves the payment, emails the member.

The fine amounts themselves come from fines.py, which stays free of database code.
"""
import fine_repository
import fines
import notifications
from errors import conflict, not_found


def pay_fine(loan_id):
    loan = fine_repository.get_loan(loan_id)
    if loan is None:
        raise not_found("loan not found")
    if not loan["returned"]:
        raise conflict("return the book before paying")
    if not fines.has_fine_to_pay(loan["fine"], loan["fine_paid"]):
        raise conflict("no fine to pay")

    updated = fine_repository.mark_fine_paid(loan_id)
    email = fine_repository.get_member_email(loan["member_id"])
    notifications.send_email(email, "Fine paid", "We received $" + str(fines.money(loan["fine"])))
    return updated
