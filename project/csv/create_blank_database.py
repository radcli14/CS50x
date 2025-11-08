import sqlite3
import csv
import os

# Get the project root directory (parent of csv folder)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# Database file path (in project root)
DATABASE = os.path.join(PROJECT_ROOT, "mealplan.db")

# Remove existing database if it exists
if os.path.exists(DATABASE):
    os.remove(DATABASE)
    print(f"Removed existing {DATABASE}")

# Connect to database
db = sqlite3.connect(DATABASE)
cursor = db.cursor()

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

print("Created all tables successfully")

# Import CSV files
csv_folder = os.path.dirname(__file__)

# Import stores
print("Importing stores...")
with open(os.path.join(csv_folder, "stores.csv"), "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        cursor.execute(
            "INSERT INTO stores (id, name, address) VALUES (?, ?, ?)",
            (int(row["id"]), row["name"], row["address"])
        )

# Import items
print("Importing items...")
with open(os.path.join(csv_folder, "items.csv"), "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        quantity = float(row["quantity"]) if row["quantity"] else None
        cursor.execute(
            "INSERT INTO items (id, name, quantity, unit) VALUES (?, ?, ?, ?)",
            (row["id"], row["name"], quantity, row["unit"] if row["unit"] else None)
        )

# Import lists
print("Importing lists...")
with open(os.path.join(csv_folder, "lists.csv"), "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        cursor.execute(
            "INSERT INTO lists (id, item_id, quantity) VALUES (?, ?, ?)",
            (int(row["id"]), row["item_id"], int(row["quantity"]))
        )

# Import meals
print("Importing meals...")
with open(os.path.join(csv_folder, "meals.csv"), "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        cursor.execute(
            "INSERT INTO meals (id, user_id, date, type, summary) VALUES (?, ?, ?, ?, ?)",
            (int(row["id"]), int(row["user_id"]), row["date"], row["type"], row["summary"])
        )

# Import trips
print("Importing trips...")
with open(os.path.join(csv_folder, "trips.csv"), "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        cursor.execute(
            "INSERT INTO trips (user_id, store_id, list_id, date, summary) VALUES (?, ?, ?, ?, ?)",
            (int(row["user_id"]), int(row["store_id"]), int(row["list_id"]), row["date"], row["summary"])
        )

# Commit all changes
db.commit()
db.close()

print(f"\nSuccessfully created {DATABASE} with all tables and imported CSV data!")
print("\nTable row counts:")
db = sqlite3.connect(DATABASE)
cursor = db.cursor()
for table in ["users", "stores", "items", "lists", "meals", "trips"]:
    count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"  {table}: {count} rows")
db.close()

