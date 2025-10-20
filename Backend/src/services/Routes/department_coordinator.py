from typing import Any
from Backend.src.DataBase.src.utils.insert_exam_schedule import insert_exam_schedule
from Backend.src.DataBase.src.utils.update_classroom import update_classroom as db_update_classroom
from Backend.src.DataBase.src.utils.class_list_menu import class_list_menu
from Backend.src.DataBase.src.utils.student_list_menu import student_list_menu, student_list_for_department
from Backend.src.DataBase.scripts.class_list_save_from_excel import class_list_save_from_excel
from Backend.src.DataBase.scripts.student_list_save_from_excel import student_list_save_from_excel
from Backend.src.DataBase.src.utils.insert_classroom import insert_classroom_to_db
from Backend.src.DataBase.src.structures.classrooms import Classroom
import pandas as pd
from fastapi import APIRouter, Body, Depends, Form, UploadFile, File
from Backend.src.DataBase.src.structures.user import User
from Backend.src.services.Utils.check_if_coordinator import require_coordinator
from Backend.src.DataBase.src.utils.search_classroom import search_classroom as db_search_classroom
from Backend.src.DataBase.src.utils.delete_classroom import delete_classroom as db_delete_classroom
from Backend.src.DataBase.src.utils.get_all_classrooms import get_all_classrooms 
from Backend.src.DataBase.src.utils.read_exam_program import read_exam_schedule_by_department
from Backend.src.DataBase.src.utils.delete_stutent_list import delete_students
from Backend.src.DataBase.src.utils.delete_classes import delete_classes
import io

router = APIRouter(prefix="/department_coordinator", tags=["department_coordinator"])


@router.post("/upload_classes_list") 
async def upload_classes_list(user: User = Depends(require_coordinator), file: UploadFile = File(...)):    
    contents = await file.read()
    
    result = delete_classes(user.department)
    if result.get('status') == 'error' and result.get('status') != 'success':
        return {"message": "Error while deleting existing class list.", 'status': 'error', 'detail': result.get('errors', '')}
    
    df = pd.read_excel(io.BytesIO(contents), sheet_name="Ders Listesi", header=None)
    
    status, msg = class_list_save_from_excel(df, department=user.department)
    
    if status == 'error' and status != 'success':
        return {"message": "Error while uploading class list.", 'status': status, 'detail': msg}
    
    return {"message": "Class list uploaded successfully", 'status': status, 'detail': msg}


@router.post("/upload_students_list")
async def upload_students_list(user: User = Depends(require_coordinator), file: UploadFile = File(...)): 
    contents = await file.read()
    
    result = delete_students(user.department)
    if result.get('status') == 'error' and result.get('status') != 'success':
        return {"message": "Error while deleting existing student list.", 'status': 'error', 'detail': result.get('errors', '')}
    
    df = pd.read_excel(io.BytesIO(contents))
    
    return_dict = student_list_save_from_excel(df, department=user.department)
    
    status = return_dict.get('status', 'error')
    msg = return_dict.get('msg', '')
    
    if status == 'error' and status != 'success':
        return {"message": "Error while uploading student list.", 'status': status, 'detail': msg}
    
    return {"message": "Student list uploaded successfully", 'status': status, 'detail': msg}

@router.post("/student_list_filter")
def student_list_filter(student_num: str = Form(...), user: User = Depends(require_coordinator)):
    name, surname, classes = None, None, []
    
    try:
        student_num_int = int(student_num)
    except ValueError:
        return {'name': name, 'surname': surname, 'classes': classes, "message": "Invalid student number format.", 'status': 'error'}
    
    students_and_classes = student_list_menu(student_num_int)

    if not students_and_classes:
        return {'name': name, 'surname': surname, 'classes': classes, "message": "No records found for the given student number.", 'status': 'error'}
    
    for record in students_and_classes:
        if name is None:
            name = record.get('name')
        if surname is None:
            surname = record.get('surname')
        classes.append((record.get('class_name'), record.get('class_id')))
        
    return {'name': name, 'surname': surname, 'classes': classes, "message": "Records fetched successfully.", 'status': 'success'}

@router.get("/all_classes")
def all_classes(user: User = Depends(require_coordinator)):
    class_dict = {}

    try:
        classes_list, status, msg = class_list_menu(user.department)

        if status == 'error':
            return {
                'classes': {},
                "message": "Error while fetching classes.",
                'status': 'error',
                'detail': msg
            }

        for cls in classes_list:
            class_id = cls['class_id']

            if class_id not in class_dict:
                class_dict[class_id] = {
                    'class_id': class_id,
                    'class_name': cls['class_name'],
                    'students': []
                }

            if cls['student_num']:
                class_dict[class_id]['students'].append({
                    'student_num': cls['student_num'],
                    'name': cls['name'],
                    'surname': cls['surname']
                })

    except Exception as e:
        return {
            'classes': class_dict,
            "message": "Error while fetching classes.",
            'status': 'error',
            'detail': str(e)
        }

    return {
        'classes': class_dict,
        "message": "Classes fetched successfully.",
        'status': 'success',
        'detail': msg
    }
    
