from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from typing import List, Optional

app = FastAPI()

# Define the origins that are allowed to access the API
origins = [
    "http://localhost:8080",  # Update this to match your frontend server
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# Load your data
data = pd.read_csv("filtered_meals.csv")

# Data preprocessing
# Convert categorical columns (Veg/Non-Veg and other) to numeric or keep them as they are if necessary
data['Type'] = data['Type'].apply(lambda x: 0 if x.lower() == 'veg' else 1)  # 0 for Veg, 1 for Non-Veg

# Function to calculate food suggestions based on diet type, weight goal, state, and allergens
def calculate_food_suggestions(diet_type: int, weight_goal: str, state: str, food_type: str, exclude_allergens: List[str]):
    filtered_data = data[data['Type'] == diet_type]  # Filter by diet type (Veg/Non-Veg)

    # Filter based on weight goal
    if weight_goal == "gain":
        filtered_data = filtered_data[filtered_data['Total Calories'] >= 300]
    elif weight_goal == "lose":
        filtered_data = filtered_data[filtered_data['Total Calories'] <= 200]
    elif weight_goal == "healthy":
        filtered_data = filtered_data[(filtered_data['Total Calories'] >= 200) & (filtered_data['Total Calories'] <= 300)]

    # Filter by state (optional)
    if state != "all":
        filtered_data = filtered_data[filtered_data['State'] == state]

    # Filter by food type (optional)
    if food_type != "all":
        filtered_data = filtered_data[filtered_data['Type'] == food_type]

    # Exclude foods with allergic ingredients
    for allergen in exclude_allergens:
        filtered_data = filtered_data[~filtered_data['Allergic Ingredients'].str.contains(allergen, na=False)]

    # Sort by priority (based on Calories and Protein)
    filtered_data["PriorityScore"] = filtered_data['Total Calories'] * 0.5 + filtered_data['Total Protein'] * 0.3

    # Get top recommendations (e.g., top 3)
    breakfast_recommendations = filtered_data.nlargest(3, 'PriorityScore')
    lunch_recommendations = filtered_data.nlargest(3, 'PriorityScore')
    dinner_recommendations = filtered_data.nlargest(3, 'PriorityScore')

    return {
        "breakfast": breakfast_recommendations[[
            'Food Name', 'Total Calories', 'Total Carbs', 'Total Fats', 'Total Protein', 'Total Sugar', 'Total Sodium', 'Vitamin Content'
        ]].to_dict(orient='records'),
        "lunch": lunch_recommendations[[
            'Food Name', 'Total Calories', 'Total Carbs', 'Total Fats', 'Total Protein', 'Total Sugar', 'Total Sodium', 'Vitamin Content'
        ]].to_dict(orient='records'),
        "dinner": dinner_recommendations[[
            'Food Name', 'Total Calories', 'Total Carbs', 'Total Fats', 'Total Protein', 'Total Sugar', 'Total Sodium', 'Vitamin Content'
        ]].to_dict(orient='records')
    }

@app.get("/get_diet_plan/")
def get_diet_plan(
    diet_type: int, 
    weight_goal: str, 
    state: str = "all", 
    food_type: str = "all", 
    exclude_allergens: Optional[List[str]] = []
):
    suggestions = calculate_food_suggestions(diet_type, weight_goal, state, food_type, exclude_allergens)
    return {
        "diet_type": "Vegetarian" if diet_type == 0 else "Non-Vegetarian",
        "weight_goal": weight_goal,
        "suggestions": suggestions
    }

# To run the app: uvicorn main:app --reload
