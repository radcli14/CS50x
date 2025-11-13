import os
from datetime import datetime
from endpoints import api_bp
from flask import Flask, redirect, render_template, request, session
from flask_session import Session

from helpers import login_required
from database import (
    change_user_password, 
    get_stores, get_user_data, get_user_lists, get_user_meals, get_user_trips, 
    login_user, register_new_user
    )

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
        return change_user_password(request)

    else:
        return render_template("change_password.html")


@app.route("/")
@login_required
def index():
    data = get_user_data()
    print("index data", data)
    return render_template("index.html", data=data)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        return login_user(request)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/lists")
@login_required
def lists():
    """Show the user's lists"""
    data = get_user_data()
    trips = get_user_trips()
    items = get_user_lists()
    return render_template("lists.html", data=data, trips=trips, items=items)


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
    data = get_user_data()
    meals = get_user_meals()
    return render_template("meals.html", data=data, meals=meals)


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
    data = get_user_data()
    stores = get_stores()
    return render_template("stores.html", data=data, stores=stores)
