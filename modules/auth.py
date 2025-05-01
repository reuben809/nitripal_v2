import streamlit as st
import bcrypt
from modules.db import Database
import time

@st.cache_resource
def get_db():
    return Database()

def hash_password(password):
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def verify_password(stored_password_hash, provided_password):
    """Verify a password against stored hash"""
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password_hash)

def register_user(username, password, email):
    """Register a new user"""
    db = get_db()
    
    # Check if username already exists
    if db.user_exists(username):
        return False, "Username already exists"
    
    # Hash the password
    password_hash = hash_password(password)
    
    # Create user document
    user_data = {
        "username": username,
        "password": password_hash,
        "email": email,
        "created_at": time.time(),
        "xp": 0,
        "health_history": "",
        "food_history": ""
    }
    
    # Insert user into database
    success = db.create_user(user_data)
    if success:
        return True, "Registration successful"
    else:
        return False, "Registration failed"

def login_user(username, password):
    """Authenticate a user and establish session"""
    db = get_db()
    user = db.get_user(username)
    
    if not user:
        return False, "User not found"
    
    # Verify password
    if not verify_password(user["password"], password):
        return False, "Invalid password"
    
    # Set session state
    st.session_state.authenticated = True
    st.session_state.username = username
    st.session_state.user_id = str(user["_id"])
    
    return True, "Login successful"

def is_authenticated():
    """Check if user is authenticated"""
    return st.session_state.get("authenticated", False)

def logout_user():
    """Log out user by clearing session state"""
    if "authenticated" in st.session_state:
        st.session_state.authenticated = False
    if "username" in st.session_state:
        st.session_state.username = None
    if "user_id" in st.session_state:
        st.session_state.user_id = None
