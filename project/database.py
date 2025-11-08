import sqlite3
from flask import g

# Database file path
DATABASE = "mealplan.db"
# The database uses the schema:
# CREATE TABLE users (
#     id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
#     username TEXT NOT NULL,
#     hash TEXT NOT NULL
# );


def get_db():
    """
    Get database connection.
    Reuses connection per request using Flask's g object.
    """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # Makes rows accessible by column name
    return db


def close_db(exception):
    """
    Close database connection at end of request.
    This function should be registered with app.teardown_appcontext
    """
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db(app):
    """
    Initialize database connection handling for the Flask app.
    Registers the teardown handler to close connections.
    
    Args:
        app: Flask application instance
    """
    app.teardown_appcontext(close_db)

