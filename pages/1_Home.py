import streamlit as st
import base64
from modules.auth import is_authenticated
from modules.db import Database
from modules.models import classify_food_image
from modules.recipes import generate_dish_from_image, get_nutrition_info
from streamlit_lottie import st_lottie
import requests
import time

# Set page configuration
st.set_page_config(
    page_title="NutriPal - Recipe Generator",
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
st.subheader('Recipe Generator')

# Load lottie animation for sidebar
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
    
    # User info
    st.markdown(f"### Welcome, {st.session_state.username}!")
    st.markdown("---")
    
    # Navigation options
    if st.button("Home"):
        st.switch_page("app.py")
    
    if st.button("Next Food Prediction"):
        st.switch_page("pages/2_Next_Food.py")
    
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

# Main functionality
def main_recipe_generator():
    # Image upload section
    st.markdown("### Upload Food Image")
    img = st.file_uploader('Upload a food image', type=['jpg', 'jpeg', 'png'])
    toggle = st.toggle('Proceed without image')
    
    # Store detected ingredients
    ingredients = []
    detected_ingredients_str = ""
    
    # Process uploaded image
    if img is not None or toggle:
        if img is not None:
            img_data = img.read()
            base64_encoded_img = base64.b64encode(img_data).decode("utf-8")
            st.image(img_data, width=400)
            
            with st.spinner("Analyzing image..."):
                img_classification = classify_food_image(base64_encoded_img)
            
            # Display detected ingredients
            st.markdown(f"<h4 style='text-align: center; color:#15db4d'><b>Ingredients Found</b></h4>", unsafe_allow_html=True)
            
            for i, ing in enumerate(img_classification, 1):
                st.text(f"{i}- {ing['label']}")
                ingredients.append(ing['label'])
            
            detected_ingredients_str = ', '.join(ingredients)
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Health preferences section
        st.markdown("### Health & Diet Preferences")
        user_health = st.text_area(
            "Tell us about any health concerns or dietary preferences",
            placeholder="I am experiencing mild fever, sinus issues, and difficulty sleeping.",
            help="This information helps us tailor the recipe to your specific health needs"
        )
        
        kitchen_ingredients = st.text_area(
            'Additional ingredients available in your kitchen',
            placeholder="In my kitchen, I have ripe tomatoes, fresh basil, garlic cloves, olive oil, chicken breast",
            help="List any additional ingredients you'd like to use in your recipe"
        )
        
        # Environmental preferences
        st.markdown("### Environmental Considerations")
        water_footprint = st.checkbox("Reduce Water Footprint", 
                                     help="Prioritize ingredients with lower water usage in their production")
        
        eco_info = st.expander("What is Water Footprint?", expanded=water_footprint)
        eco_info.write("The water footprint of a product is the volume of freshwater used to produce the product, measured at the place where the product was actually produced. It refers to the sum of water used in the various steps of the production chain.")
        
        ignore_health = st.checkbox("Prioritize Environmental Impact Over Health Considerations", 
                                   help="Focus solely on environmental impact, even if it means ignoring some health considerations")
        
        # Generate dish button
        col1, col2, col3 = st.columns(3)
        with col2:
            dish_button = st.button('Generate Dish')
        
        # Generate and display recipe
        if dish_button:
            if 'apikey' not in st.session_state or not st.session_state['apikey']:
                st.error("Please enter your HuggingFace API key to generate recipes")
                return
            
            # Update user health history if provided
            if user_health:
                db.update_user_health_history(st.session_state.username, user_health)
            
            # Get user health history
            user = db.get_user(st.session_state.username)
            health_history = user.get("health_history", "")
            
            with st.spinner("Creating your personalized recipe..."):
                # Generate recipe
                recipe = generate_dish_from_image(
                    img_data if img is not None else None,
                    health_history,
                    kitchen_ingredients,
                    water_footprint,
                    ignore_health
                )
                
                # Store in session state for nutrition page
                st.session_state['recipe'] = recipe
                
                # Update food history with ingredients
                ingredients_to_log = detected_ingredients_str
                if kitchen_ingredients:
                    ingredients_to_log += (", " if ingredients_to_log else "") + kitchen_ingredients
                
                if ingredients_to_log:
                    db.update_user_food_history(st.session_state.username, ingredients_to_log)
            
            # Display recipe
            st.markdown("## Your Personalized Recipe")
            st.markdown(recipe, unsafe_allow_html=True)
            
            # Get nutrition information
            if st.button("Get Nutrition Information"):
                with st.spinner("Analyzing nutritional content..."):
                    nutrition_info = get_nutrition_info(recipe)
                
                st.markdown("## Nutritional Information")
                st.markdown(nutrition_info, unsafe_allow_html=True)
                
                # Save recipe to database
                from utils.food_analysis import parse_ingredients_from_recipe
                ingredients_list = parse_ingredients_from_recipe(recipe)
                
                # Log meal
                db.log_meal(
                    username=st.session_state.username,
                    date=time.strftime('%Y-%m-%d'),
                    meal_type="recipe",
                    description=recipe,
                    ingredients=ingredients_list,
                    nutrition={}  # Would be parsed from nutrition_info in a full implementation
                )
                
                # Add to community (if user wants)
                share_recipe = st.checkbox("Share this recipe with the community")
                if share_recipe:
                    recipe_name = st.text_input("Give your recipe a name")
                    recipe_tags = st.text_input("Add tags (comma separated)")
                    
                    if st.button("Share Recipe"):
                        tags = [tag.strip() for tag in recipe_tags.split(',')] if recipe_tags else []
                        
                        recipe_data = {
                            "username": st.session_state.username,
                            "title": recipe_name or "Untitled Recipe",
                            "description": recipe,
                            "tags": tags,
                            "ingredients": ingredients_list,
                            "eco_friendly": water_footprint,
                            "health_focused": not ignore_health
                        }
                        
                        success = db.add_community_recipe(recipe_data)
                        if success:
                            st.success("Recipe shared successfully!")
                        else:
                            st.error("Failed to share recipe")

# Run the main function
main_recipe_generator()
