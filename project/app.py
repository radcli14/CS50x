import os
import sys
import traceback

# Add diagnostic logging for import
print("=" * 80, file=sys.stderr)
print("STARTING APP.PY IMPORT", file=sys.stderr)
print(f"Python version: {sys.version}", file=sys.stderr)
print("=" * 80, file=sys.stderr)

try:
    print("Importing Flask...", file=sys.stderr)
    from datetime import datetime
    from flask import Flask, flash, redirect, render_template, request, session
    print("Flask imported successfully", file=sys.stderr)
except Exception as e:
    print(f"ERROR importing Flask: {e}", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    raise

try:
    print("Importing flask_session...", file=sys.stderr)
    from flask_session import Session
    print("flask_session imported successfully", file=sys.stderr)
except Exception as e:
    print(f"ERROR importing flask_session: {e}", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    raise

try:
    print("Importing werkzeug...", file=sys.stderr)
    from werkzeug.security import check_password_hash, generate_password_hash
    print("werkzeug imported successfully", file=sys.stderr)
except Exception as e:
    print(f"ERROR importing werkzeug: {e}", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    raise

try:
    print("Importing helpers...", file=sys.stderr)
    from helpers import apology, login_required
    print("helpers imported successfully", file=sys.stderr)
except Exception as e:
    print(f"ERROR importing helpers: {e}", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    raise

try:
    print("Importing database...", file=sys.stderr)
    from database import get_db, init_db, get_user_data
    print("database imported successfully", file=sys.stderr)
except Exception as e:
    print(f"ERROR importing database: {e}", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    raise

# Configure application
print("Creating Flask app...", file=sys.stderr)
try:
    app = Flask(__name__)
    print("Flask app created", file=sys.stderr)
except Exception as e:
    print(f"ERROR creating Flask app: {e}", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    raise

# Configure session storage
# Check if we're running on Vercel (serverless environment)
# Vercel sets VERCEL environment variable
print("Checking Vercel environment...", file=sys.stderr)
is_vercel = os.environ.get("VERCEL") == "1"
print(f"Is Vercel: {is_vercel}", file=sys.stderr)

try:
    if is_vercel:
        # On Vercel, use Flask's default signed cookie sessions (filesystem not available)
        print("Configuring for Vercel...", file=sys.stderr)
        app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
        app.config["SESSION_PERMANENT"] = False
        # Flask will use signed cookies by default when Session is not configured
        print("Vercel session config complete", file=sys.stderr)
    else:
        # Local development: use filesystem sessions
        print("Configuring for local development...", file=sys.stderr)
        app.config["SESSION_PERMANENT"] = False
        app.config["SESSION_TYPE"] = "filesystem"
        Session(app)
        print("Local session config complete", file=sys.stderr)
except Exception as e:
    print(f"ERROR configuring sessions: {e}", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    raise

# Initialize database connection handling
print("Initializing database...", file=sys.stderr)
try:
    init_db(app)
    print("Database initialized", file=sys.stderr)
except Exception as e:
    print(f"ERROR initializing database: {e}", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    raise

print("=" * 80, file=sys.stderr)
print("SUCCESS: APP.PY FULLY LOADED", file=sys.stderr)
print("=" * 80, file=sys.stderr)


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change the user's password"""

    if request.method == "POST":
        # Get current user data, as well as form data
        data = get_user_data()
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        # Check that the old password matches the user's current password
        if not old_password:
            return apology("Please enter your existing password", 403)
        if not check_password_hash(data["hash"], old_password):
            return apology("You entered your existing password incorrectly", 403)

        # Check that a new password was entered
        if not new_password:
            return apology("Please enter a new password", 403)

        if confirmation != new_password:
            return apology("Your confirmation does not match the new password", 403)

        # Create a secure hash of the **new** password
        hash = generate_password_hash(new_password)

        # Update the user's password in the database
        db = get_db()
        db.execute("UPDATE users SET hash = ? WHERE id = ?", (hash, session["user_id"]))
        db.commit()  # Important: commit the transaction

        # Redirect back to the index
        return redirect("/")

    else:
        return render_template("change_password.html")


@app.route("/")
@login_required
def index():
    data=get_user_data()
    print(data)
    return render_template("index.html", data=data)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        db = get_db()
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", (request.form.get("username"),)
        ).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/lists")
@login_required
def lists():
    """Show the user's lists"""
    data=get_user_data()
    return render_template("lists.html", data=data)


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/meals")
@login_required
def meals():
    """Show the user's meals"""
    data=get_user_data()
    return render_template("meals.html", data=data)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted, and is not already in use
        username = request.form.get("username")
        if not username:
            return apology("must provide username", 400)
        
        db = get_db()
        rows = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchall()
        if len(rows) > 0:
            return apology(f"username {username} is already in use")

        # Ensure password was submitted
        password = request.form.get("password")
        if not password:
            return apology("must provide password", 400)

        # Ensure password and confirmation match
        confirmation = request.form.get("confirmation")
        if not confirmation:
            return apology("must provide confirmation", 400)
        if password != confirmation:
            return apology("password and confirmation must match")

        # Create a secure hash of the password
        hash = generate_password_hash(password)

        # Insert this user into the database
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hash))
        db.commit()  # Important: commit the transaction

        # Get the new database entry with this user
        rows = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchall()

        # Add this user to the session
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/stores")
@login_required
def stores():
    """Show the user's stores"""
    data=get_user_data()
    return render_template("stores.html", data=data)