import os
import motor.motor_asyncio
from dotenv import load_dotenv

load_dotenv()

# Load MongoDB URI from environment variables
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = "linked_microservice_insights"

if not MONGO_URI:
    raise ValueError("MONGO_URI is not set in the environment variables.")

# Singleton MongoDB Client
class MongoDB:
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
        return cls._client

# Initialize MongoDB Client
client = MongoDB.get_client()
database = client[DATABASE_NAME]

# Collections
pages_collection = database["pages"]
posts_collection = database["posts"]
users_collection = database["users"]
scraper_collection = database["scraper"]
comment_collection = database["comments"]

# Test Connection
async def check_mongo_connection():
    try:
        await client.admin.command("ping")
        print(" MongoDB Connected Successfully!")
    except Exception as e:
        print(f" MongoDB Connection Failed: {e}")

# Close MongoDB Connection on FastAPI Shutdown
async def close_mongo_connection():
    if client:
        client.close()
        print("🔌 MongoDB Connection Closed.")

# Export collections for easy import
__all__ = [
    "database", "pages_collection", "posts_collection",
    "users_collection", "scraper_collection", "comment_collection",
    "check_mongo_connection", "close_mongo_connection"
]
