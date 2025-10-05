from Backend.src.DataBase.scripts.Utils.process_class_list import process_class_list
from Backend.src.DataBase.src.utils.insert_classes import insert_classes
import pandas as pd

def class_list_save_from_excel(df: pd.DataFrame, department:str):
    ders_listesi_df, status, msg = process_class_list(df, department, sheet_name="Ders Listesi")
    
    if status == 'error' and status != 'success':
        print("Error while processing class list.", msg)
        return status, msg
        
                
    class_list = ders_listesi_df.to_dict(orient="records")
    
    try:
        insert_classes(class_list)
    except Exception as e:
        print("Error while inserting classes.", e)
        raise
    
    
    