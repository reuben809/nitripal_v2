import streamlit as st
import bcrypt
import uuid
from modules.db import Database


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def verify_password(stored_hash, password):
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash)


def register_user(username, password, email):
    db = Database()
    if db.user_exists(username):
        return False, "Username exists"

    user_data = {
        "user_id": str(uuid.uuid4()),
        "username": username,
        "password": hash_password(password),
        "email": email,
        "created_at": time.time(),
        "xp": 0,
        "health_history": "",
        "food_history": ""
    }

    if db.create_user(user_data):
        return True, "Registration successful"
    return False, "Registration failed"


def login_user(username, password):
    db = Database()
    user = db.get_user_by_username(username)

    if not user or not verify_password(user["password"], password):
        return False, "Invalid credentials"

    st.session_state.update({
        "authenticated": True,
        "user_id": user["user_id"],
        "username": username
    })
    return True, "Login successful"