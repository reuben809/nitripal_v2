import streamlit as st
from modules.auth import is_authenticated
from modules.db import Database
from streamlit_lottie import st_lottie
import requests
import time

# Set page configuration
st.set_page_config(
    page_title="NutriPal - Community Recipes",
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
st.subheader('Community Recipes')

# Load lottie animation for sidebar
def load_lottie_animation():
    url = "https://lottie.host/d6fdfdb9-44d5-45de-bc54-9c92bc8f628f/J3YHSrJGMT.json"
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
    
    if st.button("Meal Planner"):
        st.switch_page("pages/3_Meal_Planner.py")
    
    if st.button("AI Nutritionist"):
        st.switch_page("pages/5_AI_Nutritionist.py")
    
    # Logout button
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()

# Main content
def community_recipes():
    # Tabs for browsing and submitting recipes
    browse_tab, submit_tab = st.tabs(["Browse Recipes", "Submit Recipe"])
    
    with browse_tab:
        st.markdown("## Browse Community Recipes")
        
        # Filters
        st.markdown("### Filters")
        col1, col2 = st.columns(2)
        
        with col1:
            # Filter by tags
            all_tags = ["Vegetarian", "Vegan", "Gluten-Free", "Low-Carb", "High-Protein", 
                        "Dairy-Free", "Nut-Free", "Keto", "Paleo", "Low Water Footprint"]
            selected_tags = st.multiselect("Filter by Tags", all_tags)
        
        with col2:
            # Sort options
            sort_option = st.selectbox("Sort by", ["Newest First", "Most Popular"])
        
        # Display recipes
        st.markdown("### Recipes")
        
        # Get recipes from database
        recipes = db.get_community_recipes(tags=selected_tags if selected_tags else None)
        
        if not recipes:
            st.info("No recipes found. Be the first to share a recipe!")
        else:
            for recipe in recipes:
                with st.expander(f"{recipe.get('title', 'Untitled Recipe')} by {recipe.get('username', 'Unknown')}"):
                    # Display tags
                    tags = recipe.get('tags', [])
                    if tags:
                        st.markdown(f"**Tags:** {', '.join(tags)}")
                    
                    # Display recipe
                    st.markdown(recipe.get('description', 'No description available.'))
                    
                    # Display eco-friendly and health-focused badges
                    badges_col1, badges_col2 = st.columns(2)
                    
                    if recipe.get('eco_friendly', False):
                        badges_col1.success("Eco-Friendly Recipe")
                    
                    if recipe.get('health_focused', True):
                        badges_col2.info("Health-Focused Recipe")
                    
                    # Add to my meal planner button
                    if st.button(f"Add to Meal Planner", key=f"add_{recipe['_id']}"):
                        meal_types = ["Breakfast", "Lunch", "Dinner", "Snack"]
                        meal_type = st.selectbox("Select meal type", meal_types, key=f"meal_type_{recipe['_id']}")
                        
                        if st.button("Confirm", key=f"confirm_{recipe['_id']}"):
                            success = db.log_meal(
                                username=st.session_state.username,
                                date=time.strftime('%Y-%m-%d'),
                                meal_type=meal_type.lower(),
                                description=recipe.get('description', ''),
                                ingredients=recipe.get('ingredients', []),
                                nutrition={}
                            )
                            
                            if success:
                                st.success(f"Added to meal planner as {meal_type}")
                            else:
                                st.error("Failed to add to meal planner")
    
    with submit_tab:
        st.markdown("## Share Your Recipe")
        
        # Recipe submission form
        recipe_title = st.text_input("Recipe Title")
        recipe_description = st.text_area("Recipe Description", height=300,
                                         placeholder="Share your complete recipe including ingredients and instructions...")
        recipe_tags = st.multiselect("Tags", 
                                    ["Vegetarian", "Vegan", "Gluten-Free", "Low-Carb", "High-Protein", 
                                     "Dairy-Free", "Nut-Free", "Keto", "Paleo", "Low Water Footprint"])
        
        eco_friendly = st.checkbox("This recipe has a low water footprint")
        health_focused = st.checkbox("This recipe is health-focused", value=True)
        
        # Main ingredients (for search indexing)
        main_ingredients = st.text_input("Main Ingredients (comma separated)",
                                       help="These will help others find your recipe")
        
        ingredients_list = [ingredient.strip() for ingredient in main_ingredients.split(',')] if main_ingredients else []
        
        # Submit button
        if st.button("Share Recipe"):
            if not recipe_title or not recipe_description:
                st.error("Please provide a title and description for your recipe")
            else:
                recipe_data = {
                    "username": st.session_state.username,
                    "title": recipe_title,
                    "description": recipe_description,
                    "tags": recipe_tags,
                    "ingredients": ingredients_list,
                    "eco_friendly": eco_friendly,
                    "health_focused": health_focused
                }
                
                success = db.add_community_recipe(recipe_data)
                
                if success:
                    st.success("Recipe shared successfully!")
                    st.info("Your recipe is now available for the community to enjoy!")
                else:
                    st.error("Failed to share recipe. Please try again.")

# Run the main function
community_recipes()
