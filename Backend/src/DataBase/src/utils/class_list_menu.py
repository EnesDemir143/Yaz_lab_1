from Backend.src.DataBase.src.database_connection import get_database

def class_list_menu(department: str) -> list[dict]:
    db = get_database()
    classes_collection = db['classes']
    classes = list(classes_collection.find({'department': department}))
    return classes