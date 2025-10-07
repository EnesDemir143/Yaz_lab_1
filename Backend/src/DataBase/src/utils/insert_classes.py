from Backend.src.DataBase.src.Database_connection import get_database
import pandas as pd

def insert_classes(classes: pd.DataFrame) -> None:
    with get_database() as connection:
        with connection.cursor() as cursor:
            for _, class_info in classes.iterrows():
                sql = """
                INSERT INTO classes (class_id, class_name, is_optional, teacher, department)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    class_name = VALUES(class_name),
                    is_optional = VALUES(is_optional),
                    teacher = VALUES(teacher),
                    department = VALUES(department)
                """
                cursor.execute(sql, (
                    class_info['class_id'],
                    class_info['class_name'],
                    class_info['is_optional'],
                    class_info['teacher'],
                    class_info.get('department', None)
                ))