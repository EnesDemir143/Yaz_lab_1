from Backend.src.DataBase.src.Database_connection import get_database
import pymysql

def get_departments():
    try:
        with get_database() as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = "SELECT department FROM users GROUP BY department"
                cursor.execute(sql)
                results = cursor.fetchall()
                
                sql = "SELECT department FROM classes GROUP BY department"
                cursor.execute(sql)
                class_results = cursor.fetchall()
                
                departments = [row['department'] for row in results if row['department']]
                class_departments = [row['department'] for row in class_results if row['department']]
                extended_departments = list(set(departments) | set(class_departments))
        return extended_departments, 'success', 'Departments retrieved successfully'
    except Exception as e:
        return [], 'error', str(e)