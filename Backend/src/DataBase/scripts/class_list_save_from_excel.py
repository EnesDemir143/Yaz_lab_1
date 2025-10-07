from Backend.src.DataBase.scripts.Utils.process_class_list import process_class_list
from Backend.src.DataBase.src.utils.insert_classes import insert_classes
import pandas as pd

def class_list_save_from_excel(df: pd.DataFrame, department:str):
    return_dict = process_class_list(df, department)
    
    ders_listesi_df = return_dict.get('df', df)
    status = return_dict.get('status', 'error')
    msg = return_dict.get('message', 'Bilinmeyen hata')
    
    if status == 'error' and status != 'success':
        print("Error while processing class list.", msg)
        return status, msg
               
    
    try:
        insert_classes(ders_listesi_df)
    except Exception as e:
        print("Error while inserting classes.", e)
        raise
    
    return status, msg
    
    
    