from Backend.src.DataBase.src.structures.user import User
from Backend.src.DataBase.src.database_connection import get_database
from Backend.src.DataBase.src.utils.hash_password import HashPassword

def get_current_role(user: User, hasher=HashPassword()) -> str:
    if user.email == 'admin' and user.password == 'admin':
        return 'admin'
    else:
        db = get_database()
        cursor = db.cursor()
        query = "SELECT password FROM users WHERE email = %s"
        cursor.execute(query, (user.email,))
        password = cursor.fetchone()
        cursor.close()
        db.close() 
        
        if not password:
            return 'unknown'
        password_is_true = hasher.verify_password(user.password, password)
        return 'coordinator' if password_is_true else 'unknown'