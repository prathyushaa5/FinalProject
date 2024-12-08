import os
import pandas as pd
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Create the FastAPI app instance
app = FastAPI()

# Define the origins that are allowed to access the API
origins = [
    "http://localhost:8080",  # Update this to match your frontend server
    "http://127.0.0.1:8080",
]

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# Function to load the data from the CSV file
def load_data():
    try:
        file_path = "food.csv"
        
        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Load the CSV data, skipping bad lines
        data = pd.read_csv(file_path, on_bad_lines='skip')
        
        # Ensure the required columns exist
        required_columns = [
            'Food Name', 'State', 'Type', 'Allergic Ingredients', 'Total Calories', 
            'Total Carbs', 'Total Fats', 'Total Protein', 'Total Sugar', 
            'Total Sodium', 'Vitamin Content'
        ]
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(f"Missing columns in CSV file: {', '.join(missing_columns)}")
        
        return data

    except FileNotFoundError as fnf_error:
        print(fnf_error)
        return None
    except ValueError as ve_error:
        print(ve_error)
        return None
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


# Load your data (Make sure the 'food.csv' file is present in the same directory as this script)
data = load_data()

# Data preprocessing (make sure the data is loaded before proceeding)
if data is not None:
    # Preprocess and clean data
    data['Type'] = data['Type'].apply(lambda x: 0 if x.lower() == 'veg' else 1)  # 0 for Veg, 1 for Non-Veg
    data['Allergic Ingredients'] = data['Allergic Ingredients'].fillna("None")  # Handle missing allergic ingredients

# Function to calculate food suggestions based on diet type, weight goal, and state
def calculate_food_suggestions(state: str, diet_type: int, weight_goal: str):
    if data is None:
        return {"error": "Failed to load data."}

    # Filter data by state
    filtered_data = data[data['State'].str.contains(state, case=False, na=False)]
    
    # Filter data by diet type (0 for Vegetarian, 1 for Non-Vegetarian)
    filtered_data = filtered_data[filtered_data['Type'] == diet_type]

    # Filter based on weight goal
    if weight_goal == "gain":
        filtered_data = filtered_data[filtered_data['Total Calories'] >= 300]
    elif weight_goal == "lose":
        filtered_data = filtered_data[filtered_data['Total Calories'] <= 200]
    elif weight_goal == "healthy":
        filtered_data = filtered_data[(filtered_data['Total Calories'] >= 200) & (filtered_data['Total Calories'] <= 300)]

    # Remove duplicates based on 'Food Name'
    filtered_data = filtered_data.drop_duplicates(subset=['Food Name'])

    # Calculate priority score based on calories and protein content
    filtered_data["PriorityScore"] = filtered_data['Total Calories'] * 0.5 + filtered_data['Total Protein'] * 0.3

    # Ensure PriorityScore is numeric
    filtered_data["PriorityScore"] = pd.to_numeric(filtered_data["PriorityScore"], errors='coerce')

    # Drop rows where PriorityScore is NaN after conversion
    filtered_data = filtered_data.dropna(subset=["PriorityScore"])

    # Shuffle the data to randomize suggestions each time
    filtered_data = filtered_data.sample(frac=1).reset_index(drop=True)

    # Get top 5 recommendations for meals
    recommendations = filtered_data.nlargest(5, 'PriorityScore')

    # Return the suggestions with main ingredients included
    return recommendations[['Food Name', 'Total Calories', 'Total Protein', 'Total Fats', 'Total Carbs', 'Total Sodium', 'Vitamin Content']].to_dict(orient='records')


# API endpoint to get diet plan
@app.get("/get_diet_plan/")
def get_diet_plan(state: str, diet_type: int, weight_goal: str):
    suggestions = calculate_food_suggestions(state, diet_type, weight_goal)
    if "error" in suggestions:
        return {"error": suggestions["error"]}
    return {
        "state": state,
        "diet_type": "Vegetarian" if diet_type == 0 else "Non-Vegetarian",
        "weight_goal": weight_goal,
        "suggestions": suggestions
    }
