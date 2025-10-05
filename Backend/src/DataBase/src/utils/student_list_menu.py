from Backend.src.DataBase.src.Database_connection import get_database
import pymysql

def student_list_menu(student_num: int) -> list[dict]:
    with get_database() as db:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            query = 'SELECT * FROM students JOIN classes ON students.department = classes.department WHERE students.student_num = %s'
            cursor.execute(query, (student_num,))
            students_and_classes = cursor.fetchall()
            return students_and_classes

