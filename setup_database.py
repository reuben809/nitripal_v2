import pymongo
import argparse
import bcrypt
import time
from datetime import datetime


def setup_database(connection_string, admin_username, admin_password, admin_email):
    """Setup and initialize the MongoDB database"""
    print("Connecting to MongoDB...")
    client = pymongo.MongoClient(connection_string)

    # Test connection
    try:
        client.admin.command('ping')
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        return False

    # Create/access database
    db = client.nutripal
    print("Database 'nutripal' accessed successfully")

    # Create collections if they don't exist
    collections = ["users", "food_logs", "community_recipes", "analytics"]

    for collection_name in collections:
        if collection_name not in db.list_collection_names():
            db.create_collection(collection_name)
            print(f"Collection '{collection_name}' created")
        else:
            print(f"Collection '{collection_name}' already exists")

    # Create indexes for better performance
    print("Creating indexes...")

    # User collection indexes
    db.users.create_index("username", unique=True)
    db.users.create_index("email")

    # Food logs indexes
    db.food_logs.create_index([("username", 1), ("date", 1)])
    db.food_logs.create_index("created_at")

    # Community recipes indexes
    db.community_recipes.create_index("tags")
    db.community_recipes.create_index("created_at")

    # Analytics indexes
    db.analytics.create_index([("username", 1), ("date", 1)])

    # Create admin user if it doesn't exist
    users = db.users
    if users.count_documents({"username": admin_username}) == 0:
        print(f"Creating admin user '{admin_username}'...")

        # Hash the password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), salt)

        # Create admin user document
        admin_user = {
            "username": admin_username,
            "password": hashed_password,
            "email": admin_email,
            "created_at": time.time(),
            "xp": 1000,  # Start with top level XP
            "health_history": "Admin user with full access.",
            "food_history": "Admin user with sample food history.",
            "is_admin": True
        }

        users.insert_one(admin_user)
        print("Admin user created successfully!")
    else:
        print(f"Admin user '{admin_username}' already exists")

    # Create sample data
    create_sample_data(db)

    print("Database setup completed successfully!")
    return True


def create_sample_data(db):
    """Create sample data for the database"""
    # Add sample community recipes if none exist
    if db.community_recipes.count_documents({}) == 0:
        print("Adding sample community recipes...")

        sample_recipes = [
            {
                "title": "Healthy Breakfast Bowl",
                "username": "system",
                "description": "A nutritious breakfast bowl with oats, fruits, and nuts.",
                "ingredients": ["oats", "banana", "berries", "almonds", "honey"],
                "instructions": "1. Cook oats with water or milk. 2. Top with sliced banana, berries, and almonds. 3. Drizzle with honey.",
                "tags": ["breakfast", "vegetarian", "healthy"],
                "nutrition": {
                    "calories": 350,
                    "protein": 12,
                    "carbs": 55,
                    "fat": 10
                },
                "created_at": time.time()
            },
            {
                "title": "Green Smoothie",
                "username": "system",
                "description": "A refreshing green smoothie with spinach, banana, and almond milk.",
                "ingredients": ["spinach", "banana", "almond milk", "chia seeds"],
                "instructions": "Blend all ingredients until smooth.",
                "tags": ["breakfast", "vegan", "quick"],
                "nutrition": {
                    "calories": 220,
                    "protein": 5,
                    "carbs": 40,
                    "fat": 5
                },
                "created_at": time.time()
            }
        ]

        db.community_recipes.insert_many(sample_recipes)
        print("Sample recipes added successfully!")
    else:
        print("Community recipes already exist, skipping sample data")

    # Add more sample data for other collections as needed


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Setup NutriPal MongoDB database')
    parser.add_argument('--uri', required=True, help='MongoDB connection string')
    parser.add_argument('--admin-username', default='admin', help='Admin username')
    parser.add_argument('--admin-password', required=True, help='Admin password')
    parser.add_argument('--admin-email', required=True, help='Admin email')

    args = parser.parse_args()

    # Run setup
    setup_database(args.uri, args.admin_username, args.admin_password, args.admin_email)