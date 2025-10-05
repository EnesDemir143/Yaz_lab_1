from Backend.src.DataBase.src.database_connection import get_database
import pandas as pd

def insert_students(students: pd.DataFrame) -> None:
    with get_database() as connection:
        with connection.cursor() as cursor:
            for _, student_info in students.iterrows():
                sql = """
                INSERT INTO students (student_id, name, surname, class, courses, department)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    name = VALUES(name),
                    surname = VALUES(surname),
                    class = VALUES(class),
                    courses = VALUES(courses),
                    department = VALUES(department)
                """
                cursor.execute(sql, (
                    student_info['student_num'],
                    student_info['name'],
                    student_info['surname'],
                    student_info['grade'],
                    ','.join(student_info['classes']),
                    student_info.get('department', None)
                ))