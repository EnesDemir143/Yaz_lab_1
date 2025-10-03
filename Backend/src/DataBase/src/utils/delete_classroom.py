from Backend.src.DataBase.src.database_connection import get_database
from typing import Union, List

def delete_classroom(classroom_id: Union[List[str], str]) -> bool:
    try:
        db = get_database()
    except Exception as e:
        raise ValueError(f"Error connecting to database: {e}")
    
    if isinstance(classroom_id, List):
        format_strings = ','.join(['%s'] * len(classroom_id))
        query = f"DELETE FROM classrooms WHERE id IN ({format_strings})"
        params = tuple(classroom_id)
    else:
        query = "DELETE FROM classrooms WHERE id = %s"
        params = (classroom_id,)
        
    try:
        cursor = db.cursor()
        cursor.execute(query, params)
        db.commit()
        cursor.close()
        db.close()
        return True
    except Exception as e:
        raise ValueError(f"Error executing delete operation: {e}")