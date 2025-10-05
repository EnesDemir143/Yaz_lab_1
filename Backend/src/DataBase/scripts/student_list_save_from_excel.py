from Backend.src.DataBase.src.utils.get_year_from_str import get_year_from_str
from Backend.src.DataBase.src.utils.insert_students import insert_students
import pandas as pd

def student_list_save_from_excel(path: str, department: str) -> None:
    student_list_df = pd.read_excel(path)
    
    student_list_df['Sınıf'] = student_list_df['Sınıf'].apply(get_year_from_str)
    
    students_df: pd.DataFrame = pd.DataFrame()

    for _, row in student_list_df.iterrows():
        name, surname = row['Ad Soyad'].split(' ', 1)
        student_info = {
            'student_num': row['ÖĞRENCİ NO'],
            'name': name,
            'surname': surname,
            'grade': row['Sınıf'],
            'classes': [course.strip() for course in row['DERSLER'].split(',')],
            'department': department
        }
        
        students_df = students_df.append(student_info, ignore_index=True)
    
    try:
        insert_students(students_df)
    except Exception as e:
        print("Error while inserting students.", e)
        raise