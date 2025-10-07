from Backend.src.DataBase.src.Database_connection import get_database
from typing import Union, List
import pymysql

def delete_classroom(classroom_id: Union[List[str], str]) -> None:
    try:
        with get_database() as db:
            with db.cursor(pymysql.cursors.DictCursor) as cursor:
                if isinstance(classroom_id, List):
                    format_strings = ','.join(['%s'] * len(classroom_id))
                    sql = f"DELETE FROM classrooms WHERE `classroom_id` IN ({format_strings})"
                    cursor.execute(sql, classroom_id)
                else:
                    sql = "DELETE FROM classrooms WHERE `classroom_id` = %s"
                    cursor.execute(sql, (classroom_id,))
    except Exception as e:
        return 'error', str(e)
    return 'success', 'Classroom updated successfully.'                
    