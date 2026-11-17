"""Library rules for books."""
import book_repository
import validation
from checks import ensure, ensure_fields, ensure_found, ensure_valid


def list_books(only_available):
    return book_repository.list_books(only_available)


def get_book(book_id):
    return ensure_found(book_repository.get_book(book_id), "book not found")


def create_book(data):
    ensure_fields(data, ["title", "author"], "title and author are required")
    ensure_valid(validation.is_valid_isbn(data.get("isbn")), "invalid isbn")
    return book_repository.create_book(data["title"], data["author"], data["isbn"])


def delete_book(book_id):
    book = get_book(book_id)
    ensure(book["available"], "book is on loan")
    book_repository.delete_book(book_id)
