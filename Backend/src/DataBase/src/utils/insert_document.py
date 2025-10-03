from Backend.src.DataBase.src.database_connection import get_database
from typing import Union, Dict, List


def insert_document(collection_name: str, document: Union[Dict, List[Dict]]) -> str:
    db = get_database()
