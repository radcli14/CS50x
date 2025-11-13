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


def change_user_password(request):
    """Change the user's password in the database"""

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
    response = supabase.table("Users").update({"hash": hash}).eq("id", session["user_id"]).execute()
    print("change_user_password, response", response)

    # Redirect back to the index
    return redirect("/")


def get_stores():
    """Get all of the stores in the database (currently not by user)"""
    response = supabase.table("Stores").select("*").execute()
    return response.data


def get_user_data():
    """Get the active user's data"""
    response = supabase.table("Users").select("*").eq("id", session["user_id"]).execute()
    if len(response.data) > 0:
        return response.data[0]


def get_user_lists():
    """Get all of the lists created by the active user"""
    response = supabase.table("Lists").select("*").execute() # TODO: have to get user items from trips .eq("user_id", session["user_id"])
    return response.data


def get_user_meals():
    """Get all of the meals created by the active user"""
    response = supabase.table("Meals").select("*").eq("user_id", session["user_id"]).execute()
    return response.data


def get_user_trips():
    """Get all of the trips created by the active user"""
    response = (
        supabase.from_("Trips")
            .select("id, user_id, store_id, date, summary, Stores(name, address), Lists(id, item_id, quantity, Items(name))")
            .eq("user_id", session["user_id"])
            .execute() 
    )
    trips = response.data

    # Flatten the table so that store name and address are on the same row as the trip id
    for trip in trips:
        for store_key in trip["Stores"].keys():
            trip[store_key] = trip["Stores"][store_key]
        trip.pop("Stores");
    
        # The item is only used to provide an English name, flatten to that one
        for item in trip["Lists"]:
            item["name"] = item["Items"]["name"]
            item.pop("Items");

    return trips


def login_user(request):
    """Login a user with form data"""
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