@router.get("/just_classes")
def just_classes(user: User = Depends(require_coordinator)):
    try:
        classes_list, status, msg = class_list_menu(user.department)
        
        if status == 'error' and status != 'success':
            return {"classes": [], "message": "Error while fetching classes.", 'status': status, 'detail': msg}
        
        unique_classes = {cls['class_id']: cls['class_name'] for cls in classes_list}
        classes = [(cid, cname) for cid, cname in unique_classes.items()]
        
    except Exception as e:
        return {"classes": [], "message": "Error while fetching classes.", 'status': 'error', 'detail': str(e)}
        
    return {"classes": classes, "message": "Classes fetched successfully.", 'status': status, 'detail': msg}

@router.get("/classes_with_years")
def classes_with_years(user: User = Depends(require_coordinator)):
    class_dict = {}

    try:
        classes_list, status, msg = class_list_menu(user.department, years_and_instructor=True)

        if status == 'error':
            return {
                'classes': {},
                "message": "Error while fetching classes.",
                'status': 'error',
                'detail': msg
            }

        for cls in classes_list:
            class_id = cls['class_id']

            if class_id not in class_dict:
                class_dict[class_id] = {
                    'class_id': class_id,
                    'class_name': cls['class_name'],
                    'year': cls.get('year', []),
                    'instructor': cls.get('teacher', ''),
                    'students': []
                }

            if cls['student_num']:
                class_dict[class_id]['students'].append({
                    'student_num': cls['student_num'],
                    'name': cls['name'],
                    'surname': cls['surname']
                })

    except Exception as e:
        return {
            'classes': class_dict,
            "message": "Error while fetching classes.",
            'status': 'error',
            'detail': str(e)
        }

    return {
        'classes': class_dict,
        "message": "Classes fetched successfully.",
        'status': 'success',
        'detail': msg
    }
    
@router.post("/insert_classroom")
def insert_classroom(classroom: Classroom, user: User = Depends(require_coordinator)):
        status, msg = insert_classroom_to_db(classroom)
        
        if status == 'error' and status != 'success':
            return {"message": "Error while inserting/updating classroom.", 'status': status, 'detail': msg}
        
        return {"message": "Classroom inserted/updated successfully.", 'status': status, 'detail': msg}

@router.post("/search_classroom")
def search_classroom(classroom_code: str, user: User = Depends(require_coordinator)):
    result, status, msg = db_search_classroom(classroom_code)
    
    if status == 'error' and status != 'success':
        return {"message": "Error while searching for classroom.", 'status': status, 'detail': msg}
    
    return {"classroom": result, "message": "Classroom found successfully.", 'status': status, 'detail': msg}

@router.post("/update_classroom")
def update_classroom(new_classroom_data: Classroom, user: User = Depends(require_coordinator)):
    status, msg = db_update_classroom(new_classroom_data)
    
    if status == 'error' and status != 'success':
        return {"message": "Error while updating classroom.", 'status': status, 'detail': msg}
    
    return {"message": "Classroom updated successfully.", 'status': status, 'detail': msg}

@router.post("/delete_classroom")
def delete_classroom(classroom_code: str, user: User = Depends(require_coordinator)):
    status, msg = db_delete_classroom(classroom_code)
    
    if status == 'error' and status != 'success':
        return {"message": "Error while deleting classroom.", 'status': status, 'detail': msg}
    
    return {"message": "Classroom deleted successfully.", 'status': status, 'detail': msg}

@router.get("/exam_classrooms")
def exam_classrooms(user: User = Depends(require_coordinator)):
    try:
        classrooms_list, status, msg = get_all_classrooms(user.department)
        
        if status == 'error':
            print(f"Error while fetching exam classrooms: {msg}")
            return {
                "classrooms": [],
                "message": "Error while fetching exam classrooms.",
                'status': 'error',
                'detail': msg
            }
            
        print(f"Fetched {len(classrooms_list)} exam classrooms for department {user.department}")
        for cls in classrooms_list:
            print(f"Classroom ID: {cls['classroom_id']}, Name: {cls['classroom_name']}, Capacity: {cls['capacity']}")
        
        return {
            "classrooms": classrooms_list,
            "message": "Exam classrooms fetched successfully.",
            'status': 'success',
            'detail': msg
        }
        
    except Exception as e:
        print(f"Exception while fetching exam classrooms: {e}")
        return {
            "classrooms": [],
            "message": "Error while fetching exam classrooms.",
            'status': 'error',
            'detail': str(e)
        }
        
@router.post("/insert_exam_schedule_to_db")
def insert_exam_schedule_db(exam_schedule: Any = Body(...), user: User = Depends(require_coordinator)):
    print("📥 Raw exam_schedule string alındı")
    status, msg = insert_exam_schedule(exam_schedule, n_jobs=6)
    
    if status == 'error':
        print("Error while inserting exam schedule to db.")
        raise ValueError("Error while inserting exam schedule to db.")
    
    return {
        "status": status,
        "message": msg
    }

@router.get("/get_exam_schedule")
def get_exam_schedule(user: User = Depends(require_coordinator)):
    
    result = read_exam_schedule_by_department(user.department)
    
    return result

@router.get("/check_students_exist")
def check_students_exist(user: User = Depends(require_coordinator)):
    try:
        students_and_classes = student_list_for_department(department=user.department)

        if not students_and_classes:
            return {'students': False, "message": "No students found in the database for this department.", 'status': 'success'}
        
        return {'students': True, "message": "Students exist in the database for this department.", 'status': 'success'}
        
    except Exception as e:
        return {'students': False, "message": "Error while checking for students.", 'status': 'error', 'detail': str(e)}