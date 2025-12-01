from database import get_user_meals_str, get_user_name, get_user_trips_str, get_stores
from google import genai
import re
from datetime import datetime


def generate_meal_plan_and_list(user_request, user_id=None):
    """
    Generate a meal plan and shopping list using Gemini API based on user's request and history.

    Args:
        user_request (str): The user's prompt describing their trip and preferences
        user_id (int, optional): The user's ID. Defaults to 1 if not provided.

    Returns:
        dict: Contains 'raw_response' (str), 'meals' (list), 'items' (list), 'store_name' (str)
    """
    # Default to user_id=1 if not provided
    if user_id is None:
        user_id = 1

    # Get current date and day of week for context
    today = datetime.now()
    current_date = today.strftime("%Y-%m-%d")
    current_day = today.strftime("%A")

    # Get user name, and meals/trips history as formatted strings
    user_name = get_user_name(user_id=user_id)
    user_meals_str = get_user_meals_str(user_id=user_id)
    user_trips_str = get_user_trips_str(user_id=user_id)

    # Get list of available stores
    stores = get_stores()
    stores_str = "\n".join([f"  - {store['name']} (Address: {store['address']})" for store in stores])

    client = genai.Client()

    # Create the prompt from the user request and their data
    prompt_content = f"""
You are an intelligent meal planner and shopping list generator. Your task is to recommend a list of meals based on the user's history and a new trip request, and then generate a corresponding shopping list.

## 📋 Contextual Data
1.  **User Name:**
{user_name}

2.  **Current Date and Time:**
Today is {current_day}, {current_date}

3.  **Available Stores:**
{stores_str}

4.  **Meal History (for inspiration):**
{user_meals_str}

5.  **Trip History (for store/duration context):**
{user_trips_str}

## Task and Request
The user is planning a new trip with the following description: **'{user_request}'**.

Based on the request and the user's past meal/trip data, perform the following steps:

1.  **Parse Dates:**
Convert any relative date references (like "tonight", "tomorrow", "this weekend", "next week") into specific YYYY-MM-DD dates based on today's date ({current_date}).

2.  **Identify Store:**
If the user mentions a store name in their request, identify which store from the Available Stores list they are referring to. If no store is mentioned or doesn't match, output "Unknown Store".

3.  **Generate a MEAL PLAN:**
Create a simple list of meals based on the user's prompt with the correct dates.
Each item should be a simple sentence describing the meal (e.g., "Chicken with rice and broccoli").
These should be inspired by the user's meal history but also varied to introduce new ideas.

4.  **Generate a SHOPPING LIST:**
Create a detailed list of all ingredients needed for the generated meal plan.
The format must match the style of a typical store shopping list (e.g., list items with approximate quantities).
Try to estimate the user's current inventory based on recent shopping trips, rather than assuming they need everything from scratch.

## Required Output Format
Your entire response must be structured exactly as follows, using Markdown headings:

### STORE
[Store Name from the Available Stores list, or "Unknown Store"]

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

    # Parse the response
    parsed_data = parse_gemini_response(response.text)

    return {
        "raw_response": response.text,
        "meals": parsed_data["meals"],
        "items": parsed_data["items"],
        "store_name": parsed_data["store_name"]
    }


def parse_gemini_response(response_text):
    """
    Parse the Gemini API response to extract store name, meal plan, and shopping list.

    Args:
        response_text (str): The raw markdown response from Gemini

    Returns:
        dict: Contains 'store_name' (str), 'meals' (list of dicts), and 'items' (list of dicts)
    """
    meals = []
    items = []
    store_name = None

    # Split response into sections
    lines = response_text.strip().split('\n')
    current_section = None

    for line in lines:
        line = line.strip()

        # Detect section headers
        if '### STORE' in line or '## STORE' in line:
            current_section = 'store'
            continue
        elif '### MEAL PLAN' in line or '## MEAL PLAN' in line:
            current_section = 'meals'
            continue
        elif '### SHOPPING LIST' in line or '## SHOPPING LIST' in line:
            current_section = 'items'
            continue

        # Parse store name
        if current_section == 'store' and line and not line.startswith('#'):
            store_name = line.strip()
            current_section = None  # Reset after reading store name
            continue

        # Parse meal plan items
        if current_section == 'meals' and line.startswith('- [ ]'):
            # Remove "- [ ]" prefix
            content = line.replace('- [ ]', '').strip()
            # Parse: Date, Type, Description
            match = re.match(r'(\d{4}-\d{2}-\d{2}),\s*([^,]+),\s*(.+)', content)
            if match:
                meals.append({
                    'date': match.group(1),
                    'type': match.group(2).strip(),
                    'summary': match.group(3).strip()
                })

        # Parse shopping list items
        elif current_section == 'items' and line.startswith('- [ ]'):
            # Remove "- [ ]" prefix
            content = line.replace('- [ ]', '').strip()
            # Parse: Name, Quantity
            match = re.match(r'([^,]+),\s*(\d+(?:\.\d+)?)', content)
            if match:
                items.append({
                    'name': match.group(1).strip(),
                    'quantity': float(match.group(2))
                })

    return {
        "store_name": store_name,
        "meals": meals,
        "items": items
    }


# Allow script to run standalone for testing
if __name__ == "__main__":
    print("Welcome to the Meal Planner and Shopping List Generator!")
    print("Please provide a prompt describing your upcoming shopping trip and meal preferences.")
    print("You should include detail such as the number of days, where you will be shopping, and any cravings.")
    print("***")
    user_request = input("Enter your prompt here: ")

    # Generate meal plan and list
    result = generate_meal_plan_and_list(user_request, user_id=1)

    # Print the results
    print("\nResponse\n---------------\n", result["raw_response"], "\n")
    print("\nParsed Meals:", result["meals"])
    print("\nParsed Items:", result["items"])
