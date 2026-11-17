"""Paying fines: checks the rules, saves the payment, emails the member.

The fine amounts themselves come from fines.py, which stays free of database code.
"""
import fines
import loan_repository
import member_repository
import notifications
from errors import conflict, not_found


def pay_fine(loan_id):
    loan = loan_repository.get_loan(loan_id)
    if loan is None:
        raise not_found("loan not found")
    if not loan["returned"]:
        raise conflict("return the book before paying")
    if not fines.has_fine_to_pay(loan["fine"], loan["fine_paid"]):
        raise conflict("no fine to pay")

    updated = loan_repository.mark_fine_paid(loan_id)
    member = member_repository.get_member(loan["member_id"])
    notifications.send_email(member["email"], "Fine paid", "We received $" + str(fines.money(loan["fine"])))
    return updated
