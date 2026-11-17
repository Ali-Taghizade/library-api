import os

from flask import Flask

import book_routes
import db
import fine_routes
import loan_routes
import member_routes
import report_routes
from db import init_db
from errors import register_error_handlers

app = Flask(__name__)
app.register_blueprint(book_routes.bp)
app.register_blueprint(member_routes.bp)
app.register_blueprint(loan_routes.bp)
app.register_blueprint(fine_routes.bp)
app.register_blueprint(report_routes.bp)
register_error_handlers(app)


if not os.path.exists(db.DB_PATH):
    init_db()
