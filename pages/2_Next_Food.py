import streamlit as st
from modules.auth import is_authenticated
from modules.db import Database
from modules.recipes import predict_next_meal
from streamlit_lottie import st_lottie
import requests
import time

# Set page configuration
st.set_page_config(
    page_title="NutriPal - Next Meal Prediction",
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
    st.switch_page("pages/Login.py")

# Initialize database
@st.cache_resource
def init_database():
    return Database()

db = init_database()

# App title and description
st.title('🍎 :red[NutriPal] - Your AI-Powered Nutrition Coach')
st.subheader('Next Meal Prediction')

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
    
    if st.button("Meal Planner"):
        st.switch_page("pages/3_Meal_Planner.py")
    
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
def next_meal_prediction():
    st.markdown("""
    ### Next Meal Prediction
    
    This feature analyzes your eating patterns and suggests what you might want to eat next.
    Let's start by recording your recent food intake.
    """)
    
    # Food intake recording section
    st.markdown("### Log Today's Food Intake")
    st.info('Better to enter food items in order of consumption. Eg: Breakfast, Lunch, Snacks, Dinner')
    
    eating_habits = st.text_area(
        'What did you eat today?',
        help="List all the foods you've consumed today"
    )
    
    # Save food intake to database
    if eating_habits and st.button("Save Food Intake"):
        success = db.update_user_food_history(st.session_state.username, eating_habits)
        if success:
            st.success('Your food intake has been recorded successfully!')
        else:
            st.error('Failed to record food intake. Please try again.')
    
    st.markdown("---")
    
    # Next meal prediction section
    st.markdown("### Get Next Meal Prediction")
    
    predict_button = st.button('Predict My Next Meal')
    
    if predict_button:
        if 'apikey' not in st.session_state or not st.session_state['apikey']:
            st.error("Please enter your HuggingFace API key to use this feature")
            return
        
        # Get user's food history
        user = db.get_user(st.session_state.username)
        food_history = user.get("food_history", "")
        
        if not food_history:
            st.warning("You don't have enough food history. Please log your meals first.")
            return
        
        with st.spinner("Analyzing your food patterns..."):
            prediction = predict_next_meal(food_history)
        
        st.markdown("### Predicted Next Meal")
        st.markdown(prediction)
        
        # Option to add predicted meal to meal planner
        add_to_planner = st.checkbox("Add this prediction to my meal planner")
        
        if add_to_planner:
            meal_types = ["Breakfast", "Lunch", "Dinner", "Snack"]
            selected_meal_type = st.selectbox("Select meal type", meal_types)
            
            if st.button("Add to Meal Planner"):
                success = db.log_meal(
                    username=st.session_state.username,
                    date=time.strftime('%Y-%m-%d'),
                    meal_type=selected_meal_type.lower(),
                    description=prediction,
                    ingredients=[],
                    nutrition={}
                )
                
                if success:
                    st.success(f"Added to meal planner as {selected_meal_type}")
                else:
                    st.error("Failed to add to meal planner")
    
    # Display recent food history
    st.markdown("### Your Recent Food History")
    user = db.get_user(st.session_state.username)
    food_history = user.get("food_history", "No food history recorded yet.")
    
    with st.expander("View Food History", expanded=False):
        st.markdown(food_history)

# Run the main function
next_meal_prediction()
