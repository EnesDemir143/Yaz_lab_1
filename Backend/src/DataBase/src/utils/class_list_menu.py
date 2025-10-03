from Backend.src.DataBase.src.database_connection import get_database
import pymysql

def class_list_menu(department: str) -> list[dict]:
    db = get_database()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    
    query = "SELECT * FROM classes WHERE department = %s"
    cursor.execute(query, (department,))
    classes = cursor.fetchall()
    
    cursor.close()
    db.close()
    return classes