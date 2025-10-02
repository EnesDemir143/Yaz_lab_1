import pymongo
from dotenv import load_dotenv
import os

ENV_PATH = '../../../../.env'

load_dotenv(ENV_PATH)

def get_database() -> pymongo.database.Database:
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise ValueError("MONGO_URI is not set in the environment variables")
    
    client = pymongo.MongoClient(mongo_uri)
    return client.get_default_database()