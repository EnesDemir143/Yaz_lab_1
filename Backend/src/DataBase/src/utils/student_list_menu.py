from Backend.src.DataBase.src.database_connection import DatabaseConnection
import pandas as pd

def student_list_menu(student_num: int) -> pd.DataFrame:
    db = DatabaseConnection.get_database()
    students_collection = db['students']
    classes_collection = db['classes']

    students = list(students_collection.find({'ÖĞRENCİ NO': student_num})) 

    classes = {}
    for student in students:
        dersler = student.get('DERSLER', [])  
        classes[student['Ad Soyad']] = []
        for ders_id in dersler:
            class_doc = classes_collection.find_one({'DERS KODU': ders_id}, {'DERSİN ADI': 1})
            if class_doc:
                classes[student['Ad Soyad']].append([ders_id, class_doc['DERSİN ADI']])
    
    df = pd.DataFrame({
        'name_surname': [student['Ad Soyad'] for student in students],
        'classes': [classes[student['Ad Soyad']] for student in students]
    })
    
    return df
