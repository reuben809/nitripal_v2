import streamlit as st
import time
from utils.navigation import standard_sidebar
from modules.auth import is_authenticated
from modules.db import Database
from config import Settings

# Set page configuration
st.set_page_config(
    page_title="NutriPal - Your AI-Powered Nutrition Coach",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize standard sidebar
standard_sidebar()


def main():
    # Check authentication
    if not is_authenticated():
        st.switch_page("pages/0_Login.py")

    # Initialize database connection
    @st.cache_resource
    def init_database():
        return Database()

    db = init_database()

    # Main page content
    st.title('🍎 :red[NutriPal] - Your AI-Powered Nutrition Coach')

    # Welcome section
    st.markdown(f"""
    Welcome to NutriPal, your AI-powered nutrition assistant! 

    **Logged in as:** {st.session_state.username}

    NutriPal helps you make informed decisions about your diet and wellness by providing:
    - Personalized meal recommendations based on your health profile
    - Nutrition analysis of your meals
    - Meal planning and tracking
    - Community recipe sharing
    - AI-powered nutrition advice
    """)

    # User stats section
    user_stats = db.get_user_stats(st.session_state.user_id)
    if user_stats:
        st.markdown("### Your Progress")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Current Level:** {user_stats['level_name']}")
            st.markdown(f"**Total XP:** {user_stats['xp']}")

        # XP progress bar
        with col2:
            progress = ((user_stats['xp'] - user_stats['current_level_xp']) /
                        (user_stats['next_level_xp'] - user_stats['current_level_xp']))
            st.progress(progress, text=f"Progress to Next Level: {progress * 100:.1f}%")

    # Quick actions
    st.markdown("## Quick Actions")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🍲 Generate Recipe")
        st.markdown("Create personalized recipes from ingredients")
        if st.button("Start Cooking", key="recipe_gen"):
            st.switch_page("pages/1_Home.py")

    with col2:
        st.markdown("### 📅 Meal Planner")
        st.markdown("Plan your weekly meals")
        if st.button("Plan Meals", key="meal_plan"):
            st.switch_page("pages/3_Meal_Planner.py")

    with col3:
        st.markdown("### 💬 AI Nutritionist")
        st.markdown("Get personalized nutrition advice")
        if st.button("Chat Now", key="ai_chat"):
            st.switch_page("pages/5_AI_Nutritionist.py")

    # Recent activity
    st.markdown("## Recent Activity")
    recent_meals = db.get_recent_meals(st.session_state.user_id, limit=3)

    if recent_meals:
        for meal in recent_meals:
            with st.expander(f"{meal['date']} - {meal['meal_type'].capitalize()}"):
                st.markdown(f"**Description:** {meal['description']}")
                if meal['ingredients']:
                    st.markdown("**Ingredients:**")
                    st.write(", ".join(meal['ingredients']))
    else:
        st.info("No recent meals logged. Start by generating a recipe or planning meals!")


if __name__ == "__main__":
    main()