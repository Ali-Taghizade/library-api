"""Reusable checks for services: each one raises an error when it fails.

They replace the repeated "if ... : return an error" blocks, so a service reads as a
list of conditions.
"""
from errors import bad_request, error, not_found


def ensure_found(item, message):
    """404 when the record doesn't exist; otherwise return it."""
    if item is None:
        raise not_found(message)
    return item


def ensure_fields(data, fields, message):
    """400 when any of the required fields is missing or empty."""
    if any(not data.get(field) for field in fields):
        raise bad_request(message)


def ensure_valid(is_valid, message):
    """400 when a value failed validation."""
    if not is_valid:
        raise bad_request(message)


def ensure(condition, message, status=409):
    """Raise an error (409 Conflict by default) when a library rule isn't met."""
    if not condition:
        raise error(message, status)
