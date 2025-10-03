import pymysql
from dotenv import load_dotenv
import os

ENV_PATH = '../../../../.env'

load_dotenv(ENV_PATH)

def get_database() -> pymysql.connections.Connection:
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise ValueError("MONGO_URI is not set in the environment variables")
    
    connection = pymysql.connect(
        host='mysql',
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        port=3306
    )
    return connection