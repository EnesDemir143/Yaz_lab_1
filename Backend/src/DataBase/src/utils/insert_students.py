from Backend.src.DataBase.src.Database_connection import get_database
import pandas as pd

def insert_students(students: pd.DataFrame) -> None:
    with get_database() as connection:
        with connection.cursor() as cursor:
            for _, student_info in students.iterrows():
                sql = """
                INSERT INTO students (student_id, name, surname, grade, department)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    name = VALUES(name),
                    surname = VALUES(surname),
                    grade = VALUES(grade),
                    department = VALUES(department)
                """
                cursor.execute(sql, (
                    student_info['student_num'],
                    student_info['name'],
                    student_info['surname'],
                    student_info['grade'],
                    student_info.get('department', None)
                ))
                
                sql_2 = """
                INSERT INTO student_classes (student_id, class_id) 
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE
                    class_id = VALUES(class_id)
                """
                class_codes = student_info['classes'].split(',') if pd.notna(student_info['classes']) else []
                for class_code in class_codes:
                    cursor.execute(sql_2, (student_info['student_num'], class_code.strip()))