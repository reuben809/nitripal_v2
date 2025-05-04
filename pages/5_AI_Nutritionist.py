import streamlit as st
from modules.auth import is_authenticated
from modules.db import Database
from modules.models import generate_text
from utils.navigation import setup_navigation

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

# Setup navigation
setup_navigation(st.session_state.username)

# App title and description
st.title('🍎 :red[NutriPal] - Your AI-Powered Nutrition Coach')
st.subheader('AI Nutritionist Chat')

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

    # Add a section for health profile management
    with st.expander("Manage Health Profile", expanded=False):
        st.markdown("### Update Your Health Profile")
        st.write("Provide information about your health conditions, dietary restrictions, allergies, and goals.")
        st.write("This information helps our AI provide more personalized nutrition advice.")

        # Get current health profile
        user = db.get_user(st.session_state.username)
        current_health = user.get("health_history", "")

        # Display current health profile
        if current_health:
            st.subheader("Current Health Profile")
            st.info(current_health)

        # Form for updating health profile
        health_update = st.text_area(
            "Enter health information",
            placeholder="Example: I have type 2 diabetes, lactose intolerance, and I'm trying to lose weight. I exercise 3 times a week and have high blood pressure.",
            height=150
        )

        if st.button("Update Health Profile"):
            if health_update:
                # Update health history in database
                success = db.update_user_health_history(st.session_state.username, health_update)
                if success:
                    st.success("Health profile updated successfully!")
                    # Rerun to show updated profile
                    st.rerun()
                else:
                    st.error("Failed to update health profile. Please try again.")
            else:
                st.warning("Please enter health information before updating.")

    # Check for API key in session state (now loaded from secrets)
    if not st.session_state.get('huggingface_api_key'):
        st.error("No API key available. Please contact the administrator.")
        return

    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(
                f"<div style='background-color:#e6f7ff;padding:10px;border-radius:5px;margin-bottom:10px'><strong>You:</strong> {message['content']}</div>",
                unsafe_allow_html=True)
        else:
            st.markdown(
                f"<div style='background-color:#f0f0f0;padding:10px;border-radius:5px;margin-bottom:10px'><strong>AI Nutritionist:</strong> {message['content']}</div>",
                unsafe_allow_html=True)

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
            try:
                # Get a specialized model for nutrition analysis
                from modules.models import get_text_model

                # Create a prompt template and chain
                from langchain_core.prompts import PromptTemplate
                from langchain.chains import LLMChain

                llm = get_text_model("nutrition")
                prompt_template = PromptTemplate(template=prompt, input_variables=[])
                chain = LLMChain(llm=llm, prompt=prompt_template)

                # Run the chain
                response = chain.run({})
            except Exception as e:
                st.error(str(e))
                return

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
                try:
                    # Get a specialized model for nutrition analysis
                    from modules.models import get_text_model

                    # Create a prompt template and chain
                    from langchain_core.prompts import PromptTemplate
                    from langchain.chains import LLMChain

                    llm = get_text_model("nutrition")
                    prompt_template = PromptTemplate(template=prompt, input_variables=[])
                    chain = LLMChain(llm=llm, prompt=prompt_template)

                    # Run the chain
                    response = chain.run({})
                except Exception as e:
                    st.error(str(e))
                    return

            # Add AI response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": response})

            # Rerun to update the chat display
            st.rerun()


# Run the main function
ai_nutritionist_chat()
