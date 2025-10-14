from Backend.src.DataBase.src.Database_connection import get_database
import pymysql

def class_list_menu(department: str, years_and_instructor=False) -> list[dict]:
    try:
        with get_database() as db:
            with db.cursor(pymysql.cursors.DictCursor) as cursor:
                if years_and_instructor:
                    query = """
                    SELECT 
                        c.class_id,
                        c.class_name,
                        c.year,
                        c.teacher,
                        s.student_num,
                        s.name,
                        s.surname
                    FROM classes c
                    LEFT JOIN student_classes sc ON sc.class_id = c.class_id
                    LEFT JOIN students s ON s.student_num = sc.student_num
                    WHERE c.department = %s;
                    """ 
                else:
                    query = """
                    SELECT 
                        c.class_id,
                        c.class_name,
                        s.student_num,
                        s.name,
                        s.surname
                    FROM classes c
                    LEFT JOIN student_classes sc ON sc.class_id = c.class_id
                    LEFT JOIN students s ON s.student_num = sc.student_num
                    WHERE c.department = %s;
                    """
                cursor.execute(query, (department,))
                classes = cursor.fetchall()
    except Exception as e:
        print(f"Error while fetching classes: {e}")
        return [], 'error', str(e)
    return classes, 'success', 'Classes fetched successfully.'
            

            
            