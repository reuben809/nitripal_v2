import streamlit as st
import os
from modules.auth import is_authenticated
from modules.db import Database
from streamlit_lottie import st_lottie
import requests
import time

# Set page configuration
st.set_page_config(
    page_title="NutriPal - Your AI-Powered Nutrition Coach",
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

# Initialize database connection
@st.cache_resource
def init_database():
    return Database()

db = init_database()

# Check authentication status
if not is_authenticated():
    st.switch_page("pages/Login.py")

# App title and description
st.title('🍎 :red[NutriPal] - Your AI-Powered Nutrition Coach')

# Load animation for sidebar
def load_lottie_animation():
    url = "https://lottie.host/3675d60a-37e0-4c26-8476-e662a4067e08/9juUlYZEnf.json"
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
    
    # User info and navigation
    st.markdown(f"### Welcome, {st.session_state.username}!")
    st.markdown("---")
    
    # Display user level and XP
    user_stats = db.get_user_stats(st.session_state.username)
    if user_stats:
        st.markdown(f"**Level**: {user_stats['level_name']}")
        
        # Create XP progress bar
        xp = user_stats['xp']
        next_level_xp = user_stats['next_level_xp']
        current_level_xp = user_stats['current_level_xp']
        if next_level_xp > current_level_xp:
            progress = (xp - current_level_xp) / (next_level_xp - current_level_xp)
        else:
            progress = 1.0
        
        st.progress(progress, text=f"XP: {xp}/{next_level_xp}")
    
    # Logout button
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()

# Main page content
st.markdown("""
Welcome to NutriPal, your AI-powered nutrition assistant! 

NutriPal helps you make informed decisions about your diet and wellness by providing:
- Personalized meal recommendations based on your health profile
- Nutrition analysis of your meals
- Meal planning and tracking
- Community recipe sharing
- AI-powered nutrition advice

Navigate through the pages in the sidebar to explore all features.
""")

# Quick access cards using columns
st.markdown("## Quick Access")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🍲 Generate Recipe")
    st.markdown("Create a personalized dish based on ingredients and health preferences")
    if st.button("Go to Recipe Generator"):
        st.switch_page("pages/1_Home.py")

with col2:
    st.markdown("### 📅 Meal Planner")
    st.markdown("Plan your meals for the week and track your nutrition")
    if st.button("Go to Meal Planner"):
        st.switch_page("pages/3_Meal_Planner.py")

with col3:
    st.markdown("### 💬 AI Nutritionist")
    st.markdown("Chat with our AI nutritionist for personalized advice")
    if st.button("Chat with AI"):
        st.switch_page("pages/5_AI_Nutritionist.py")

# Recent activity
st.markdown("## Recent Activity")
recent_meals = db.get_recent_meals(st.session_state.username, limit=3)

if recent_meals:
    for meal in recent_meals:
        with st.expander(f"{meal['date']} - {meal['meal_type']}"):
            st.markdown(meal['description'])
else:
    st.info("No recent meal activity. Start by logging your meals or generating recipes!")
