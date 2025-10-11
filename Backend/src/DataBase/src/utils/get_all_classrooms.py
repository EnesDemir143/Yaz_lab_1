from Backend.src.DataBase.src.Database_connection import get_database 
import pymysql

def get_all_classrooms(department: str) -> list[dict]:
    try:
        with get_database() as db:
            with db.cursor(pymysql.cursors.DictCursor) as cursor:
                query = """
                SELECT 
                    classroom_id,
                    classroom_name,
                    capacity
                FROM classrooms
                WHERE department_name = %s;
                """
                cursor.execute(query, (department.strip(),))
                classrooms = cursor.fetchall()
    except Exception as e:
        print(f"Error while fetching all classes: {e}")
        return [], 'error', str(e)
    return classrooms, 'success', 'All classes fetched successfully.'
