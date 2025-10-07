from Backend.src.DataBase.src.Database_connection import get_database
import pymysql

def student_list_menu(student_num: int) -> list[dict]:
    with get_database() as db:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            query = 'SELECT s.name, s.surname, c.class_name, c.class_id ' \
                    'FROM students s ' \
                    'LEFT JOIN student_classes sc ON s.student_num = sc.student_num ' \
                    'LEFT JOIN classes c ON sc.class_id = c.class_id ' \
                    'WHERE s.student_num = %s'
            cursor.execute(query, (student_num,))
            students_and_classes = cursor.fetchall()
            return students_and_classes

