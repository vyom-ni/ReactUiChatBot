import json
import os
from core.config import USERS_FILE
import json
import os
import uuid
from datetime import datetime

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def create_user_if_not_exist(phone):
    users = load_users()
    
    # Check if user exists by phone
    for user in users.values():
        if user["phone"] == phone:
            return user  # Existing user

    # If not found, create a new user
    new_id = str(uuid.uuid4())
    new_user = {
        "id": new_id,
        "phone": phone,
        "created_at": datetime.utcnow().isoformat()
    }
    users[new_id] = new_user
    save_users(users)
    return new_user
