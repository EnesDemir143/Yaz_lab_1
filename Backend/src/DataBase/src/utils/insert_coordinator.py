from Backend.src.DataBase.src.Database_connection import get_database
from Backend.src.DataBase.src.structures.user import User
from Backend.src.DataBase.src.utils.hash_password import HashPassword

def insert_department_coordinator(user: User, hash=HashPassword()) -> None:
    with get_database() as connection:
        with connection.cursor() as cursor:
            hashed_password = hash.hash_password(user.password)
    
            sql = """
            INSERT INTO users (email, password_hash, department)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                password_hash = VALUES(password_hash),
                department = VALUES(department)
            """
            cursor.execute(sql, (user.email, hashed_password, user.department))  