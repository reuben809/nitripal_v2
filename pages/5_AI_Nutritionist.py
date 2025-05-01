import streamlit as st
from modules.auth import is_authenticated
from modules.db import Database
from modules.models import generate_text
from streamlit_lottie import st_lottie
import requests
import time

# Set page configuration
st.set_page_config(
    page_title="NutriPal - AI Nutritionist",
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
st.subheader('AI Nutritionist Chat')

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
    
    if st.button("Community Recipes"):
        st.switch_page("pages/4_Community.py")
    
    # Logout button
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Main content
def ai_nutritionist_chat():
    st.markdown("""
    ### Chat with AI Nutritionist
    
    Ask any nutrition or diet-related questions, get meal ideas, or discuss your health goals.
    Our AI nutritionist has access to your health history and food preferences to provide personalized advice.
    """)
    
    # Check for API key
    if 'apikey' not in st.session_state or not st.session_state['apikey']:
        st.error("Please enter your HuggingFace API key to use this feature")
        return
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"<div style='background-color:#e6f7ff;padding:10px;border-radius:5px;margin-bottom:10px'><strong>You:</strong> {message['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background-color:#f0f0f0;padding:10px;border-radius:5px;margin-bottom:10px'><strong>AI Nutritionist:</strong> {message['content']}</div>", unsafe_allow_html=True)
    
    # User input
    user_question = st.text_input("Ask a question about nutrition, health, or diet")
    
    # Process user input
    if user_question and st.button("Send"):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        
        # Get user context
        user = db.get_user(st.session_state.username)
        health_history = user.get("health_history", "")
        food_history = user.get("food_history", "")
        
        # Create context-aware prompt
        system_context = f"""
        You are a nutritionist AI assistant helping a user with their nutrition and health questions.
        
        User's health history: {health_history}
        
        User's food history: {food_history}
        
        Answer the user's question based on their history and provide personalized advice.
        Be friendly, helpful, and informative. If their question requires medical expertise beyond nutrition,
        advise them to consult with a healthcare professional.
        """
        
        prompt = f"{system_context}\n\nUser question: {user_question}\n\nResponse:"
        
        with st.spinner("Thinking..."):
            response = generate_text(prompt)
        
        # Add AI response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # Rerun to update the chat display
        st.rerun()
    
    # Option to clear chat history
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()
    
    # Suggested questions
    st.markdown("### Suggested Questions")
    suggested_questions = [
        "What foods can help me reduce inflammation?",
        "Can you suggest a high-protein breakfast?",
        "How can I maintain my energy levels throughout the day?",
        "What's a good meal plan for weight loss?",
        "How can I increase my fiber intake?"
    ]
    
    for question in suggested_questions:
        if st.button(question, key=f"suggested_{question}"):
            # Add question to chat history and process
            st.session_state.chat_history.append({"role": "user", "content": question})
            
            # Get user context
            user = db.get_user(st.session_state.username)
            health_history = user.get("health_history", "")
            food_history = user.get("food_history", "")
            
            # Create context-aware prompt
            system_context = f"""
            You are a nutritionist AI assistant helping a user with their nutrition and health questions.
            
            User's health history: {health_history}
            
            User's food history: {food_history}
            
            Answer the user's question based on their history and provide personalized advice.
            Be friendly, helpful, and informative. If their question requires medical expertise beyond nutrition,
            advise them to consult with a healthcare professional.
            """
            
            prompt = f"{system_context}\n\nUser question: {question}\n\nResponse:"
            
            with st.spinner("Thinking..."):
                response = generate_text(prompt)
            
            # Add AI response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            
            # Rerun to update the chat display
            st.rerun()

# Run the main function
ai_nutritionist_chat()
