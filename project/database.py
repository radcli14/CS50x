import sqlite3
import os
import csv
import re
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


def update_stores(data):
    """Upsert stores data received from the frontend."""
    if not data or not isinstance(data, dict):
        print("update_stores: invalid data payload")
        return None

    stores = data.get("stores") or []

    for store in stores:
        store_id = store.get("id")
        name = store.get("name")
        address = store.get("address")

        try:
            if store_id:
                # Update existing store
                resp = supabase.table("Stores").update({
                    "name": name,
                    "address": address
                }).eq("id", store_id).execute()
                print("update_stores: updated store", store_id, resp)
            else:
                # Insert new store
                resp = supabase.table("Stores").insert({
                    "name": name,
                    "address": address
                }).execute()
                print("update_stores: created store", resp)
        except Exception as e:
            print(f"update_stores: error processing store {store_id}", e)

    return {"status": "ok"}


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


def update_meals(data):
    """Upsert meals data received from the frontend."""
    if not data or not isinstance(data, dict):
        print("update_meals: invalid data payload")
        return None

    meals = data.get("meals") or []
    user_id = session.get("user_id")

    for meal in meals:
        meal_id = meal.get("id")
        date = meal.get("date")
        meal_type = meal.get("type")
        summary = meal.get("summary")

        try:
            if meal_id:
                # Update existing meal
                resp = supabase.table("Meals").update({
                    "date": date,
                    "type": meal_type,
                    "summary": summary
                }).eq("id", meal_id).execute()
                print("update_meals: updated meal", meal_id, resp)
            else:
                # Insert new meal
                resp = supabase.table("Meals").insert({
                    "user_id": user_id,
                    "date": date,
                    "type": meal_type,
                    "summary": summary
                }).execute()
                print("update_meals: created meal", resp)
        except Exception as e:
            print(f"update_meals: error processing meal {meal_id}", e)

    return {"status": "ok"}


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
        if trip["Stores"] is not None:
            for store_key in trip["Stores"].keys():
                trip[store_key] = trip["Stores"][store_key]
            trip.pop("Stores")
        else:
            # If no store is associated with this trip yet, set defaults
            trip["name"] = None
            trip["address"] = None
    
        # The item is only used to provide an English name, flatten to that one
        if trip["Lists"]:
            for item in trip["Lists"]:
                item["name"] = item["Items"]["name"]
                item.pop("Items")

    return trips



def update_list(data):
    """Upsert list/trip/store/items data received from the frontend.

    This is best-effort: it will update the Trips row (if `trip_id` provided),
    upsert the store (by id or name), and update/insert list item rows.
    The exact schema mapping is flexible because Supabase schema may differ;
    we log responses for debugging.
    """
    if not data or not isinstance(data, dict):
        print("update_list: invalid data payload")
        return None

    user_id = session.get("user_id")
    trip_id = data.get("trip_id")
    summary = data.get("summary")
    store_id = data.get("store_id")
    store_name = data.get("store_name")
    store_address = data.get("store_address")
    date = data.get("date")
    items = data.get("items") or []

    # Ensure store exists (if store_id not provided try to find by name or create one)
    if not store_id and store_name:
        store_id = update_store(store_name, store_address)

    # Update the header date, including date, store id, and summary
    trip_update = {}
    if date is not None:
        trip_update["date"] = date
    if store_id is not None:
        trip_update["store_id"] = store_id
    if summary is not None:
        trip_update["summary"] = summary

    try:
        if trip_id:
            # Update existing trip row
            if trip_update:
                resp = supabase.table("Trips").update(trip_update).eq("id", trip_id).execute()
                print("update_list: updated trip", resp)
        else:
            # Create a new trip record and capture its id
            create_payload = {"user_id": user_id}
            create_payload.update(trip_update)
            created = supabase.table("Trips").insert(create_payload).execute()
            print("update_list: created trip", created)
            if created and getattr(created, "data", None) and len(created.data) > 0:
                trip_id = created.data[0].get("id")
    except Exception as e:
        print("update_list: error updating/creating trip", e)

    # Handle items: update existing entries when possible, insert new ones otherwise
    for item in items:
        update_list_item(item, trip_id)

    return {"status": "ok"}


def update_store(name, address):
    """Upsert a store by name and address, returning the store id. Intended to be used when store_id is not provided, in which case we will create one."""
    try:
        # Check if the store already exists by name and address. Name is not unique in the database, but we'll assume its the same location if address also matches
        resp = (
            supabase.table("Stores")
                .select("*")
                .eq("name", name)
                .eq("address", address)
                .limit(1)
                .execute()
        )

        # If found, use that store id
        if resp and resp.data and len(resp.data) > 0:
            return resp.data[0].get("id")
        
        # Otherwise, create a new store, and return its id
        created = supabase.table("Stores").insert({
            "name": name, 
            "address": address
        }).execute()
        print("update_list: created store", created)
        if created and getattr(created, "data", None):
            return created.data[0].get("id")

    except Exception as e:
        print("update_list: store upsert error", e)

