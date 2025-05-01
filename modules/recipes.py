import streamlit as st
from modules.models import generate_text, classify_food_image
from langchain.chains import RetrievalQA
from modules.models import load_text_model, create_qdrant_from_text
import time

def generate_dish_from_image(image_data, health_history, kitchen_ingredients, eco_friendly=False, ignore_health=False):
    """
    Generate a recipe based on image ingredients, health history, and preferences
    
    Args:
        image_data: Image bytes for food classification
        health_history: User's health history string
        kitchen_ingredients: Additional ingredients from kitchen (string)
        eco_friendly: Boolean flag for water footprint consideration
        ignore_health: Boolean flag to prioritize eco-friendliness over health
        
    Returns:
        Recipe as a string
    """
    start_time = time.time()
    
    # Classify ingredients in the image
    image_ingredients = []
    if image_data:
        image_classification = classify_food_image(image_data)
        image_ingredients = [item['label'] for item in image_classification]
    
    # Create retrieval-based QA system with user's health history
    vectorstore = create_qdrant_from_text(health_history)
    llm = load_text_model()
    
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever()
    )
    
    # Combine all ingredients
    all_ingredients = ' '.join(image_ingredients)
    if kitchen_ingredients:
        all_ingredients += ' ' + kitchen_ingredients
    
    # Create appropriate prompt based on user preferences
    if not ignore_health and not eco_friendly:
        prompt = f"""
        Create a detailed recipe using all available ingredients, considering my health conditions as a top priority. Ensure that the dish not only includes all ingredients but also contributes positively to my well-being in line with my health objectives.

        AVAILABLE INGREDIENTS: {all_ingredients}.

        MY HEALTH: {health_history}.

        Please craft a recipe with the available ingredients. If any ingredients might be harmful due to my health conditions, please indicate so and skip them. You have the freedom to remove any harmful ingredients and adjust the recipe accordingly. Additionally, feel free to incorporate ingredients that could benefit my health, but kindly specify them before providing the recipe instructions.

        In case there isn't enough information, please create a generalized method for ingredients and health condition and try to give a generalized recipe.

        \n Before Giving Recipe do give me a list of selected ingredients, rejected ingredients and additional ingredients. Also Give a catchy DISH name!
        """
    elif eco_friendly and not ignore_health:
        prompt = f"""
        AVAILABLE INGREDIENTS: {all_ingredients}.\n
        MY HEALTH: {health_history}.\n  

        Use the available ingredients to create a recipe that not only aligns with my health objectives but also has a low water footprint. 
        Please ensure that the dish is not only healthy but also environmentally friendly. 
        If any ingredients have a high water footprint, please avoid them, even if it's beneficial for my health history. 
        You have the freedom to remove any high water footprint consuming ingredients and adjust the recipe accordingly. 
        Additionally, feel free to incorporate ingredients that could benefit my health as well as it has low water footprint, 
        but kindly specify them before providing the recipe instructions.\n

        If you wanna do trade off between health and water footprint, "Choose Water Footprint" and specify the trade off and the reason for the trade off.
        """
    else:
        prompt = f"""
        AVAILABLE INGREDIENTS: {all_ingredients}.\n

        Use the available ingredients to create a recipe that has a low water footprint. 
        Please ensure that the dish is highly environmentally friendly. 
        If any ingredients have a high water footprint, please avoid them. 
        You have the freedom to remove any high water footprint consuming ingredients and adjust the recipe accordingly. 
        Additionally, feel free to incorporate ingredients that could benefit Environment if it has low water footprint, 
        but kindly specify them before providing the recipe instructions.\n
        Additionally before giving me recipe do give me a list of rejected ingredients and reason for it!
        """
    
    # Generate recipe
    recipe = qa.run(prompt)
    
    # Log performance
    end_time = time.time()
    st.session_state.last_recipe_generation_time = end_time - start_time
    
    return recipe

def get_nutrition_info(recipe):
    """
    Extract nutritional information from a recipe
    
    Args:
        recipe: Recipe text to analyze
        
    Returns:
        Nutritional information as a string
    """
    prompt = f"""
    RECIPE: {recipe}.
    \nYou've been provided with a recipe for a dish. Your task is to extract key nutritional information from the given recipe.

    Extract the amounts of proteins, carbohydrates, and fat content present in the provided recipe.

    Note that you are not allowed to add or remove any ingredients from the recipe, nor manipulate the preparation steps.

    Additionally, extract all the vitamins and minerals content from the recipe.

    Your output should be:
    - Amounts of protein content present in the recipe.
    - Amounts of carbohydrate content present in the recipe.
    - Amounts of fat content present in the recipe.
    - Amounts of vitamins and minerals content present in the recipe.
    - Total calorie content

    Ensure that all nutritional information is accurately calculated and presented.\n
    Output should only be Nutritional content as specified above, \n don't include Instructions and Ingredients in Output
    """
    
    nutrition_info = generate_text(prompt)
    return nutrition_info

def parse_nutrition_values(nutrition_text):
    """
    Parse nutrition text to extract numerical values for database storage
    
    Args:
        nutrition_text: Nutrition information text
        
    Returns:
        Dictionary with nutrition values
    """
    # Default values
    nutrition = {
        "calories": 0,
        "protein": 0,
        "carbs": 0,
        "fat": 0
    }
    
    try:
        # Simple parsing - extract numbers followed by g or calories
        lines = nutrition_text.strip().split('\n')
        for line in lines:
            line = line.lower()
            
            # Parse calories
            if "calorie" in line or "calories" in line:
                # Find numbers in the line
                import re
                numbers = re.findall(r'\d+', line)
                if numbers:
                    # Use the first number as calories
                    nutrition["calories"] = int(numbers[0])
            
            # Parse macronutrients
            if "protein" in line:
                numbers = re.findall(r'\d+', line)
                if numbers:
                    nutrition["protein"] = int(numbers[0])
            
            if "carbohydrate" in line or "carbs" in line:
                numbers = re.findall(r'\d+', line)
                if numbers:
                    nutrition["carbs"] = int(numbers[0])
                    
            if "fat" in line:
                numbers = re.findall(r'\d+', line)
                if numbers:
                    nutrition["fat"] = int(numbers[0])
    
    except Exception as e:
        st.warning(f"Error parsing nutrition values: {e}")
    
    return nutrition

def predict_next_meal(food_history):
    """
    Predict next meal based on user's food history
    
    Args:
        food_history: String with user's food history
        
    Returns:
        Predicted next meal as a string
    """
    prompt = f"""Food Consumption History: {food_history}

    .\nYou are given data of Food consumption history of a person. You have to predict the next meal of the person based on the data given.
    Even if information provided is less for next meal prediction do create a generalized prediction of next meal.
    \n Prediction depends upon, food items consumed in order and frequency of food items's consumed. Like a Sequential task.
    \nYou're free to add new meal as well as recommend some old meal.
    \n Output should be a meal name or a list of meal names.
    \n First answer which meal would be next meal and then proceed with your response"""
    
    prediction = generate_text(prompt)
    return prediction
