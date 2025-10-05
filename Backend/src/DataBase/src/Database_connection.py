import pymysql
from dotenv import load_dotenv
import os

ENV_PATH = '../../../../.env'

load_dotenv(ENV_PATH)

def get_database() -> pymysql.connections.Connection:
    try:
        connection = pymysql.connect(
            host='mysql',
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE"),
            port=3306
        )
    except pymysql.MySQLError as e:
        print(f"Error connecting to database: {e}")
        raise
    return connection