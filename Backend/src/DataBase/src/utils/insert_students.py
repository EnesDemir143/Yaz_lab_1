from Backend.src.DataBase.src.Database_connection import get_database
import pandas as pd

def insert_students(students: pd.DataFrame) -> None:
    with get_database() as connection:
        with connection.cursor() as cursor:
            for _, student_info in students.iterrows():
                sql = """
                INSERT INTO students (student_num, name, surname, grade, department)
                VALUES (%s, %s, %s, %s, %s)
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
                INSERT INTO student_classes (student_num, class_id) 
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE
                    class_id = VALUES(class_id)
                """
                
                classes_value = student_info['classes']
                if isinstance(classes_value, list):
                    class_codes = classes_value
                elif pd.notna(classes_value):
                    class_codes = [c.strip() for c in str(classes_value).split(',')]
                else:
                    class_codes = []

                for class_code in class_codes:
                    cursor.execute(sql_2, (student_info['student_num'], class_code.strip()))