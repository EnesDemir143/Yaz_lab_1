from Backend.src.DataBase.src.Database_connection import get_database
from Backend.src.DataBase.src.structures.classrooms import Classroom

def update_classroom(new_classroom_data: Classroom):
    try:
        with get_database() as db:
            with db.cursor() as cursor:
                query = """
                    UPDATE classrooms
                    SET classroom_name = %s,
                        department_name = %s,
                        capacity = %s,
                        desks_per_row = %s,
                        desks_per_column = %s,
                        desk_structure = %s
                    WHERE classroom_id = %s
                """
                cursor.execute(query, (
                    new_classroom_data.classroom_name,
                    new_classroom_data.department_name,
                    new_classroom_data.capacity,
                    new_classroom_data.desks_per_row,
                    new_classroom_data.desks_per_column,
                    new_classroom_data.desk_structure,
                    new_classroom_data.classroom_id
                ))
                if cursor.rowcount == 0:
                    return 'error', 'Classroom not found.'
    except Exception as e:
        return 'error', str(e)
    return 'success', 'Classroom updated successfully.'