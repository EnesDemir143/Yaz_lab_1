from Backend.src.DataBase.src.Database_connection import get_database
from Backend.src.DataBase.src.structures.classrooms import Classroom

def insert_classroom_to_db(classroom: Classroom):
    try:
        with get_database() as db:
            with db.cursor() as cursor:
                query = """
                    INSERT INTO classrooms (classroom_id, classroom_name, department_name, capacity, desks_per_row, desk_per_column, desk_structure)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        classroom_name = VALUES(classroom_name),
                        department_name = VALUES(department_name),
                        capacity = VALUES(capacity),
                        desks_per_row = VALUES(desks_per_row),
                        desk_per_column = VALUES(desk_per_column),
                        desk_structure = VALUES(desk_structure)
                """
                cursor.execute(query, (
                    classroom.classroom_id,
                    classroom.classroom_name,
                    classroom.department_name,
                    classroom.capacity,
                    classroom.desks_per_row,
                    classroom.desk_per_column,
                    classroom.desk_structure
                ))
    except Exception as e:
        return 'error', str(e)
    return 'success', 'Classroom inserted/updated successfully.'