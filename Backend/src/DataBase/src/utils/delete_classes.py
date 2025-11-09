from Backend.src.DataBase.src.Database_connection import get_database
import pandas as pd

def delete_classes(department: str) -> None:
    try:
        with get_database() as connection:
            with connection.cursor() as cursor:
                sql = """
                DELETE FROM classes WHERE department = %s
                """
                cursor.execute(sql, (department,))
            
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
