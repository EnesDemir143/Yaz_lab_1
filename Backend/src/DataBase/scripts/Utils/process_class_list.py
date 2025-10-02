import re
import pandas as pd

def oku_ders_listesi(path: str, sheet_name: str = "Ders Listesi") -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name=sheet_name, header=None)

    sinif_rows = df[df[0].astype(str).str.contains("Sınıf", case=False, na=False)].reset_index()

    rows = []
    for i in range(len(sinif_rows)):
        start = sinif_rows.loc[i, "index"] + 2 
        end = sinif_rows.loc[i+1, "index"] if i+1 < len(sinif_rows) else len(df)
        sinif_text = str(df.loc[sinif_rows.loc[i, "index"], 0])

        sinif_match = re.search(r'(\d+)', sinif_text)
        sinif = int(sinif_match.group(1)) if sinif_match else 0

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
    
    final_df.to_excel("processed_ders_listesi.xlsx", index=False)
    
    return final_df