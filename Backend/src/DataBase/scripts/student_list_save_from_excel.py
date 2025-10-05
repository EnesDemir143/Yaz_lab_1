from Backend.src.DataBase.src.utils.get_year_from_str import get_year_from_str
from Backend.src.DataBase.src.utils.insert_students import insert_students
import pandas as pd

def student_list_save_from_excel(student_list_df, department: str) -> None:
    
    students_df: pd.DataFrame = pd.DataFrame()
    
    try:
        student_list_df['Sınıf'] = student_list_df['Sınıf'].apply(get_year_from_str)
    except Exception as e:
        return {
            'df': students_df,
            'status': 'error',
            'msg': f"[HATA] 'Sınıf' sütunu işlenirken hata oluştu: {e}"
        }

    for idx, row in student_list_df.iterrows():
        excel_row = idx + 2  
        try:
            required_cols = ['Ad Soyad', 'ÖĞRENCİ NO', 'Sınıf', 'DERSLER']
            for col in required_cols:
                if col not in row or pd.isna(row[col]) or str(row[col]).strip() == "":
                    return {
                        'status': 'error',
                        'msg': f"[HATA] Satır {excel_row}: '{col}' sütunu eksik veya boş."
                    }

            try:
                name, surname = row['Ad Soyad'].split(' ', 1)
            except Exception as e_name:
                return {
                    'status': 'error',
                    'msg': f"[HATA] Satır {excel_row}: 'Ad Soyad' sütunu okunamadı veya geçersiz formatta | {e_name}"
                }
                
            try:
                classes = [c.strip() for c in str(row['DERSLER']).split(',') if c.strip()]
            except Exception as e_class:
                return {
                    'status': 'error',
                    'msg': f"[HATA] Satır {excel_row}: 'DERSLER' sütunu okunamadı veya geçersiz formatta | {e_class}"
                }

            student_info = {
                'student_num': row['ÖĞRENCİ NO'],
                'name': name,
                'surname': surname,
                'grade': row['Sınıf'],
                'classes': classes,
                'department': department
            }

            students_df = pd.concat([students_df, pd.DataFrame([student_info])], ignore_index=True)

        except Exception as e_row:
            return {
                'status': 'error',
                'msg': f"[HATA] Satır {excel_row}: İşlenirken hata oluştu | {e_row}"
            }

    try:
        insert_students(students_df)
    except Exception as e_insert:
        return {
            'status': 'error',
            'msg': f"[HATA] Öğrenciler veritabanına eklenirken hata oluştu | {e_insert}"
        }

    return {
        'status': 'success',
        'msg': f"{len(students_df)} öğrenci başarıyla eklendi."
    }
