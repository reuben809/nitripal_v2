import streamlit as st
import re

# Dictionary of high water footprint foods
HIGH_WATER_FOOTPRINT_FOODS = {
    "beef": 15400,
    "lamb": 10400,
    "pork": 5990,
    "chicken": 4330,
    "rice": 2500,
    "almonds": 12000,
    "chocolate": 17000,
    "coffee": 18900,
    "cheese": 5000,
    "butter": 5550,
    "avocado": 2000,
    "pistachios": 11360,
    "walnuts": 4900,
    "sugar": 1780,
    "asparagus": 1470,
    "vanilla": 126505,
}

# Dictionary of low water footprint foods
LOW_WATER_FOOTPRINT_FOODS = {
    "lettuce": 130,
    "tomatoes": 210,
    "cabbage": 200,
    "cucumber": 240,
    "potatoes": 290,
    "oranges": 560,
    "apples": 700,
    "bananas": 860,
    "corn": 1220,
    "oats": 1640,
    "lentils": 5874,
    "beans": 5053,
    "chickpeas": 4177,
    "quinoa": 1250,
    "peas": 1800,
}

def check_eco_friendly_ingredients(ingredients_list):
    """
    Check ingredients for water footprint
    
    Args:
        ingredients_list: List of ingredients
        
    Returns:
        Tuple of (eco_friendly_ingredients, high_footprint_ingredients)
    """
    eco_friendly = []
    high_footprint = []
    
    for ingredient in ingredients_list:
        ingredient_lower = ingredient.lower()
        
        # Check if this ingredient is in our high water footprint list
        for food, _ in HIGH_WATER_FOOTPRINT_FOODS.items():
            if food in ingredient_lower:
                high_footprint.append(ingredient)
                break
        else:
            # If not found in high footprint list, check low footprint list
            for food, _ in LOW_WATER_FOOTPRINT_FOODS.items():
                if food in ingredient_lower:
                    eco_friendly.append(ingredient)
                    break
    
    return eco_friendly, high_footprint

def get_alternative_ingredients(high_footprint_ingredient):
    """
    Suggest alternative ingredients with lower water footprint
    
    Args:
        high_footprint_ingredient: The high water footprint ingredient
        
    Returns:
        List of alternative ingredients
    """
    alternatives = {
        "beef": ["lentils", "beans", "tofu", "seitan", "jackfruit"],
        "lamb": ["lentils", "beans", "tofu", "seitan", "mushrooms"],
        "pork": ["tofu", "tempeh", "seitan", "jackfruit"],
        "chicken": ["tofu", "tempeh", "seitan", "lentils"],
        "rice": ["quinoa", "barley", "couscous", "bulgur", "potatoes"],
        "almonds": ["walnuts", "peanuts", "sunflower seeds", "pumpkin seeds"],
        "chocolate": ["carob", "cacao nibs (in smaller amounts)"],
        "coffee": ["tea", "chicory root", "dandelion tea"],
        "cheese": ["nutritional yeast", "tofu", "hummus"],
        "butter": ["olive oil", "coconut oil", "plant-based spreads"],
        "avocado": ["hummus", "pesto", "edamame spread"],
        "pistachios": ["pumpkin seeds", "sunflower seeds", "peanuts"],
        "walnuts": ["pumpkin seeds", "sunflower seeds", "peanuts"],
        "sugar": ["honey", "maple syrup", "date sugar", "coconut sugar"],
        "asparagus": ["broccoli", "green beans", "zucchini"],
        "vanilla": ["cinnamon", "almond extract", "lemon zest"],
    }
    
    for food in HIGH_WATER_FOOTPRINT_FOODS.keys():
        if food in high_footprint_ingredient.lower():
            return alternatives.get(food, ["No specific alternatives found"])
    
    return ["No specific alternatives found"]

