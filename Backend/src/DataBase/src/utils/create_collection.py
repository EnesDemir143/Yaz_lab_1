from Backend.src.DataBase.src.database_connection import get_database


def create_collection(collection_name: str):
    db = get_database()
    if collection_name in db.list_collection_names():
        return f"Collection '{collection_name}' already exists."
    db.create_collection(collection_name)
    return f"Collection '{collection_name}' created successfully."