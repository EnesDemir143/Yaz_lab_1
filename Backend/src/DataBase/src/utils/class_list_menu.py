from Backend.src.DataBase.src.database_connection import get_database
import pymysql

def class_list_menu(department: str) -> list[dict]:
    with get_database() as db:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            query = "SELECT * FROM classes WHERE department = %s"
            cursor.execute(query, (department,))
            return cursor.fetchall()
            