from backend.utils.db_connection import users_collection
from werkzeug.security import generate_password_hash, check_password_hash

def create_user(username, email, password):
    # Check if user already exists
    if users_collection.find_one({"username": username}):
        return {"error": "Username already exists."}
    
    hashed_pw = generate_password_hash(password)
    user = {"username": username, "email": email, "password": hashed_pw}
    users_collection.insert_one(user)
    return {"message": "User registered successfully."}

def verify_user(username, password):
    user = users_collection.find_one({"username": username})
    if not user:
        return {"error": "User not found."}
    
    if check_password_hash(user["password"], password):
        return {"message": "Login successful.", "username": username}
    else:
        return {"error": "Invalid password."}
