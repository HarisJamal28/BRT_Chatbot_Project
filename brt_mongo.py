
# my_mongo.py
from dotenv import load_dotenv
from pymongo import MongoClient
import os
import time  # Import the time module

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("No MongoDB URI found in the .env file")


DATABASE_NAME = "BRT_Chatbot"     # Name of your database
COLLECTION_NAME = "chat_history"          # Name of your collection

# Initialize MongoDB client and specify database and collection
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

def save_chat(user_id, role, content):
    """
    Saves a chat message to MongoDB.

    Parameters:
    - user_id (str): The user's unique identifier.
    - role (str): The role of the message sender (e.g., 'user' or 'assistant').
    - content (str): The content of the chat message.
    """
    chat_data = {
        "user_id": user_id,
        "role": role,
        "content": content,
        "timestamp": time.time()
    }
    collection.insert_one(chat_data)

def fetch_chat(user_id):
    """
    Fetches chat history for a specific user from MongoDB.

    Parameters:
    - user_id (str): The user's unique identifier.

    Returns:
    - List[dict]: A list of chat messages.
    """
    chats = list(collection.find({"user_id": user_id}, {"_id": 0}).sort("timestamp"))
    return chats

def clear_chat_history(user_id=None):
    """
    Clears chat history from MongoDB.

    Parameters:
    - user_id (str, optional): If provided, clears history for the specific user.
    If None, clears the entire collection.
    """
    if user_id:
        collection.delete_many({"user_id": user_id})
        print(f"Cleared chat history for user: {user_id}")
    else:
        collection.delete_many({})
        print("Cleared entire chat history.")
