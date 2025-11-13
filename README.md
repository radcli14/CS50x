# CS50x
Homework assignments for Harvard CS50x

## TEMP: database access

I was able to access with the following:

```python
from key import url, key # key.py not to be tracked on git
from supabase import create_client, Client 

supabase: Client = create_client(url, key)

lists = supabase.table("Lists").select("*").execute()

# Get user data (index 1 is Eliott)
response = supabase.table("Users").select("*").eq("id", 1).execute()
user = response.data[0]

# Get trips for that user
response = supabase.table("Trips").select("*").eq("user_id", 1).execute()
trips = response.data

# Get lists joined with trips
response = supabase.from_("Trips").select("id, user_id, store_id, date, summary, Lists(id, item_id, quantity)").eq("user_id", 1).execute() 
lists = response.data

# Get trips joined with store name and address, and flattened
response = supabase.from_("Trips").select("id, user_id, store_id, date, summary, Stores(name, address)").execute()
trips = response.data
for trip in trips:
    for store_key in trip["Stores"].keys():
        trip[store_key] = trip["Stores"][store_key]
    trip.pop("Stores");
```