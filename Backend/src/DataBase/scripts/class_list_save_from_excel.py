from Backend.src.DataBase.scripts.Utils.process_class_list import process_class_list
import pandas as pd

def class_list_save_from_excel(path: str, save_path: str, department:str) -> None:
    ders_listesi_df = process_class_list(path, save_path, sheet_name="Ders Listesi")
        
    if department is not None:
        ders_listesi_df['department'] = department
        
    classes = ders_listesi_df.to_dict(orient='records')
    
    
    