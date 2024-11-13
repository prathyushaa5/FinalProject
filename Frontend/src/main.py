from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

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
data = pd.read_csv("food.csv")

# Data preprocessing
data['VegNonVeg'] = pd.to_numeric(data['VegNonVeg'], errors='coerce')  
data = data.dropna(subset=['VegNonVeg']) 
data['VegNonVeg'] = data['VegNonVeg'].astype(int) 

# Function to calculate food suggestions based on diet type and weight goal
def calculate_food_suggestions(diet_type: int, weight_goal: str):
    filtered_data = data[data['VegNonVeg'] == diet_type]

    # Filter based on weight goal
    if weight_goal == "gain":
        filtered_data = filtered_data[filtered_data['Calories'] >= 300]  
    elif weight_goal == "lose":
        filtered_data = filtered_data[filtered_data['Calories'] <= 200] 
    elif weight_goal == "healthy":
        filtered_data = filtered_data[(filtered_data['Calories'] >= 200) & (filtered_data['Calories'] <= 300)]

    # Calculate priority score
    filtered_data["PriorityScore"] = filtered_data['Calories'] * 0.5 + filtered_data['Proteins'] * 0.3

    # Get top recommendations
    breakfast_recommendations = filtered_data[filtered_data['Breakfast'] == 1].nlargest(3, 'PriorityScore')
    lunch_recommendations = filtered_data[filtered_data['Lunch'] == 1].nlargest(3, 'PriorityScore')
    dinner_recommendations = filtered_data[filtered_data['Dinner'] == 1].nlargest(3, 'PriorityScore')

    return {
        "breakfast": breakfast_recommendations[['Food_items', 'Calories', 'Proteins', 'Fats', 'Carbohydrates']].to_dict(orient='records'),
        "lunch": lunch_recommendations[['Food_items', 'Calories', 'Proteins', 'Fats', 'Carbohydrates']].to_dict(orient='records'),
        "dinner": dinner_recommendations[['Food_items', 'Calories', 'Proteins', 'Fats', 'Carbohydrates']].to_dict(orient='records')
    }

@app.get("/get_diet_plan/")
def get_diet_plan(diet_type: int, weight_goal: str):
    suggestions = calculate_food_suggestions(diet_type, weight_goal)
    return {
        "diet_type": "Vegetarian" if diet_type == 0 else "Non-Vegetarian",
        "weight_goal": weight_goal,
        "suggestions": suggestions
    }

# To run the app: uvicorn main:app --reload
