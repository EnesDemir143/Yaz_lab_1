from Backend.src.DataBase.src.utils.update_classroom import update_classroom as db_update_classroom
import pandas as pd
from fastapi import APIRouter, Depends, UploadFile, File, Form
from Backend.src.DataBase.src.structures.classrooms import Classroom
from Backend.src.DataBase.src.structures.user import User
from Backend.src.DataBase.src.utils.class_list_menu import class_list_menu
from Backend.src.DataBase.src.utils.insert_classroom import insert_classroom_to_db
from Backend.src.DataBase.src.utils.student_list_menu import student_list_menu
from Backend.src.services.Utils.check_if_admin import require_admin
from Backend.src.DataBase.scripts.class_list_save_from_excel import class_list_save_from_excel
from Backend.src.DataBase.scripts.student_list_save_from_excel import student_list_save_from_excel
from Backend.src.DataBase.src.utils.insert_coordinator import insert_department_coordinator
from Backend.src.DataBase.src.utils.search_classroom import search_classroom as db_search_classroom
from Backend.src.DataBase.src.utils.delete_classroom import delete_classroom as db_delete_classroom
from Backend.src.DataBase.src.utils.get_departments import get_departments as db_get_departments
import io


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/insert_coordinator")
async def insert_coordinator(coordinator: User, user: User = Depends(require_admin)):
    status, msg = insert_department_coordinator(coordinator)
    
    if status == 'error' and status != 'success':
        return {"message": "Error while inserting coordinator.", 'status': status, 'detail': msg}
    
    return {"message": "Coordinator inserted successfully", 'status': status, 'detail': msg}
    
    

@router.post("/upload_classes_list") 
async def upload_classes_list(uploaded_department: str = Form(...), user: User = Depends(require_admin), file: UploadFile = File(...)):
    contents = await file.read()

    df = pd.read_excel(io.BytesIO(contents), sheet_name="Ders Listesi", header=None)
    
    status, msg = class_list_save_from_excel(df, department=uploaded_department)
    
    if status == 'error' and status != 'success':
        return {"message": "Error while uploading class list.", 'status': status, 'detail': msg}
    
    return {"message": "Class list uploaded successfully", 'status': status, 'detail': msg}


@router.post("/upload_students_list")
async def upload_students_list(uploaded_department: str = Form(...), user: User = Depends(require_admin),  file: UploadFile = File(...)):
    contents = await file.read()
    
    df = pd.read_excel(io.BytesIO(contents))
    
    return_dict = student_list_save_from_excel(df, department=uploaded_department)
    
    status = return_dict.get('status', 'error')
    msg = return_dict.get('msg', '')
    
    if status == 'error' and status != 'success':
        return {"message": "Error while uploading student list.", 'status': status, 'detail': msg}
    
    return {"message": "Student list uploaded successfully", 'status': status, 'detail': msg}

@router.post("/student_list_filter")
def student_list_filter(student_num: str = Form(...), user: User = Depends(require_admin)):
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

@router.post("/all_classes")
def all_classes(department: str = Form(...), user: User = Depends(require_admin)):
    class_dict = {}
    
    try:
        classes = class_list_menu(department)
        
        for cls in classes:
            if cls['class_id'] not in classes:
                classes[cls['class_id']] = {
                    'class_id': cls['class_id'],
                    'class_name': cls['class_name'],
                    'students': []
                }
            if cls['student_num']:
                classes[cls['class_id']]['students'].append({
                    'student_num': cls['student_num'],
                    'name': cls['name'],
                    'surname': cls['surname']
                })
        
    except Exception as e:
        return {'classes': class_dict, "message": "Error while fetching classes.", 'status': 'error', 'detail': str(e)}
    
    return {'classes': class_dict, "message": "Classes fetched successfully.", 'status': 'success'}

@router.post("/insert_classroom")
def insert_classroom(classroom: Classroom, user: User = Depends(require_admin)):
        status, msg = insert_classroom_to_db(classroom)
        
        if status == 'error' and status != 'success':
            return {"message": "Error while inserting/updating classroom.", 'status': status, 'detail': msg}
        
        return {"message": "Classroom inserted/updated successfully.", 'status': status, 'detail': msg}
    
@router.post("/search_classroom")
def search_classroom(classroom_code: str, user: User = Depends(require_admin)):
    result, status, msg = db_search_classroom(classroom_code)
    
    if status == 'error' and status != 'success':
        return {"message": "Error while searching for classroom.", 'status': status, 'detail': msg}
    
    return {"classroom": result, "message": "Classroom found successfully.", 'status': status, 'detail': msg}

@router.post("/update_classroom")
def update_classroom(new_classroom_data: Classroom, user: User = Depends(require_admin)):
    status, msg = db_update_classroom(new_classroom_data)
    
    if status == 'error' and status != 'success':
        return {"message": "Error while updating classroom.", 'status': status, 'detail': msg}
    
    return {"message": "Classroom updated successfully.", 'status': status, 'detail': msg}

@router.post("/delete_classroom")
def delete_classroom(classroom_code: str, user: User = Depends(require_admin)):
    status, msg = db_delete_classroom(classroom_code)
    
    if status == 'error' and status != 'success':
        return {"message": "Error while deleting classroom.", 'status': status, 'detail': msg}
    
    return {"message": "Classroom deleted successfully.", 'status': status, 'detail': msg}

@router.get("/get_departments")
def get_departments(user: User = Depends(require_admin)):
    db_get_departments()
    departments, status, msg = db_get_departments()
    
    if status == 'error' and status != 'success':
        return {"message": "Error while fetching departments.", 'status': status, 'detail': msg}
    
    return {"departments": departments, "message": "Departments fetched successfully.", 'status': status, 'detail': msg}