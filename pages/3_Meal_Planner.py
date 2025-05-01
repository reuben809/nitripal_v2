import streamlit as st
from datetime import datetime, timedelta
from modules.auth import is_authenticated
from modules.db import Database
from utils.viz import create_weekly_calendar, create_nutrition_chart
from streamlit_lottie import st_lottie
import requests
import pandas as pd

# Set page configuration
st.set_page_config(
    page_title="NutriPal - Meal Planner",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Hide default sidebar navigation
no_sidebar_style = """
    <style>
        div[data-testid="stSidebarNav"] {display: none;}
    </style>
"""
st.markdown(no_sidebar_style, unsafe_allow_html=True)

# Check authentication
if not is_authenticated():
    st.warning("Please login to access this page")
    st.switch_page("pages/0_Login.py")

# Initialize database
@st.cache_resource
def init_database():
    return Database()

db = init_database()

# App title and description
st.title('🍎 :red[NutriPal] - Your AI-Powered Nutrition Coach')
st.subheader('Meal Planner')

# Load lottie animation for sidebar
def load_lottie_animation():
    url = "https://lottie.host/561e66a9-5d47-42c4-ae0a-53ae0f9b31dc/1YI1SYCjX5.json"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            st.sidebar.error('Error loading animation')
            return None
    except Exception as e:
        st.sidebar.error(f'Error: {e}')
        return None

# Display animation in sidebar
with st.sidebar:
    animation_data = load_lottie_animation()
    if animation_data:
        st_lottie(animation_data, speed=2, height=200, quality='high', width=190)
    
    # User info
    st.markdown(f"### Welcome, {st.session_state.username}!")
    st.markdown("---")
    
    # Navigation options
    if st.button("Home"):
        st.switch_page("app.py")
    
    if st.button("Recipe Generator"):
        st.switch_page("pages/1_Home.py")
    
    if st.button("Next Food Prediction"):
        st.switch_page("pages/2_Next_Food.py")
    
    if st.button("Community Recipes"):
        st.switch_page("pages/4_Community.py")
    
    if st.button("AI Nutritionist"):
        st.switch_page("pages/5_AI_Nutritionist.py")
    
    # Logout button
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()

# Main content
def meal_planner():
    # Weekly calendar view with meal planning
    st.markdown("## Weekly Meal Plan")
    
    # Date selection
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    
    # Get meals for the week
    end_date = (start_of_week + timedelta(days=6)).strftime('%Y-%m-%d')
    start_date = start_of_week.strftime('%Y-%m-%d')
    
    weekly_meals = db.get_meals_by_date_range(
        st.session_state.username,
        start_date,
        end_date
    )
    
    # Group meals by date
    meals_by_date = {}
    for meal in weekly_meals:
        date = meal.get('date')
        if date not in meals_by_date:
            meals_by_date[date] = []
        meals_by_date[date].append(meal)
    
    # Create calendar view
    create_weekly_calendar(meals_by_date, start_of_week)
    
    # Add new meal form
    st.markdown("---")
    st.markdown("## Add New Meal")
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_date = st.date_input("Date", today)
        meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
    
    with col2:
        meal_description = st.text_area("Meal Description", placeholder="Describe your meal here...")
        main_ingredients = st.text_input("Main Ingredients (comma separated)")
    
    # Process ingredients
    ingredients_list = [ingredient.strip() for ingredient in main_ingredients.split(',')] if main_ingredients else []
    
    # Add meal button
    if st.button("Add Meal"):
        success = db.log_meal(
            username=st.session_state.username,
            date=selected_date.strftime('%Y-%m-%d'),
            meal_type=meal_type.lower(),
            description=meal_description,
            ingredients=ingredients_list,
            nutrition={}  # Empty for now, nutrition would be calculated in a full implementation
        )
        
        if success:
            st.success(f"{meal_type} added successfully for {selected_date.strftime('%Y-%m-%d')}")
            # Rerun to update the calendar
            st.rerun()
        else:
            st.error("Failed to add meal")
    
    # Nutrition progress tracking
    st.markdown("---")
    st.markdown("## Nutrition Progress Tracking")
    
    # Get nutrition data for the past week
    nutrition_data = db.get_nutrition_history(st.session_state.username, days=7)
    
    if nutrition_data:
        # Create chart
        chart = create_nutrition_chart(nutrition_data)
        if chart:
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No nutrition data available for visualization")
    else:
        st.info("No nutrition data available. Start logging your meals to track your nutrition!")

# Run the main function
meal_planner()
