import streamlit as st
import asyncio
import re
from langchain_community.chains import RetrievalQA
from modules.models import get_text_model, create_qdrant_from_text, generate_text, classify_food_image
from modules.db import Database
from config import Settings
import time


async def generate_recipe_async(prompt):
    try:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, generate_text, prompt)
    except Exception as e:
        st.error(f"Async generation error: {str(e)}")
        return ""


def generate_dish_from_image(image_data, health_history, kitchen_ingredients, eco_friendly=False, ignore_health=False):
    start_time = time.time()
    db = Database()

    # Classify image ingredients
    image_ingredients = []
    if image_data:
        classification = classify_food_image(image_data)
        image_ingredients = [item['label'] for item in classification]

    # Create context-aware QA system
    vectorstore = create_qdrant_from_text(health_history)
    llm = get_text_model()

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="map_reduce",
        retriever=vectorstore.as_retriever()
    )

    # Build ingredients list
    all_ingredients = ' '.join(image_ingredients + [kitchen_ingredients])

    # Generate appropriate prompt
    prompt_template = build_prompt_template(
        all_ingredients,
        health_history,
        eco_friendly,
        ignore_health
    )

    # Async generation
    recipe = asyncio.run(generate_recipe_async(prompt_template))

    # Update user history
    if st.session_state.get('user_id'):
        db.update_user_food_history(
            st.session_state.user_id,
            ', '.join(image_ingredients)
        )

    # Performance logging
    st.session_state.last_gen_time = time.time() - start_time
    return recipe


def build_prompt_template(ingredients, health, eco, ignore_health):
    base = f"""INGREDIENTS: {ingredients}
    HEALTH PROFILE: {health}
    """

    if ignore_health:
        return base + """Create an environmentally-friendly recipe prioritizing:
        1. Lowest water footprint
        2. Seasonal availability
        3. Local sourcing
        Explain any eco-friendly substitutions."""

    if eco:
        return base + """Create a recipe that balances:
        1. Health requirements
        2. Environmental impact
        Highlight both aspects in your response."""

    return base + """Create a health-optimized recipe considering:
        1. Nutritional needs
        2. Dietary restrictions
        3. Medical conditions
        Explain health benefits of key ingredients."""


def parse_nutrition_values(text):
    nutrients = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
    patterns = {
        'calories': r'calories?:\s*(\d+)',
        'protein': r'protein:\s*(\d+)g',
        'carbs': r'carbs?:\s*(\d+)g',
        'fat': r'fat:\s*(\d+)g'
    }

    try:
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                nutrients[key] = int(match.group(1))
    except Exception as e:
        st.error(f"Nutrition parsing error: {str(e)}")

    return nutrients


def predict_next_meal(food_history):
    prompt = f"""Analyze this food history and predict the next meal:
    {food_history}

    Consider:
    - Meal timing patterns
    - Nutritional balance
    - User preferences
    - Recent ingredients

    Return: 1 suggested meal with brief justification."""

    try:
        return generate_text(prompt)
    except Exception as e:
        st.error("Prediction failed. Please try again.")
        return ""