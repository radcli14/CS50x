import sqlite3
import os
import csv
from flask import g, session

# Database file path
# On Vercel, filesystem is read-only except /tmp
# Use /tmp for database in serverless environments, otherwise use local path
if os.environ.get("VERCEL") == "1":
    DATABASE = "/tmp/mealplan.db"
else:
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
    Also ensures schema is initialized on first access (lazy initialization).
    """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # Makes rows accessible by column name
        # Lazy initialization: ensure schema exists on first connection
        # This avoids initialization errors during module import
        _ensure_schema_initialized(db)
    return db


def _ensure_schema_initialized(db):
    """
    Check if schema is initialized, and initialize if needed.
    Uses a flag in Flask's g to avoid checking on every request.
    """
    if not getattr(g, '_schema_initialized', False):
        try:
            init_schema(db)
            g._schema_initialized = True
        except Exception as e:
            # Log the error but don't fail silently
            import sys
            import traceback
            error_msg = f"Schema initialization failed: {str(e)}\n{traceback.format_exc()}"
            print(error_msg, file=sys.stderr)
            # Re-raise so the error is visible
            raise


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


def init_schema(db):
    """
    Initialize database schema if tables don't exist.
    This ensures the database is ready to use.
    Also imports CSV data if tables are being created for the first time.
    """
    cursor = db.cursor()
    
    # Check if users table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='users'
    """)
    
    if not cursor.fetchone():
        # Create users table
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                username TEXT NOT NULL,
                hash TEXT NOT NULL
            )
        """)
        
        # Create stores table
        cursor.execute("""
            CREATE TABLE stores (
                id INTEGER PRIMARY KEY NOT NULL,
                name TEXT NOT NULL,
                address TEXT
            )
        """)
        
        # Create items table
        cursor.execute("""
            CREATE TABLE items (
                id TEXT PRIMARY KEY NOT NULL,
                name TEXT NOT NULL,
                quantity REAL,
                unit TEXT
            )
        """)
        
        # Create lists table (junction table)
        cursor.execute("""
            CREATE TABLE lists (
                id INTEGER NOT NULL,
                item_id TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                PRIMARY KEY (id, item_id),
                FOREIGN KEY (item_id) REFERENCES items(id)
            )
        """)
        
        # Create meals table
        cursor.execute("""
            CREATE TABLE meals (
                id INTEGER PRIMARY KEY NOT NULL,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                type TEXT NOT NULL,
                summary TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Create trips table
        cursor.execute("""
            CREATE TABLE trips (
                user_id INTEGER NOT NULL,
                store_id INTEGER NOT NULL,
                list_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                summary TEXT,
                PRIMARY KEY (user_id, store_id, list_id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (store_id) REFERENCES stores(id),
                FOREIGN KEY (list_id) REFERENCES lists(id)
            )
        """)
        
        db.commit()
        
        # Import CSV data after creating tables
        _import_csv_data(db, cursor)


def _import_csv_data(db, cursor):
    """
    Import CSV data into the database.
    This is called only when tables are first created.
    """
    import sys
    
    # Get the project root directory (parent of csv folder)
    # Try multiple path resolution strategies for different deployment scenarios
    current_file = os.path.abspath(__file__)
    project_root = os.path.dirname(current_file)
    csv_folder = os.path.join(project_root, "csv")
    
    # Log path resolution for debugging
    print(f"DEBUG: Looking for CSV files. Current file: {current_file}", file=sys.stderr)
    print(f"DEBUG: Project root: {project_root}", file=sys.stderr)
    print(f"DEBUG: CSV folder: {csv_folder}", file=sys.stderr)
    print(f"DEBUG: CSV folder exists: {os.path.exists(csv_folder)}", file=sys.stderr)
    print(f"DEBUG: CWD: {os.getcwd()}", file=sys.stderr)
    
    # If csv folder doesn't exist at expected location, try alternative paths
    # This handles Vercel's deployment structure where files might be in different locations
    if not os.path.exists(csv_folder):
        # Try relative to current working directory
        csv_folder = os.path.join(os.getcwd(), "csv")
        print(f"DEBUG: Trying CWD path: {csv_folder}, exists: {os.path.exists(csv_folder)}", file=sys.stderr)
        if not os.path.exists(csv_folder):
            # Try as relative path
            csv_folder = "csv"
            print(f"DEBUG: Trying relative path: {csv_folder}, exists: {os.path.exists(csv_folder)}", file=sys.stderr)
    
    # Import stores
    stores_path = os.path.join(csv_folder, "stores.csv")
    if os.path.exists(stores_path):
        try:
            with open(stores_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cursor.execute(
                        "INSERT INTO stores (id, name, address) VALUES (?, ?, ?)",
                        (int(row["id"]), row["name"], row["address"])
                    )
        except Exception as e:
            print(f"Warning: Could not import stores.csv: {e}")
    
    # Import items
    items_path = os.path.join(csv_folder, "items.csv")
    if os.path.exists(items_path):
        try:
            with open(items_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    quantity = float(row["quantity"]) if row["quantity"] else None
                    cursor.execute(
                        "INSERT INTO items (id, name, quantity, unit) VALUES (?, ?, ?, ?)",
                        (row["id"], row["name"], quantity, row["unit"] if row["unit"] else None)
                    )
        except Exception as e:
            print(f"Warning: Could not import items.csv: {e}")
    
    # Import lists
    lists_path = os.path.join(csv_folder, "lists.csv")
    if os.path.exists(lists_path):
        try:
            with open(lists_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cursor.execute(
                        "INSERT INTO lists (id, item_id, quantity) VALUES (?, ?, ?)",
                        (int(row["id"]), row["item_id"], int(row["quantity"]))
                    )
        except Exception as e:
            print(f"Warning: Could not import lists.csv: {e}")
    
    # Import meals
    meals_path = os.path.join(csv_folder, "meals.csv")
    if os.path.exists(meals_path):
        try:
            with open(meals_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cursor.execute(
                        "INSERT INTO meals (id, user_id, date, type, summary) VALUES (?, ?, ?, ?, ?)",
                        (int(row["id"]), int(row["user_id"]), row["date"], row["type"], row["summary"])
                    )
        except Exception as e:
            print(f"Warning: Could not import meals.csv: {e}")
    
    # Import trips
    trips_path = os.path.join(csv_folder, "trips.csv")
    if os.path.exists(trips_path):
        try:
            with open(trips_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cursor.execute(
                        "INSERT INTO trips (user_id, store_id, list_id, date, summary) VALUES (?, ?, ?, ?, ?)",
                        (int(row["user_id"]), int(row["store_id"]), int(row["list_id"]), row["date"], row["summary"])
                    )
        except Exception as e:
            print(f"Warning: Could not import trips.csv: {e}")
    
    # Commit all CSV imports
    db.commit()


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

