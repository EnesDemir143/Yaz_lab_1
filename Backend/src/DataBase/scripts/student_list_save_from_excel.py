from Backend.src.DataBase.src.utils.insert_document import insert_document
from Backend.src.DataBase.src.utils.get_year_from_str import get_year_from_str
import pandas as pd

def student_list_save_from_excel(path: str, department: str) -> None:
    student_list_df = pd.read_excel(path)
    
    student_list_df['Sınıf'] = student_list_df['Sınıf'].apply(get_year_from_str)
    
    students_dict = {}

    for _, row in student_list_df.iterrows():
        student_num = row["ÖĞRENCİ NO"]

        if student_num not in students_dict:
            students_dict[student_num] = {
                "ÖĞRENCİ NO": student_num,
                "Ad Soyad": row["Ad Soyad"],
                "SINIF": row["Sınıf"],
                "DERSLER": [],
                "BÖLÜM": department
            }

        students_dict[student_num]["DERSLER"].append(row["DERS KODU"])

    students = list(students_dict.values())
    
    insert_document("students", students)
    