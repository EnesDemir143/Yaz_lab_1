from Backend.src.DataBase.src.Database_connection import get_database

def get_departments():
    try:
        with get_database() as conn:
            with conn.cursor() as cursor:
                sql = "SELECT department_name FROM users GrOUP BY department_name"
                cursor.execute(sql)
                results = cursor.fetchall()
                departments = [row['department_name'] for row in results if row['department_name']]
        return departments, 'success', 'Departments retrieved successfully'
    except Exception as e:
        return [], 'error', str(e)