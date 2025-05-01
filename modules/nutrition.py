import streamlit as st
from datetime import datetime, timedelta
from modules.db import Database
from modules.recipes import parse_nutrition_values
import time

def log_meal_with_nutrition(username, meal_type, description, nutrition_text=None, ingredients=None):
    """
    Log a meal with nutrition information to the database
    
    Args:
        username: Username of the user
        meal_type: Type of meal (breakfast, lunch, dinner, snack)
        description: Description of the meal
        nutrition_text: Optional nutrition text to parse
        ingredients: Optional list of ingredients
        
    Returns:
        Boolean indicating success of operation
    """
    db = Database()
    
    # Get today's date
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Parse nutrition values if available
    nutrition = {}
    if nutrition_text:
        nutrition = parse_nutrition_values(nutrition_text)
    
    # Log meal to database
    success = db.log_meal(
        username=username,
        date=today,
        meal_type=meal_type,
        description=description,
        ingredients=ingredients,
        nutrition=nutrition
    )
    
    return success

def get_weekly_nutrition_data(username):
    """
    Get weekly nutrition data for visualization
    
    Args:
        username: Username of the user
        
    Returns:
        List of nutrition data points by date
    """
    db = Database()
    
    # Get data for last 7 days
    nutrition_history = db.get_nutrition_history(username, days=7)
    
    return nutrition_history

def calculate_daily_targets(user_data):
    """
    Calculate daily nutrition targets based on user profile
    
    Args:
        user_data: User profile data
        
    Returns:
        Dictionary with daily targets
    """
    # Default values
    targets = {
        "calories": 2000,
        "protein": 50,
        "carbs": 250,
        "fat": 70
    }
    
    # TODO: Implement personalized target calculation based on user data
    # This would involve considering factors like:
    # - Weight, height, age, gender
    # - Activity level
    # - Health goals (weight loss, maintenance, muscle gain)
    # - Health conditions
    
    return targets

def analyze_meal_pattern(username):
    """
    Analyze meal pattern for the user
    
    Args:
        username: Username of the user
        
    Returns:
        Analysis of meal patterns
    """
    db = Database()
    
    # Get recent meals
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
    meals = db.get_meals_by_date_range(username, start_date, end_date)
    
    # Count meal types
    meal_types_count = {
        "breakfast": 0,
        "lunch": 0,
        "dinner": 0,
        "snack": 0
    }
    
    for meal in meals:
        meal_type = meal.get("meal_type", "").lower()
        if meal_type in meal_types_count:
            meal_types_count[meal_type] += 1
    
    # Calculate regularity score (percentage of days with all main meals)
    days_analyzed = (datetime.now() - datetime.strptime(start_date, '%Y-%m-%d')).days + 1
    
    # Group meals by date
    meals_by_date = {}
    for meal in meals:
        date = meal.get("date")
        meal_type = meal.get("meal_type", "").lower()
        
        if date not in meals_by_date:
            meals_by_date[date] = set()
        
        if meal_type in ["breakfast", "lunch", "dinner"]:
            meals_by_date[date].add(meal_type)
    
    # Count days with all main meals
    days_with_all_meals = 0
    for date, meal_types in meals_by_date.items():
        if len(meal_types) == 3:  # breakfast, lunch, dinner
            days_with_all_meals += 1
    
    regularity_score = (days_with_all_meals / days_analyzed) * 100 if days_analyzed > 0 else 0
    
    return {
        "meal_types_count": meal_types_count,
        "days_analyzed": days_analyzed,
        "regularity_score": regularity_score
    }

def track_health_metrics(username, metrics):
    """
    Track health metrics over time
    
    Args:
        username: Username of the user
        metrics: Dictionary with health metrics (weight, blood pressure, etc.)
        
    Returns:
        Boolean indicating success
    """
    db = Database()
    
    # Create metrics document
    metrics_data = {
        "username": username,
        "date": datetime.now().strftime('%Y-%m-%d'),
        "metrics": metrics,
        "created_at": time.time()
    }
    
    # Insert into analytics collection
    try:
        result = db.analytics.insert_one(metrics_data)
        return result.acknowledged
    except Exception as e:
        st.error(f"Error tracking health metrics: {e}")
        return False
