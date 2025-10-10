from Backend.src.DataBase.src.Database_connection import get_database 
import pymysql

def get_all_classes(department: str) -> list[dict]:
    try:
        with get_database() as db:
            with db.cursor(pymysql.cursors.DictCursor) as cursor:
                query = """
                SELECT 
                    class_id,
                    class_name
                FROM classes
                WHERE department = %s;
                """
                cursor.execute(query, (department,))
                classes = cursor.fetchall()
    except Exception as e:
        print(f"Error while fetching all classes: {e}")
        return [], 'error', str(e)
    return classes, 'success', 'All classes fetched successfully.'