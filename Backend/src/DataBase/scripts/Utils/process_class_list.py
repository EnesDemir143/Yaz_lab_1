import os
import re
import pandas as pd
from Backend.src.DataBase.src.utils.get_year_from_str import get_year_from_str

def process_class_list(path: str, save_path:str, sheet_name: str = "Ders Listesi") -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name=sheet_name, header=None)

    sinif_rows = df[df[0].astype(str).str.contains("Sınıf", case=False, na=False)].reset_index()

    rows = []
    for i in range(len(sinif_rows)):
        start = sinif_rows.loc[i, "index"] + 2 
        end = sinif_rows.loc[i+1, "index"] if i+1 < len(sinif_rows) else len(df)
        sinif_text = str(df.loc[sinif_rows.loc[i, "index"], 0])

        sinif = get_year_from_str(sinif_text)

        block = df.iloc[start:end, :3].copy()
        block.columns = ["DERS KODU", "DERSİN ADI", "DERSİ VEREN ÖĞR. ELEMANI"]
        secmeli_mask = block["DERS KODU"].astype(str).str.contains("Seçimlik|Seçmeli", case=False, na=False)

        if secmeli_mask.any():
            secmeli_index = secmeli_mask.idxmax()
            block = block.drop(secmeli_index)
            
            block["Seçmeli mi?"] = False
            block.loc[secmeli_index+1:, "Seçmeli mi?"] = True
        else:
            block["Seçmeli mi?"] = False

        block["SINIF"] = sinif
        rows.append(block)

    final_df = pd.concat(rows, ignore_index=True)
    
    final_df = final_df[~final_df["DERS KODU"].isin(['DERS KODU', 'DERSİN ADI', 'DERSİ VEREN ÖĞR. ELEMANI'])]
    
    if not os.path.exists(save_path):
        final_df.to_excel(save_path, index=False)
    
    return final_df