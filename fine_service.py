"""Paying fines: checks the rules, saves the payment, emails the member.

The fine amounts themselves come from fines.py, which stays free of database code.
"""
import fines
import loan_repository
import member_repository
import notifications
from checks import ensure, ensure_found


def pay_fine(loan_id):
    loan = ensure_found(loan_repository.get_loan(loan_id), "loan not found")
    ensure(loan["returned"], "return the book before paying")
    ensure(fines.has_fine_to_pay(loan["fine"], loan["fine_paid"]), "no fine to pay")

    updated = loan_repository.mark_fine_paid(loan_id)
    member = member_repository.get_member(loan["member_id"])
    notifications.send_email(member["email"], "Fine paid", "We received $" + str(fines.money(loan["fine"])))
    return updated
