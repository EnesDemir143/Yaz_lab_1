import pandas as pd
from fastapi import APIRouter, Depends, UploadFile, File
from Backend.src.DataBase.src.structures.classrooms import Classroom
from Backend.src.DataBase.src.structures.user import User
from Backend.src.DataBase.src.utils.class_list_menu import class_list_menu
from Backend.src.DataBase.src.utils.insert_classroom import insert_classroom_to_db
from Backend.src.DataBase.src.utils.student_list_menu import student_list_menu
from Backend.src.services.Utils.check_if_admin import require_admin
from Backend.src.DataBase.scripts.class_list_save_from_excel import class_list_save_from_excel
from Backend.src.DataBase.scripts.student_list_save_from_excel import student_list_save_from_excel
import io

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/admin_dashboard")
def admin_dashboard(user: User = Depends(require_admin)):
    pass

@router.get("/insert_coordinator")
def insert_coordinator(user: User = Depends(require_admin)):
    

@router.post("/upload_classes_list") 
async def upload_classes_list(user: User = Depends(require_admin), file: UploadFile = File(...)):
    contents = await file.file.read().decode("utf-8")
    
    df = pd.read_excel(io.BytesIO(contents), sheet_name="Ders Listesi", header=None)
    
    status, msg = class_list_save_from_excel(df, department=user.department)
    
    if status == 'error' and status != 'success':
        return {"message": "Error while uploading class list.", 'status': status, 'detail': msg}
    
    return {"message": "Class list uploaded successfully", 'status': status, 'detail': msg}


@router.post("/upload_students_list")
async def upload_students_list(user: User = Depends(require_admin), file: UploadFile = File(...)):
    contents = await file.file.read().decode("utf-8")
    
    df = pd.read_excel(io.BytesIO(contents))
    
    return_dict = student_list_save_from_excel(df, department=user.department)
    
    status = return_dict.get('status', 'error')
    msg = return_dict.get('msg', '')
    
    if status == 'error' and status != 'success':
        return {"message": "Error while uploading student list.", 'status': status, 'detail': msg}
    
    return {"message": "Student list uploaded successfully", 'status': status, 'detail': msg}

@router.post("/student_list_filter")
def student_list_filter(student_num: str, user: User = Depends(require_admin)):
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
        classes.append((record.get('class_name'), record.get('class_code')))
        
    return {'name': name, 'surname': surname, 'classes': classes, "message": "Records fetched successfully.", 'status': 'success'}

@router.post("/all_classes")
def all_classes(department: str, user: User = Depends(require_admin)):
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