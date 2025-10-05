from Backend.src.DataBase.src.Database_connection import get_database
import pymysql

def class_list_menu(department: str) -> list[dict]:
    with get_database() as db:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            query = """
            SELECT 
                c.class_id,
                c.class_name,
                s.student_num,
                s.name,
                s.surname
            FROM classes c
            LEFT JOIN student_classes sc ON sc.class_id = c.class_id
            LEFT JOIN students s ON s.student_num = sc.student_num;
            """
            cursor.execute(query, (department,))
            classes = cursor.fetchall()
    return classes
            

            
            