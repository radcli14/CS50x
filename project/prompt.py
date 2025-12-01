from dotenv import load_dotenv
import os
from google import genai

from database import supabase, get_user_meals, get_user_data, get_user_trips

load_dotenv

# Get user info (for myself, id=1)
user_id = 1
user_data = get_user_data(user_id=user_id)
#print("User Data\n", user_data)

# Get all of the meals this user has logged
user_meals = get_user_meals(user_id=user_id)
#print("Meals\n", user_meals)

# Get all of the trips this user has taken
user_trips = get_user_trips(user_id=user_id)
#print("Trips\n", user_trips)

# User the data in a Gemini AI request to get meal and list suggestions
# gemini_key: str = os.environ.get("GEMINI_API_KEY") or "unknown-key"
user_data_str = str(user_data)
user_meals_str = str(user_meals)
user_trips_str = str(user_trips)

user_request = input("Provide your prompt for meal and list suggestions:")

client = genai.Client()

prompt_content = f"""
You are an intelligent meal planner and shopping list generator. Your task is to recommend a list of meals based on the user's history and a new trip request, and then generate a corresponding shopping list.

## 📋 Contextual Data
1.  **User Profile:** {user_data_str}
2.  **Meal History (for inspiration):** {user_meals_str}
3.  **Trip History (for store/duration context):** {user_trips_str}

## 🎯 Task and Request
The user is planning a new trip with the following description: **'{user_request}'**.

Based on the **number of days** specified in the request and the user's past meal/trip data, perform the following steps:
1.  **Generate a MEAL PLAN:** Create a simple list of enough meals based on the user's prompt. Each item should be a simple sentence describing the meal (e.g., "Chicken with rice and broccoli").
2.  **Generate a SHOPPING LIST:** Create a detailed list of all ingredients needed for the generated meal plan. The format must match the style of a typical store shopping list (e.g., list items with approximate quantities).

## 📝 Required Output Format
Your entire response must be structured exactly as follows, using Markdown headings:

### MEAL PLAN
- [ ] [Date], [Meal Type], [Meal 1 description]
- [ ] [Date], [Meal Type], [Meal 2 description]
- [ ] ... 

### SHOPPING LIST
- [ ] [Item Name], [Approximate Quantity]
- [ ] [Item Name], [Approximate Quantity]
- [ ] ...
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt_content
)

print(response.text)