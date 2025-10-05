from Backend.src.DataBase.src.utils.student_list_menu import student_list_menu
from Backend.src.DataBase.scripts.class_list_save_from_excel import class_list_save_from_excel
from Backend.src.DataBase.scripts.student_list_save_from_excel import student_list_save_from_excel
import pandas as pd
from fastapi import APIRouter, Depends, UploadFile, File
from Backend.src.DataBase.src.structures.user import User
from Backend.src.services.Utils.check_if_coordinator import require_coordinator

import io

router = APIRouter(prefix="/department_coordinator", tags=["department_coordinator"])

@router.get("/coordinator_dashboard")
def coordinator_dashboard(user: User = Depends(require_coordinator)):
    pass

@router.post("/upload_classes_list") 
async def upload_classes_list(user: User = Depends(require_coordinator), file: UploadFile = File(...)):
    contents = await file.file.read().decode("utf-8")
    
    df = pd.read_excel(io.BytesIO(contents), sheet_name="Ders Listesi", header=None)
    
    status, msg = class_list_save_from_excel(df, department=user.department)
    
    if status == 'error' and status != 'success':
        return {"message": "Error while uploading class list.", 'status': status, 'detail': msg}
    
    return {"message": "Class list uploaded successfully", 'status': status, 'detail': msg}


@router.post("/upload_students_list")
async def upload_students_list(user: User = Depends(require_coordinator), file: UploadFile = File(...)):
    contents = await file.file.read().decode("utf-8")
    
    df = pd.read_excel(io.BytesIO(contents))
    
    return_dict = student_list_save_from_excel(df, department=user.department)
    
    status = return_dict.get('status', 'error')
    msg = return_dict.get('msg', '')
    
    if status == 'error' and status != 'success':
        return {"message": "Error while uploading student list.", 'status': status, 'detail': msg}
    
    return {"message": "Student list uploaded successfully", 'status': status, 'detail': msg}

@router.post("/student_list_filter")
def student_list_filter(student_num: str, user: User = Depends(require_coordinator)):
    
    try:
        student_num_int = int(student_num)
    except ValueError:
        return {"message": "Invalid student number format.", 'status': 'error', 'data': None}
    
    students_and_classes = student_list_menu(student_num_int)
    
    name, surname, classes = None, None, []
    for record in students_and_classes:
        if name is None:
            name = record.get('name')
        if surname is None:
            surname = record.get('surname')
        classes.append((record.get('class_name'), record.get('class_code')))
        
    
    if not students_and_classes:
        return {"message": "No records found for the given student number.", 'status': 'error', 'data': None}
    
    return {"message": "Records retrieved successfully.", 'status': 'success', 'data': students_and_classes}