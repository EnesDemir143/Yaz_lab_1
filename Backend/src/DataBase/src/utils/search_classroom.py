from Backend.src.DataBase.src.Database_connection import get_database
from typing import Dict, List, Union
import pymysql

def search_classroom(classroom_code: str) -> Union[Dict, List[Dict]]:
    with get_database() as db:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM classrooms WHERE classroom_id = %s"
            cursor.execute(sql, (classroom_code, ))
            result = cursor.fetchone()
            if not result:
                return [], 'error', 'Classroom not found.'
            return result, 'success', 'Classroom found.'