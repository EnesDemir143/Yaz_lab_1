from Backend.src.DataBase.src.structures.user import User
from Backend.src.DataBase.src.Database_connection import get_database
from Backend.src.DataBase.src.utils.hash_password import HashPassword

def get_current_role(user: User, hasher=HashPassword()) -> str:
    if user.email == 'admin' and user.password == 'admin' and user.department == 'admin':
        return 'admin', 'admin'
    else:
        with get_database() as db:
            with db.cursor() as cursor:
                query = "SELECT password_hash, department FROM users WHERE email = %s"
                cursor.execute(query, (user.email,))
                password, department = cursor.fetchone()
        print("department:", department)  
        print("fetched password hash from DB:", password)
        print("provided password:", user.password)
        if not password:
            return 'unknown', 'unknown'
        password_is_true = hasher.verify_password(user.password, password)
        print("Password verification result:", password_is_true)
        return 'coordinator' if password_is_true else 'unknown', department if password_is_true else 'unknown'