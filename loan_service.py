"""Library rules for loans: checking out, returning and renewing books."""
from datetime import date, timedelta

import book_repository
import fines
import loan_repository
import member_repository
import notifications
import validation
from errors import bad_request, conflict, not_found

LOAN_DAYS = 14
MAX_RENEWALS = 1
LOAN_LIMITS = {"student": 3, "staff": 5}


# ---------- rules about a member's loans (also used by members and reports) ----------


def loan_limit(member_type):
    return LOAN_LIMITS.get(member_type, LOAN_LIMITS["student"])


def count_open_loans(loans):
    return sum(1 for loan in loans if not loan["returned"])


def total_owed(loans):
    return sum(
        fines.balance_owed(loan["due_date"], loan["returned"], loan["fine"], loan["fine_paid"])
        for loan in loans
    )


def current_fine(loan):
    return fines.current_fine(loan["due_date"], loan["returned"], loan["fine"])


def is_overdue(loan):
    return not loan["returned"] and fines.is_overdue(loan["due_date"])


# ---------- use cases ----------


def list_loans(only_overdue):
    loans = loan_repository.list_loans()
    if only_overdue:
        return [loan for loan in loans if is_overdue(loan)]
    return loans


def get_loan(loan_id):
    loan = loan_repository.get_loan(loan_id)
    if loan is None:
        raise not_found("loan not found")
    return loan


def create_loan(data):
    if not data.get("book_id") or not data.get("member_id"):
        raise bad_request("book_id and member_id are required")
    if data.get("due_date") and not validation.is_valid_date(data["due_date"]):
        raise bad_request("invalid due_date")

    book = book_repository.get_book(data["book_id"])
    if book is None:
        raise not_found("book not found")
    member = member_repository.get_member(data["member_id"])
    if member is None:
        raise not_found("member not found")
    if not book["available"]:
        raise conflict("book is not available")

    member_loans = loan_repository.list_loans_for_member(member["id"])
    if total_owed(member_loans) > 0:
        raise conflict("member has unpaid fines")
    if count_open_loans(member_loans) >= loan_limit(member["type"]):
        raise conflict("loan limit reached")

    today = date.today()
    due_date = data.get("due_date") or (today + timedelta(days=LOAN_DAYS)).isoformat()
    loan = loan_repository.create_loan(data["book_id"], data["member_id"], due_date, today.isoformat())
    notifications.send_email(member["email"], "Book checked out", "You checked out " + book["title"])
    return loan


def return_book(loan_id):
    loan = get_loan(loan_id)
    if loan["returned"]:
        raise conflict("loan already returned")

    fine = fines.late_fine(loan["due_date"])
    updated = loan_repository.mark_returned(loan_id, loan["book_id"], fine)
    member = member_repository.get_member(loan["member_id"])
    book = book_repository.get_book(loan["book_id"])
    notifications.send_email(
        member["email"], "Book returned", "You returned " + book["title"] + ". Fine: $" + str(fines.money(fine))
    )
    return updated


def renew_loan(loan_id):
    loan = get_loan(loan_id)
    if loan["returned"]:
        raise conflict("loan already returned")
    if fines.is_overdue(loan["due_date"]):
        raise conflict("overdue loans cannot be renewed")
    if loan["renewals"] >= MAX_RENEWALS:
        raise conflict("loan was already renewed")

    new_due = (date.fromisoformat(loan["due_date"]) + timedelta(days=LOAN_DAYS)).isoformat()
    updated = loan_repository.extend_loan(loan_id, new_due)
    member = member_repository.get_member(loan["member_id"])
    book = book_repository.get_book(loan["book_id"])
    notifications.send_email(member["email"], "Loan renewed", "You renewed " + book["title"])
    return updated
