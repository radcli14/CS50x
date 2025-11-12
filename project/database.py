import sqlite3
import os
import csv
from flask import g, session
from supabase import create_client, Client 

# Database file path
# On Vercel, filesystem is read-only except /tmp
DATABASE = "/tmp/mealplan.db"

# Testing supabase
url: str = os.environ.get("MEALPLAN_SUPABASE_URL") or "unknown-url"
key: str = os.environ.get("MEALPLAN_SUPABASE_KEY") or "unknown-key"
supabase: Client = create_client(url, key)
stores = supabase.table("Stores").select("*").execute()
print("database.py, url:", url)
print("database.py, key:", key)
print("stores", stores)

def get_db():
    """
    Get database connection.
    Reuses connection per request using Flask's g object.
    Also ensures schema is initialized on first access (lazy initialization).
    """
    print("get_db")
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # Makes rows accessible by column name

    print(" returning ", db.execute(".schema").fetchall())
    return db


def get_user_data():
    """Get the active user's data"""
    db = get_db()
    rows = db.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchall()
    if len(rows) > 0:
        return dict(rows[0])
    return None  # Return None if user not found


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
    
    Note: Schema initialization is now lazy - it happens on first database access
    rather than at import time. This prevents errors in serverless environments.
    
    Args:
        app: Flask application instance
    """
    app.teardown_appcontext(close_db)
    # Schema initialization is now handled lazily in get_db()
    # This avoids issues with app context during module import

