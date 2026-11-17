"""Error handling: services raise errors, and this module turns them into JSON responses.

Services call error(message, status) (or a shortcut such as not_found) without
knowing anything about HTTP responses; register_error_handlers connects that to Flask.
"""
from flask import jsonify


class LibraryError(Exception):
    def __init__(self, message, status):
        super().__init__(message)
        self.message = message
        self.status = status


def error(message, status):
    """Create an error with a custom message and HTTP status code, ready to raise."""
    return LibraryError(message, status)


def bad_request(message):
    return error(message, 400)


def not_found(message):
    return error(message, 404)


def conflict(message):
    return error(message, 409)


def error_response(message, status):
    """The JSON body and status code the API sends for an error."""
    return jsonify({"error": message}), status


def register_error_handlers(app):
    @app.errorhandler(LibraryError)
    def handle_library_error(err):
        return error_response(err.message, err.status)
