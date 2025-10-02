from Backend.src.DataBase.scripts.Utils.process_class_list import process_class_list
from Backend.src.DataBase.src.utils.insert_document import insert_document
import pandas as pd

def read_save_from_excel(path: str, save_path: str) -> pd.DataFrame:
    ders_listesi_df = process_class_list(path, save_path, sheet_name="Ders Listesi")
    
    classes = ders_listesi_df.to_dict(orient='records')
    
    insert_document("classes", classes)
    
    return ders_listesi_df