def parse_ingredients_from_recipe(recipe_text):
    """
    Parse ingredients from recipe text
    
    Args:
        recipe_text: Full recipe text
        
    Returns:
        List of ingredients
    """
    ingredients = []
    
    # Look for common ingredient section headers
    ingredient_section_patterns = [
        r"(?:INGREDIENTS:|Ingredients:|ingredients:)[\s\S]*?(?=\n\s*\n|\n\s*(?:INSTRUCTIONS|Instructions|METHOD|Method|DIRECTIONS|Directions|STEPS|Steps))",
        r"(?:\*\*Ingredients\*\*|\*Ingredients\*)[\s\S]*?(?=\n\s*\n|\n\s*(?:\*\*Instructions\*\*|\*Instructions\*|\*\*Method\*\*|\*Method\*))",
    ]
    
    ingredient_section = None
    for pattern in ingredient_section_patterns:
        match = re.search(pattern, recipe_text)
        if match:
            ingredient_section = match.group(0)
            break
    
    if ingredient_section:
        # Extract ingredients with common list formats
        ingredient_lines = re.findall(r'(?:^|\n)\s*(?:[-•*]|\d+\.|\d+\)) (.*?)(?:\n|$)', ingredient_section)
        ingredients.extend(ingredient_lines)
        
        # If no list format found, try splitting by newlines and filtering
        if not ingredients:
            lines = ingredient_section.split('\n')
            for line in lines[1:]:  # Skip the header line
                line = line.strip()
                if line and not line.startswith(('Instructions', 'INSTRUCTIONS', 'Method', 'METHOD', 'Directions', 'DIRECTIONS')):
                    ingredients.append(line)
    
    # If we didn't find an ingredient section, look for bullet points or numbered lists
    if not ingredients:
        ingredient_lines = re.findall(r'(?:^|\n)\s*(?:[-•*]|\d+\.|\d+\)) (.*?)(?:\n|$)', recipe_text)
        
        # Filter out likely non-ingredient lines
        for line in ingredient_lines:
            if not any(word in line.lower() for word in ["instructions", "method", "directions", "steps", "preheat", "bake", "simmer", "stir"]):
                ingredients.append(line)
    
    # Clean up ingredients
    cleaned_ingredients = []
    for ingredient in ingredients:
        # Remove quantity and measurements, keeping the food item
        food_item = re.sub(r'^[\d\s/¼½¾\-]+\s*(?:cup|cups|tablespoon|tablespoons|tbsp|tsp|teaspoon|teaspoons|gram|grams|g|kg|ml|oz|ounce|ounces|lb|pound|pounds|pinch|dash)\s+of\s+', '', ingredient)
        food_item = re.sub(r'^[\d\s/¼½¾\-]+\s*(?:cup|cups|tablespoon|tablespoons|tbsp|tsp|teaspoon|teaspoons|gram|grams|g|kg|ml|oz|ounce|ounces|lb|pound|pounds|pinch|dash)\s+', '', food_item)
        
        # Remove additional annotations
        food_item = re.sub(r'\(.*?\)', '', food_item)
        food_item = re.sub(r',.*$', '', food_item)
        food_item = re.sub(r'for.*$', '', food_item)
        
        if food_item.strip():
            cleaned_ingredients.append(food_item.strip())
    
    return cleaned_ingredients

def calculate_macronutrients(ingredients_list):
    """
    Calculate approximate macronutrients based on ingredients
    
    Args:
        ingredients_list: List of ingredients
        
    Returns:
        Dictionary with estimated macronutrients
    """
    # This is a simplified approximation
    # For a real application, you'd use a nutrition database API
    
    # Default values
    macros = {
        "calories": 0,
        "protein": 0,
        "carbs": 0,
        "fat": 0
    }
    
    # Simple mapping of common ingredients to macros
    # Format: "ingredient": [calories, protein(g), carbs(g), fat(g)]
    macro_mapping = {
        "chicken": [165, 31, 0, 3.6],
        "beef": [250, 26, 0, 17],
        "fish": [206, 22, 0, 12],
        "rice": [130, 2.7, 28, 0.3],
        "potato": [77, 2, 17, 0.1],
        "pasta": [131, 5, 25, 1.1],
        "bread": [265, 9, 49, 3.2],
        "egg": [78, 6, 0.6, 5],
        "milk": [42, 3.4, 5, 1],
        "cheese": [402, 25, 1.3, 33],
        "yogurt": [59, 10, 3.6, 0.4],
        "butter": [717, 0.9, 0.1, 81],
        "oil": [884, 0, 0, 100],
        "carrot": [41, 0.9, 10, 0.2],
        "broccoli": [34, 2.8, 7, 0.4],
        "spinach": [23, 2.9, 3.6, 0.4],
        "tomato": [18, 0.9, 3.9, 0.2],
        "apple": [52, 0.3, 14, 0.2],
        "banana": [89, 1.1, 23, 0.3],
        "sugar": [387, 0, 100, 0],
        "flour": [364, 10, 76, 1],
        "beans": [347, 21, 63, 1.2],
        "lentils": [116, 9, 20, 0.4],
        "nuts": [607, 21, 21, 54],
        "tofu": [76, 8, 2, 4.8],
    }
    
    # Analyze each ingredient
    for ingredient in ingredients_list:
        ingredient_lower = ingredient.lower()
        
        # Check if any known ingredient is in the text
        for food, values in macro_mapping.items():
            if food in ingredient_lower:
                # Add contribution to macros
                macros["calories"] += values[0]
                macros["protein"] += values[1]
                macros["carbs"] += values[2]
                macros["fat"] += values[3]
                break
    
    return macros
