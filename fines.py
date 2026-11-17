"""Library fine rules: late returns cost a fixed amount per day overdue.

Every function takes plain values (no HTTP, no database rows), so the rules can be
tested on their own. Pass `today` to test a specific date.
"""
from datetime import date

FINE_PER_DAY = 0.50


def days_late(due_date: str, today: date | None = None) -> int:
    """Days past the due date (negative while the loan is not yet due)."""
    today = today or date.today()
    return (today - date.fromisoformat(due_date)).days


def is_overdue(due_date: str, today: date | None = None) -> bool:
    """True once the due date has passed."""
    return days_late(due_date, today) > 0


def late_fine(due_date: str, today: date | None = None) -> float:
    """Fine accrued for a loan with this due date, returned or checked as of `today`."""
    return max(0, days_late(due_date, today)) * FINE_PER_DAY


def current_fine(due_date: str, returned: bool, fine: float, today: date | None = None) -> float:
    """The loan's fine right now: still building up while open, fixed once returned."""
    if not returned:
        return late_fine(due_date, today)
    return fine


def balance_owed(due_date: str, returned: bool, fine: float, fine_paid: bool, today: date | None = None) -> float:
    """What a single loan currently costs its member (nothing once its fine is paid)."""
    if returned and fine_paid:
        return 0.0
    return current_fine(due_date, returned, fine, today)


def has_fine_to_pay(fine: float, fine_paid: bool) -> bool:
    """True when a returned loan has a fine that hasn't been paid yet."""
    return fine > 0 and not fine_paid


def money(amount) -> float:
    """Round an amount to cents for display."""
    return round(float(amount), 2)
