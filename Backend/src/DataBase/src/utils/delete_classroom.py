from Backend.src.DataBase.src.database_connection import get_database
from typing import Union, List
import pymysql

def delete_classroom(classroom_id: Union[List[str], str]) -> bool:
    with get_database() as db:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            if isinstance(classroom_id, list):
                format_strings = ','.join(['%s'] * len(classroom_id))
                sql = f"DELETE FROM classes WHERE `DERS KODU` IN ({format_strings})"
                cursor.execute(sql, classroom_id)
            else:
                sql = "DELETE FROM classes WHERE `DERS KODU` = %s"
                cursor.execute(sql, (classroom_id,))
            
        