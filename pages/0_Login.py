import streamlit as st
from modules.auth import register_user, login_user
from streamlit_lottie import st_lottie
import requests
import time

# Set page configuration
st.set_page_config(
    page_title="NutriPal - Login",
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

# Load lottie animation
def load_lottie_animation():
    url = "https://lottie.host/3675d60a-37e0-4c26-8476-e662a4067e08/9juUlYZEnf.json"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            st.error('Error loading animation')
            return None
    except Exception as e:
        st.error(f'Error: {e}')
        return None

# App title
st.title('🍎 :red[NutriPal] - Your AI-Powered Nutrition Coach')

# Create two columns for login/signup and animation
col1, col2 = st.columns([3, 2])

with col2:
    # Display animation
    animation_data = load_lottie_animation()
    if animation_data:
        st_lottie(animation_data, speed=2, height=300, quality='high')

with col1:
    # HuggingFace API key field
    api_key = st.text_input("Enter your HuggingFace API key", type="password", 
                            help="This is required for AI features. Get a free key at huggingface.co")
    if api_key:
        st.session_state['apikey'] = api_key

    # Tabs for login and signup
    login_tab, signup_tab = st.tabs(["Login", "Signup"])
    
    with login_tab:
        st.header("Login")
        
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login"):
            if not username or not password:
                st.error("Please fill in all fields")
            else:
                with st.spinner("Logging in..."):
                    success, message = login_user(username, password)
                    
                if success:
                    st.success(message)
                    if api_key:
                        st.session_state['apikey'] = api_key
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(message)
    
    with signup_tab:
        st.header("Sign Up")
        
        email = st.text_input("Email", key="signup_email")
        username = st.text_input("Username", key="signup_username")
        password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")
        
        if st.button("Sign Up"):
            if not email or not username or not password or not confirm_password:
                st.error("Please fill in all fields")
            elif password != confirm_password:
                st.error("Passwords do not match")
            else:
                with st.spinner("Creating account..."):
                    success, message = register_user(username, password, email)
                    
                if success:
                    st.success(message)
                    st.info("Please login with your new account")
                else:
                    st.error(message)

# Display additional information about NutriPal
st.markdown("---")
st.markdown("""
### About NutriPal

NutriPal is an AI-powered nutrition coach designed to help you make informed decisions about your diet and wellness. 
It provides personalized recommendations based on your health profile and dietary preferences.

#### Features:
- Image-based ingredient detection
- Personalized recipe recommendations
- Health profile integration
- Environmental footprint considerations
- Meal planning and tracking
- Community recipe sharing
- AI nutritionist chat

Get started by creating an account or logging in!
""")
