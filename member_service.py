"""Library rules for members and their accounts."""
import loan_repository
import loan_service
import member_repository
import validation
from checks import ensure, ensure_fields, ensure_found, ensure_valid


def list_members():
    return member_repository.list_members()


def get_member(member_id):
    return ensure_found(member_repository.get_member(member_id), "member not found")


def create_member(data):
    ensure_fields(data, ["name"], "name is required")
    ensure_valid(validation.is_valid_email(data.get("email")), "invalid email")
    member_type = data.get("type", "student")
    ensure_valid(validation.is_valid_member_type(member_type), "type must be student or staff")
    ensure(member_repository.get_member_by_email(data["email"]) is None, "email already registered")
    return member_repository.create_member(data["name"], data["email"], member_type)


def member_account(member_id):
    """A member's loans, what they owe, and how many more books they can borrow."""
    member = get_member(member_id)
    loans = loan_repository.list_loans_for_member(member_id)
    return {
        "loans": loans,
        "total_owed": loan_service.total_owed(loans),
        "loans_remaining": loan_service.loan_limit(member["type"]) - loan_service.count_open_loans(loans),
    }
