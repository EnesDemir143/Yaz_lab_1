from Backend.src.DataBase.src.structures.user import User
from Backend.src.DataBase.src.database_connection import get_database
from Backend.src.DataBase.src.utils.hash_password import HashPassword

def get_current_role(user: User, hasher=HashPassword()) -> str:
    if user.email == 'admin' and user.password == 'admin':
        return 'admin'
    else:
        db = get_database()
        users_collection = db['users']
        
        user_data = users_collection.find_one({'email': user.email})
        password_is_true = hasher.verify_password(user.password, user_data['password'])
        return 'coordinator' if password_is_true else 'unknown'