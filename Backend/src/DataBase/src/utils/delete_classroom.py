from Backend.src.DataBase.src.utils.get_database import get_database
from typing import Union, List

def delete_classroom(classroom_id: Union[List[str], str]) -> bool:
    try:
        db = get_database()
    except Exception as e:
        raise ValueError(f"Error connecting to database: {e}")
    
    classrooms_collection = db["classrooms"]
    try:
        if isinstance(classroom_id, list):
            result = classrooms_collection.delete_many({"classroom_id": {"$in": classroom_id}})
        else:
            result = classrooms_collection.delete_one({"classroom_id": classroom_id})
    except Exception as e:
        raise ValueError(f"Error deleting classroom(s): {e}")