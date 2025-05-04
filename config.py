import streamlit as st


class Settings:
    # MongoDB configuration
    MONGO_URI = st.secrets.get("mongodb_uri", "")

    # Model configurations
    IMAGE_MODEL = "eslamxm/vit-base-food101"
    TEXT_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"
    EMBED_MODEL = "sentence-transformers/all-MiniLM-L12-v2"

    # Database collections
    USERS_COLLECTION = "users"
    FOOD_LOGS_COLLECTION = "food_logs"
    COMMUNITY_RECIPES_COLLECTION = "community_recipes"
    ANALYTICS_COLLECTION = "analytics"

    # Gamification settings
    XP_PER_RECIPE = 10
    XP_PER_MEAL_LOG = 5
    XP_LEVELS = {
        0: "Nutrition Novice",
        100: "Health Enthusiast",
        250: "Wellness Warrior",
        500: "Nutrition Ninja",
        1000: "Diet Guru"
    }

    # Application settings
    APP_NAME = "NutriPal"
    APP_VERSION = "1.0.0"
    DEBUG = False