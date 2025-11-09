from Backend.src.DataBase.src.Database_connection import get_database


def delete_students(department: str):
    try:
        with get_database() as connection:
            with connection.cursor() as cursor:

                sql_delete_classes = """
                DELETE FROM student_classes WHERE student_num IN (
                    SELECT student_num FROM students WHERE department = %s
                )
                """
                cursor.execute(sql_delete_classes, (department,))

                sql_delete_student = """
                DELETE FROM students WHERE department = %s
                """
                cursor.execute(sql_delete_student, (department,))

        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
