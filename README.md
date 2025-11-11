# CS50x
Homework assignments for Harvard CS50x

## TEMP: database access

I was able to access with the following:

```python
from supabase import create_client, Client 

url: str = ""
key: str = "" # check key.txt

supabase: Client = create_client(url, key)

lists = supabase.table("Lists").select("*").execute()
```