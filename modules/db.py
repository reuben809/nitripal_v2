import streamlit as st
from pymongo import MongoClient
from bson.objectid import ObjectId
import time
from datetime import datetime, timedelta
import config
mongo_key = st.secrets['mongokey']
class Database:
    def __init__(self):
        """Initialize database connection"""
        self.connection_string = f"mongodb+srv://atifshaik538:{mongo_key}@nutripalcluster.vq56uyq.mongodb.net/?retryWrites=true&w=majority&appName=nutripalcluster"
        self.client = MongoClient(self.connection_string)
        self.db = self.client.nutripal
        
        # Ensure collections exist
        self.users = self.db[config.Settings.USERS_COLLECTION]
        self.food_logs = self.db[config.Settings.FOOD_LOGS_COLLECTION]
        self.community_recipes = self.db[config.Settings.COMMUNITY_RECIPES_COLLECTION]
        self.analytics = self.db[config.Settings.ANALYTICS_COLLECTION]
    
    # User management
    def user_exists(self, username):
        """Check if a username is already taken"""
        return self.users.count_documents({"username": username}) > 0
    
    def create_user(self, user_data):
        """Create a new user document"""
        try:
            result = self.users.insert_one(user_data)
            return result.acknowledged
        except Exception as e:
            st.error(f"Error creating user: {e}")
            return False
    
    def get_user(self, username):
        """Get user document by username"""
        return self.users.find_one({"username": username})
    
    def update_user_health_history(self, username, health_info):
        """Update a user's health history"""
        try:
            user = self.get_user(username)
            if not user:
                return False
            
            existing_history = user.get("health_history", "")
            new_history = existing_history + ".\n" + health_info if existing_history else health_info
            
            result = self.users.update_one(
                {"username": username},
                {"$set": {"health_history": new_history}}
            )
            return result.modified_count > 0
        except Exception as e:
            st.error(f"Error updating health history: {e}")
            return False
    
    def update_user_food_history(self, username, food_info):
        """Update a user's food history"""
        try:
            user = self.get_user(username)
            if not user:
                return False
            
            existing_history = user.get("food_history", "")
            new_history = existing_history + ".\n" + food_info if existing_history else food_info
            
            result = self.users.update_one(
                {"username": username},
                {"$set": {"food_history": new_history}}
            )
            return result.modified_count > 0
        except Exception as e:
            st.error(f"Error updating food history: {e}")
            return False
    
    def add_xp(self, username, xp_amount):
        """Add XP to user and return new total"""
        try:
            result = self.users.update_one(
                {"username": username},
                {"$inc": {"xp": xp_amount}}
            )
            
            if result.modified_count > 0:
                user = self.get_user(username)
                return user.get("xp", 0)
            return None
        except Exception as e:
            st.error(f"Error adding XP: {e}")
            return None
    
    def get_user_stats(self, username):
        """Get user level and XP information"""
        user = self.get_user(username)
        if not user:
            return None
        
        xp = user.get("xp", 0)
        
        # Determine level from XP
        current_level_xp = 0
        next_level_xp = 100  # Default first level threshold
        level_name = config.Settings.XP_LEVELS[0]
        
        # Find current level
        for level_threshold in sorted(config.Settings.XP_LEVELS.keys()):
            if xp >= level_threshold:
                current_level_xp = level_threshold
                level_name = config.Settings.XP_LEVELS[level_threshold]
            else:
                next_level_xp = level_threshold
                break
        
        return {
            "xp": xp,
            "level_name": level_name,
            "current_level_xp": current_level_xp,
            "next_level_xp": next_level_xp
        }
    
    # Meal logging
    def log_meal(self, username, date, meal_type, description, ingredients=None, nutrition=None):
        """Log a meal for a user"""
        try:
            meal_data = {
                "username": username,
                "date": date,
                "meal_type": meal_type,
                "description": description,
                "ingredients": ingredients or [],
                "nutrition": nutrition or {},
                "created_at": time.time()
            }
            
            result = self.food_logs.insert_one(meal_data)
            if result.acknowledged:
                # Add XP for logging a meal
                self.add_xp(username, config.Settings.XP_PER_MEAL_LOG)
                return True
            return False
        except Exception as e:
            st.error(f"Error logging meal: {e}")
            return False
    
    def get_meals_by_date_range(self, username, start_date, end_date):
        """Get meals logged within a date range"""
        try:
            meals = self.food_logs.find({
                "username": username,
                "date": {"$gte": start_date, "$lte": end_date}
            }).sort("date", 1)
            
            return list(meals)
        except Exception as e:
            st.error(f"Error retrieving meals: {e}")
            return []
    
    def get_recent_meals(self, username, limit=5):
        """Get recently logged meals"""
        try:
            meals = self.food_logs.find({
                "username": username
            }).sort("created_at", -1).limit(limit)
            
            return list(meals)
        except Exception as e:
            st.error(f"Error retrieving recent meals: {e}")
            return []
    
    # Community recipes
    def add_community_recipe(self, recipe_data):
        """Add a recipe to the community collection"""
        try:
            recipe_data["created_at"] = time.time()
            result = self.community_recipes.insert_one(recipe_data)
            
            if result.acknowledged:
                # Add XP for submitting a recipe
                self.add_xp(recipe_data["username"], config.Settings.XP_PER_RECIPE)
                return True
            return False
        except Exception as e:
            st.error(f"Error adding community recipe: {e}")
            return False
    
    def get_community_recipes(self, limit=20, tags=None):
        """Get community recipes with optional tag filtering"""
        try:
            query = {}
            if tags:
                query["tags"] = {"$in": tags}
            
            recipes = self.community_recipes.find(query).sort("created_at", -1).limit(limit)
            return list(recipes)
        except Exception as e:
            st.error(f"Error retrieving community recipes: {e}")
            return []
    
    def get_nutrition_history(self, username, days=7):
        """Get nutrition history for visualization"""
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            meals = self.get_meals_by_date_range(username, start_date, end_date)
            
            # Aggregate nutrition data by day
            nutrition_data = {}
            for meal in meals:
                date = meal.get("date")
                nutrition = meal.get("nutrition", {})
                
                if date not in nutrition_data:
                    nutrition_data[date] = {
                        "calories": 0,
                        "protein": 0,
                        "carbs": 0,
                        "fat": 0
                    }
                
                nutrition_data[date]["calories"] += nutrition.get("calories", 0)
                nutrition_data[date]["protein"] += nutrition.get("protein", 0)
                nutrition_data[date]["carbs"] += nutrition.get("carbs", 0)
                nutrition_data[date]["fat"] += nutrition.get("fat", 0)
            
            # Convert to list for easier charting
            result = []
            for date, data in nutrition_data.items():
                entry = {"date": date}
                entry.update(data)
                result.append(entry)
            
            return sorted(result, key=lambda x: x["date"])
        except Exception as e:
            st.error(f"Error retrieving nutrition history: {e}")
            return []
