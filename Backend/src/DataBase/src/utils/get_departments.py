from Backend.src.DataBase.src.Database_connection import get_database
import pymysql

def get_departments():
    try:
        with get_database() as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = "SELECT department FROM users GROUP BY department"
                cursor.execute(sql)
                results = cursor.fetchall()
                departments = [row['department'] for row in results if row['department']]
        return departments, 'success', 'Departments retrieved successfully'
    except Exception as e:
        return [], 'error', str(e)