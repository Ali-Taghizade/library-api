"""Library rules for loans: checking out, returning and renewing books."""
from datetime import date, timedelta

import book_repository
import fines
import loan_repository
import member_repository
import notifications
import validation
from checks import ensure, ensure_fields, ensure_found, ensure_valid

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
    return ensure_found(loan_repository.get_loan(loan_id), "loan not found")


def create_loan(data):
    ensure_fields(data, ["book_id", "member_id"], "book_id and member_id are required")
    if data.get("due_date"):
        ensure_valid(validation.is_valid_date(data["due_date"]), "invalid due_date")

    book = ensure_found(book_repository.get_book(data["book_id"]), "book not found")
    member = ensure_found(member_repository.get_member(data["member_id"]), "member not found")
    ensure(book["available"], "book is not available")

    member_loans = loan_repository.list_loans_for_member(member["id"])
    ensure(total_owed(member_loans) == 0, "member has unpaid fines")
    ensure(count_open_loans(member_loans) < loan_limit(member["type"]), "loan limit reached")

    today = date.today()
    due_date = data.get("due_date") or (today + timedelta(days=LOAN_DAYS)).isoformat()
    loan = loan_repository.create_loan(data["book_id"], data["member_id"], due_date, today.isoformat())
    notifications.send_email(member["email"], "Book checked out", "You checked out " + book["title"])
    return loan


def return_book(loan_id):
    loan = get_loan(loan_id)
    ensure(not loan["returned"], "loan already returned")

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
    ensure(not loan["returned"], "loan already returned")
    ensure(not fines.is_overdue(loan["due_date"]), "overdue loans cannot be renewed")
    ensure(loan["renewals"] < MAX_RENEWALS, "loan was already renewed")

    new_due = (date.fromisoformat(loan["due_date"]) + timedelta(days=LOAN_DAYS)).isoformat()
    updated = loan_repository.extend_loan(loan_id, new_due)
    member = member_repository.get_member(loan["member_id"])
    book = book_repository.get_book(loan["book_id"])
    notifications.send_email(member["email"], "Loan renewed", "You renewed " + book["title"])
    return updated
