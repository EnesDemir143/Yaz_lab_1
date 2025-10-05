from Backend.src.DataBase.scripts.Utils.process_class_list import process_class_list
from Backend.src.DataBase.src.utils.insert_classes import insert_classes

def class_list_save_from_excel(path: str, save_path: str, department:str) -> None:
    ders_listesi_df = process_class_list(path, save_path, department, sheet_name="Ders Listesi")
                
    class_list = ders_listesi_df.to_dict(orient="records")
    
    try:
        insert_classes(class_list)
    except Exception as e:
        print("Error while inserting classes.", e)
        raise
    
    
    