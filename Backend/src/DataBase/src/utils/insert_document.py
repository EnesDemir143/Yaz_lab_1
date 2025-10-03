from Backend.src.DataBase.src.database_connection import get_database
from typing import Union, Dict, List


def insert_document(collection_name: str, document: Union[Dict, List[Dict]]) -> str:
    db = get_database()
    collection = db[collection_name]

    if isinstance(document, list):
        result = collection.insert_many(document)
        return ','.join(str(id) for id in result.inserted_ids)
    else:
        result = collection.insert_one(document)    

    return str(result.inserted_id)
