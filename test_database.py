import os
import sys
import time
from datetime import datetime

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.db import Database


def test_database_connection():
    """Test database connection and operations"""
    print("Testing database connection...")
    db = Database()

    # Test connection
    if db.ping_database():
        print("✅ Database connection successful!")
    else:
        print("❌ Database connection failed!")
        return False

    # Print collection stats
    stats = db.get_collection_stats()
    if stats:
        print("\nCollection statistics:")
        for collection, count in stats.items():
            print(f"  - {collection}: {count} documents")

    # Test user operations
    print("\nTesting user operations...")
    test_username = f"test_user_{int(time.time())}"
    test_email = f"{test_username}@example.com"
    test_password = "test_password_123"

    # Hash the password (similar to auth.py)
    import bcrypt
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(test_password.encode('utf-8'), salt)

    # Create test user
    user_data = {
        "username": test_username,
        "password": password_hash,
        "email": test_email,
        "created_at": time.time(),
        "xp": 0,
        "health_history": "Test health history",
        "food_history": "Test food history"
    }

    if db.create_user(user_data):
        print(f"✅ Created test user: {test_username}")
    else:
        print(f"❌ Failed to create test user")
        return False

    # Retrieve the user
    user = db.get_user(test_username)
    if user and user["username"] == test_username:
        print(f"✅ Retrieved test user successfully")
    else:
        print(f"❌ Failed to retrieve test user")
        return False

    # Update health history
    if db.update_user_health_history(test_username, "Updated health history"):
        print(f"✅ Updated user health history")
    else:
        print(f"❌ Failed to update user health history")

    # Add XP
    new_xp = db.add_xp(test_username, 50)
    if new_xp == 50:
        print(f"✅ Added XP successfully: {new_xp}")
    else:
        print(f"❌ Failed to add XP")

    # Test meal logging
    print("\nTesting meal logging...")
    today = datetime.now().strftime('%Y-%m-%d')

    meal_success = db.log_meal(
        username=test_username,
        date=today,
        meal_type="breakfast",
        description="Test breakfast meal",
        ingredients=["eggs", "toast", "avocado"],
        nutrition={
            "calories": 350,
            "protein": 20,
            "carbs": 30,
            "fat": 15
        }
    )

    if meal_success:
        print(f"✅ Logged meal successfully")
    else:
        print(f"❌ Failed to log meal")

    # Get recent meals
    recent_meals = db.get_recent_meals(test_username, limit=1)
    if recent_meals and len(recent_meals) == 1:
        print(f"✅ Retrieved recent meal successfully")
    else:
        print(f"❌ Failed to retrieve recent meals")

    # Test nutrition history
    print("\nTesting nutrition history...")
    nutrition_history = db.get_nutrition_history(test_username, days=1)
    if nutrition_history and len(nutrition_history) > 0:
        print(f"✅ Retrieved nutrition history successfully")
    else:
        print(f"❌ Failed to retrieve nutrition history")

    print("\nAll tests completed!")
    return True


if __name__ == "__main__":
    test_database_connection()