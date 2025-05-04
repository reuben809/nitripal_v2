import streamlit as st
from streamlit_lottie import st_lottie
import requests


def standard_sidebar(username=None):
    """Create consistent sidebar across all pages"""
    with st.sidebar:
        # Animation
        url = "https://lottie.host/3675d60a-37e0-4c26-8476-e662a4067e08/9juUlYZEnf.json"
        animation = load_lottie_animation(url)
        if animation:
            st_lottie(animation, speed=2, height=200, quality='high', width=190)

        # Navigation
        if username:
            st.markdown(f"### Welcome, {username}!")
            st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🏠 Home"):
                st.switch_page("app.py")
            if st.button("📝 Meal Planner"):
                st.switch_page("pages/3_Meal_Planner.py")
        with col2:
            if st.button("🤖 AI Nutritionist"):
                st.switch_page("pages/5_AI_Nutritionist.py")
            if st.button("📊 Progress"):
                st.switch_page("pages/4_Community.py")

        st.markdown("---")
        if st.button("🚪 Logout"):
            st.session_state.clear()
            st.rerun()


def load_lottie_animation(url):
    """Helper function to load Lottie animations"""
    try:
        response = requests.get(url)
        return response.json() if response.status_code == 200 else None
    except Exception:
        return None