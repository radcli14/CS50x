import os
from datetime import datetime
from endpoints import api_bp
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required
from database import get_user_data, register_new_user

app = Flask(__name__)

# Configure secret key (required for sessions)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"

# Configure session - filesystem sessions don't work on Vercel's read-only filesystem
# Use filesystem locally, but Flask's default cookie sessions on Vercel
app.config["SESSION_PERMANENT"] = False
if os.environ.get("VERCEL"):
    # On Vercel: use Flask's built-in signed cookie sessions (no flask-session needed)
    app.config["SESSION_COOKIE_SECURE"] = True
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
else:
    # Local development: use filesystem sessions
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

app.register_blueprint(api_bp)


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
    print("index data", data)
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
        print("before error", db)
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
        return register_new_user(request)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/stores")
@login_required
def stores():
    """Show the user's stores"""
    data=get_user_data()
    return render_template("stores.html", data=data)
