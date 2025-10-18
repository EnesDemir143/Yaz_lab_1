import os
import pandas as pd
from typing import List
from Backend.src.DataBase.src.utils.get_year_from_str import get_year_from_str

def process_class_list(df: pd.DataFrame, department, strict: bool = True) -> pd.DataFrame:

    sinif_rows = df[df[0].astype(str).str.contains("Sınıf", case=False, na=False)].reset_index()

    rows: List[pd.DataFrame] = []
    for i in range(len(sinif_rows)):
        start = sinif_rows.loc[i, "index"] + 2
        end = sinif_rows.loc[i + 1, "index"] if i + 1 < len(sinif_rows) else len(df)
        sinif_text = str(df.loc[sinif_rows.loc[i, "index"], 0])
        sinif = get_year_from_str(sinif_text)

        try:
            block = df.iloc[start:end, :3].copy()
            if block.shape[1] < 3:
                msg = (f"[HATA] {i}. sınıf bloğunda beklenen 3 sütun yok. "
                       f"Bulunan sütun sayısı: {block.shape[1]} | Aralık: [{start}, {end})")
                print(msg)
                if strict:
                    return {
                        'df': df,
                        'status': 'error',
                        'message': msg
                    }
                else:
                    continue

            block.columns = ["class_id", "class_name", "teacher"]

            # --- 🔽 ÖNCE özel/başlık/boş satırları ayıkla (doğrulamadan ÖNCE) ---
            # 1) "Seçmeli/Seçimlik" satırını düşür ve is_optional ata
            secmeli_mask = block["class_id"].astype(str).str.contains("Seçimlik|Seçmeli", case=False, na=False)
            if secmeli_mask.any():
                secmeli_index = secmeli_mask.idxmax()
                block = block.drop(secmeli_index)
                block["is_optional"] = False
                block.loc[block.index >= secmeli_index, "is_optional"] = True
            else:
                block["is_optional"] = False

            # 2) "class_id/class_name/teacher/DERS KODU" başlık benzeri satırları ele
            block = block[~block["class_id"].isin(['class_id', 'class_name', 'teacher', 'DERS KODU'])]

            # 3) Tamamen boş/whitespace olan satırları ele
            block = block[~(block.astype(str).apply(lambda s: s.str.strip()).eq("").all(axis=1))]

            # --- 🔽 ARTIK doğrulama döngüsü (boşluk hataları burada gerçek boş satırlara denk gelirse dursun) ---
            for ridx, r in block.iterrows():
                for col in ["class_id", "class_name", "teacher"]:
                    try:
                        val = str(r[col])
                        if val.strip().lower() in ["nan", "none", ""]:
                            raise ValueError("Boş değer")
                    except Exception as e_row:
                        excel_row_no = int(ridx) + 1
                        print(f"[HATA] Satır {excel_row_no}, sütun '{col}' işlenemedi.")
                        print(f"  - Sınıf: {sinif}")
                        print(f"  - Hata Türü: {type(e_row).__name__} | Mesaj: {e_row}")
                        print(f"  - Orijinal değer: {r.get(col, None)}\n")
                        block.at[ridx, col] = None  # hücreyi None olarak işaretle
                        if strict:
                            return {
                                'df': df,
                                'status': 'error',
                                'message': f"Satır {excel_row_no}, sütun '{col}' işlenemedi: {e_row}"
                            }

            block["grade"] = sinif
            block = block[~block["class_id"].isin(['class_id', 'class_name', 'teacher'])]

            rows.append(block)

        except Exception as e:
            print("\n[HATA] Bir sınıf bloğu işlenemedi:")
            print(f"  - Sınıf başlığı: '{sinif_text}' (çıkarılan yıl: {sinif})")
            print(f"  - Aralık: [{start}, {end})")
            print(f"  - Hata Türü: {type(e).__name__} | Mesaj: {e}\n")
            if strict:
                return {
                    'df': df,
                    'status': 'error',
                    'message': f"Sınıf bloğu işlenemedi: '{sinif_text}' | Hata: {e}"
                }
            else:
                continue

    if not rows:
        msg = "[HATA] Hiçbir blok üretilemedi. Girdi formatını kontrol edin."
        print(msg)
        if strict:
            raise ValueError(msg)
        return pd.DataFrame(columns=["DERS KODU", "DERSİN ADI", "DERSİ VEREN ÖĞR. ELEMANI", "Seçmeli mi?", "SINIF"])

    final_df = pd.concat(rows, ignore_index=True)
    final_df["department"] = department if department is not None else "Unknown"

    return {
        'df':final_df,
        'status':'success',
        'message':'Class list processed successfully.'
    }
