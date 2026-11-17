"""Library reports, built from the same rules the loans use."""
import book_repository
import fines
import loan_repository
import loan_service
import report_repository


def overdue_report():
    """Open loans past their due date, each with its fine so far, plus the total."""
    items = []
    for loan in report_repository.list_open_loans_with_details():
        if fines.is_overdue(loan["due_date"]):
            items.append(
                {
                    "loan_id": loan["loan_id"],
                    "title": loan["title"],
                    "member": loan["member"],
                    "days_late": fines.days_late(loan["due_date"]),
                    "fine": fines.late_fine(loan["due_date"]),
                }
            )
    return {"items": items, "total_fines": sum(item["fine"] for item in items)}


def summary_report():
    """Totals for the whole library."""
    loans = loan_repository.list_loans()
    return {
        "total_books": book_repository.count_books(),
        "on_loan": loan_service.count_open_loans(loans),
        "fines_outstanding": loan_service.total_owed(loans),
    }
