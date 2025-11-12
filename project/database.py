import sqlite3
import os
import csv
from flask import g, session, redirect
from supabase import create_client, Client 
from helpers import apology
from werkzeug.security import check_password_hash, generate_password_hash

# Supabase environment variables and client
url: str = os.environ.get("MEALPLAN_SUPABASE_URL") or "unknown-url"
key: str = os.environ.get("MEALPLAN_SUPABASE_KEY") or "unknown-key"
supabase: Client = create_client(url, key)
#stores = supabase.table("Stores").select("*").execute()
#print("stores", stores)

def get_user_data():
    """Get the active user's data"""
    response = supabase.table("Users").select("*").eq("id", session["user_id"]).execute()
    if len(response.data) > 0:
        return response.data[0]


def login_user(request):
    # Ensure username was submitted
    if not request.form.get("username"):
        return apology("must provide username", 403)

    # Ensure password was submitted
    elif not request.form.get("password"):
        return apology("must provide password", 403)

    # Query database for username
    response = supabase.table("Users").select("*").eq("username", request.form.get("username")).execute()

    # Ensure username exists and password is correct
    if len(response.data) != 1 or not check_password_hash(
        response.data[0]["hash"], request.form.get("password")
    ):
        return apology("invalid username and/or password", 403)

    # Remember which user has logged in
    session["user_id"] = response.data[0]["id"]

    # Redirect user to home page
    return redirect("/")


def register_new_user(request):
    """Register a new user based of form data in the request"""
    # Ensure username was submitted, and is not already in use
    username = request.form.get("username")
    if not username:
        return apology("must provide username", 400)

    response = supabase.table("Users").select("*").eq("username", username).execute()
    print("register checking existing users", response)
    if len(response.data) > 0:
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
    response = supabase.table("Users").insert({"username": username, "hash": hash}).execute()

    # If it worked, Add this user to the session
    print("after register, response", response)
    if len(response.data) == 0:
        return apology("failed to register a new user")
    session["user_id"] = response.data[0]["id"]

    # Redirect user to home page
    return redirect("/")