def update_list_item(item, trip_id):
    """Update or insert a list item row based on the provided item data, checking based on comparison to previous data."""
    try:
        # row_id represents the integer id, or row, in the Lists table
        row_id = item.get("id")

        # item_id represents the string id in the Items table
        item_id = item.get("itemId")

        # Name and quantity are what are displayed to the user in the frontend
        name = item.get("name")
        qty = item.get("quantity") or 1

        print("\nupdate_list: processing item", item, trip_id)

        # First check if there is existing list row and item, so we know its previous state in the database
        previous_name = None
        if item_id:
            existing_item = (
                supabase.table("Items")
                .select("*")
                .eq("id", item_id)
                .limit(1)
                .execute()
            )
            previous_name = existing_item.data[0].get("name") if existing_item and getattr(existing_item, "data", None) and len(existing_item.data) > 0 else None
        previous_qty = None
        if row_id:
            existing_list_row = (
                supabase.table("Lists")
                .select("*")
                .eq("id", row_id)
                .limit(1)
                .execute()
            )
            previous_qty = existing_list_row.data[0].get("quantity") if existing_list_row and getattr(existing_list_row, "data", None) and len(existing_list_row.data) > 0 else None

        # First scenario, the user created a new item in the list.
        # We need to determine if that item already exists in the Items table (by name).
        # If it doesn't exist, we need to create that item. After this section, the item_id variable should be populated.
        if not item_id and name:
            print(" - 1st scenario: new item, need to lookup or create", name)

            # First check if that name has been used before, in which case we can reuse the item_id
            item_lookup = (
                supabase.table("Items")
                .select("*")
                .eq("name", name)
                .limit(1)
                .execute()
            )
            if item_lookup and getattr(item_lookup, "data", None) and len(item_lookup.data) > 0:
                item_id = item_lookup.data[0].get("id")

            # If we did not find that name in the items table, create a new entry    
            else:
                item_id = generate_item_identifier(name)
                created_item = (
                    supabase.table("Items").insert({
                        "id": item_id, 
                        "name": name
                    }).execute()
                )

                print(" - update_list_item: created item", created_item)
                if created_item and getattr(created_item, "data", None) and len(created_item.data) > 0:
                    item_id = created_item.data[0].get("id")

        # Second scenario, the user is adding a new row, and we do have an item id, but not yet a row id.
        # We need to insert a new row into Lists, and get the new row_id for that row.
        if not row_id:
            print(" - 2nd scenario: new list row, need to create", item_id, qty)

            created_list_row = (
                supabase.table("Lists").insert({
                    "trip_id": trip_id, 
                    "item_id": item_id, 
                    "quantity": qty
                }).execute()
            )
            print(" - update_list_item: created list row", created_list_row)
            if created_list_row and getattr(created_list_row, "data", None) and len(created_list_row.data) > 0:
                row_id = created_list_row.data[0].get("id")

        # Third scenario, we have an existing item and we updated its quantity in the Lists row.
        if row_id and qty != previous_qty:
            print(" - 3rd scenario: update existing list row quantity", row_id, qty)

            updated_list_row = (
                supabase.table("Lists").update({
                    "quantity": qty
                }).eq("id", row_id).execute()
            )
            print(" - update_list_item: updated list row quantity", updated_list_row)

        # Fourth scenario, we have an an existing item and we have changed its name, update the name in the Items table.
        if item_id and name is not None and name != previous_name:
            print(" - 4th scenario: update existing item name", item_id, name)

            updated_item = (
                supabase.table("Items").update({
                    "name": name
                }).eq("id", item_id).execute()
            )
            print(" - update_list_item: updated item name", updated_item)
    

    except Exception as e:
        print(f" *** update_list_item: item processing error at {item} {trip_id}", e)


def generate_item_identifier(text):
    """Convert a string into a lowercase snake_case identifier.
    
    Trims whitespace, converts to lowercase, replaces spaces with underscores,
    and removes any characters that aren't alphanumeric or underscores.
    """
    if not text:
        return None
    
    # Trim, lowercase, and replace spaces with underscores
    identifier = text.strip().lower().replace(" ", "_")
    
    # Keep only alphanumeric and underscores
    identifier = re.sub(r'[^\w]', '', identifier)
    
    # Ensure it doesn't start with a number (valid variable names can't)
    if identifier and identifier[0].isdigit():
        identifier = "_" + identifier
    
    return identifier if identifier else None


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


def create_blank_trip():
    """Create a new blank trip for the user with today's date"""
    from datetime import date
    
    today = str(date.today())
    
    # Create a new trip with minimal data
    response = supabase.table("Trips").insert({
        "user_id": session["user_id"],
        "date": today,
        "summary": ""
    }).execute()
    
    if response.data and len(response.data) > 0:
        return response.data[0]
    else:
        raise Exception("Failed to create new trip")


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