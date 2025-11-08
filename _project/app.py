import os
import sys
import traceback

# Add diagnostic logging for import
# Flush immediately to ensure output appears even if process crashes
def log(msg):
    # Write to both stderr and stdout (Vercel might capture either)
    print(msg, file=sys.stderr, flush=True)
    print(msg, file=sys.stdout, flush=True)
    # Backup: write to file in /tmp (if on Vercel)
    if os.environ.get("VERCEL") == "1":
        try:
            with open("/tmp/vercel_debug.log", "a") as f:
                f.write(f"{msg}\n")
                f.flush()
        except:
            pass  # Don't fail if we can't write to file

log("=" * 80)
log("STARTING APP.PY IMPORT")
log(f"Python version: {sys.version}")
log("=" * 80)

try:
    log("Importing Flask...")
    from datetime import datetime
    from flask import Flask, flash, redirect, render_template, request, session
    log("Flask imported successfully")
except Exception as e:
    log(f"ERROR importing Flask: {e}")
    log(traceback.format_exc())
    raise

try:
    log("Importing flask_session...")
    from flask_session import Session
    log("flask_session imported successfully")
except Exception as e:
    log(f"ERROR importing flask_session: {e}")
    log(traceback.format_exc())
    raise

try:
    log("Importing werkzeug...")
    from werkzeug.security import check_password_hash, generate_password_hash
    log("werkzeug imported successfully")
except Exception as e:
    log(f"ERROR importing werkzeug: {e}")
    log(traceback.format_exc())
    raise

try:
    log("Importing helpers...")
    from helpers import apology, login_required
    log("helpers imported successfully")
except Exception as e:
    log(f"ERROR importing helpers: {e}")
    log(traceback.format_exc())
    raise

try:
    log("Importing database...")
    from database import get_db, init_db, get_user_data
    log("database imported successfully")
except Exception as e:
    log(f"ERROR importing database: {e}")
    log(traceback.format_exc())
    raise

# Configure application
log("Creating Flask app...")
try:
    app = Flask(__name__)
    log("Flask app created")
except Exception as e:
    log(f"ERROR creating Flask app: {e}")
    log(traceback.format_exc())
    raise

# Configure session storage
# Check if we're running on Vercel (serverless environment)
# Vercel sets VERCEL environment variable
log("Checking Vercel environment...")
is_vercel = os.environ.get("VERCEL") == "1"
log(f"Is Vercel: {is_vercel}")

try:
    if is_vercel:
        # On Vercel, use Flask's default signed cookie sessions (filesystem not available)
        log("Configuring for Vercel...")
        app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
        app.config["SESSION_PERMANENT"] = False
        # Flask will use signed cookies by default when Session is not configured
        log("Vercel session config complete")
    else:
        # Local development: use filesystem sessions
        log("Configuring for local development...")
        app.config["SESSION_PERMANENT"] = False
        app.config["SESSION_TYPE"] = "filesystem"
        Session(app)
        log("Local session config complete")
except Exception as e:
    log(f"ERROR configuring sessions: {e}")
    log(traceback.format_exc())
    raise

# Initialize database connection handling
log("Initializing database...")
try:
    init_db(app)
    log("Database initialized")
except Exception as e:
    log(f"ERROR initializing database: {e}")
    log(traceback.format_exc())
    raise

log("=" * 80)
log("SUCCESS: APP.PY FULLY LOADED")
log("=" * 80)


@app.route("/debug/logs")
def debug_logs():
    """Diagnostic endpoint to view debug logs from /tmp"""
    import json
    logs = []
    try:
        if os.path.exists("/tmp/vercel_debug.log"):
            with open("/tmp/vercel_debug.log", "r") as f:
                logs.append({"file": "vercel_debug.log", "content": f.read()})
    except Exception as e:
        logs.append({"file": "vercel_debug.log", "error": str(e)})
    
    try:
        if os.path.exists("/tmp/vercel_error.log"):
            with open("/tmp/vercel_error.log", "r") as f:
                logs.append({"file": "vercel_error.log", "content": f.read()})
    except Exception as e:
        logs.append({"file": "vercel_error.log", "error": str(e)})
    
    return json.dumps({
        "logs": logs,
        "vercel_env": os.environ.get("VERCEL", "NOT SET"),
        "cwd": os.getcwd(),
        "python_path": sys.path
    }, indent=2)


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