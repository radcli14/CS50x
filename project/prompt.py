from database import get_user_meals_str, get_user_name, get_user_trips_str
from google import genai

# Display a prompt to the user
print("Welcome to the Meal Planner and Shopping List Generator!")
print("Please provide a prompt describing your upcoming shopping trip and meal preferences.")
print("You should include detail such as the number of days, where you will be shopping, and any cravings.")
print("***")
user_request = input("Enter your prompt here: ")

# Get user name, and meals/trips history as formatted strings
user_id = 1
user_name = get_user_name(user_id=user_id)
user_meals_str = get_user_meals_str(user_id=user_id)
user_trips_str = get_user_trips_str(user_id=user_id)

client = genai.Client()

# Create the prompt from the user request and their data
prompt_content = f"""
You are an intelligent meal planner and shopping list generator. Your task is to recommend a list of meals based on the user's history and a new trip request, and then generate a corresponding shopping list.

## 📋 Contextual Data
1.  **User Name:** 
{user_name}

2.  **Meal History (for inspiration):** 
{user_meals_str}

3.  **Trip History (for store/duration context):** 
{user_trips_str}

## Task and Request
The user is planning a new trip with the following description: **'{user_request}'**.

Based on the **number of days** specified in the request and the user's past meal/trip data, perform the following steps:
1.  **Generate a MEAL PLAN:** 
Create a simple list of enough meals based on the user's prompt. 
Each item should be a simple sentence describing the meal (e.g., "Chicken with rice and broccoli").
These should be inspired by the user's meal history but also varied to introduce new ideas.
Consider which day of the week (Monday, Tuesday, ...) the request is being made in your planning.

2.  **Generate a SHOPPING LIST:** 
Create a detailed list of all ingredients needed for the generated meal plan. 
The format must match the style of a typical store shopping list (e.g., list items with approximate quantities).
Try to estimate the user's current inventory based on recent shopping trips, rather than assuming they need everything from scratch.

## Required Output Format
Your entire response must be structured exactly as follows, using Markdown headings:

### MEAL PLAN
- [ ] [Date in YYYY-MM-DD format], [Meal Type from ("Breakfast", "Hameikatako", "Lunch", or "Dinner")], [Meal 1 description]
- [ ] [Date in YYYY-MM-DD format], [Meal Type from ("Breakfast", "Hameikatako", "Lunch", or "Dinner")],  [Meal 2 description]
- [ ] ... 

### SHOPPING LIST
- [ ] [Item Name], [Quantity as a plain number, no units]
- [ ] [Item Name], [Quantity as a plain number, no units]
- [ ] ...
"""

# Call the Gemini API to generate the meal plan and shopping list
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt_content
)

# Print the result for both the prompt and the response
print("Prompt Content\n-------------\n", prompt_content, "\n")
print("Response\n---------------\n", response.text, "\n")
