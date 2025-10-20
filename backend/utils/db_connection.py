from pymongo import MongoClient
from pymongo.database import Database
from config.settings import MONGO_URI

client = MongoClient(MONGO_URI)
# annotate db as Database so type-checkers (Pylance) understand indexing on it
db: Database = client["notevault"]
users_collection = db["users"]
