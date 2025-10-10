from Backend.src.DataBase.src.utils.update_classroom import update_classroom as db_update_classroom
from Backend.src.DataBase.src.utils.class_list_menu import class_list_menu
from Backend.src.DataBase.src.utils.student_list_menu import student_list_menu
from Backend.src.DataBase.scripts.class_list_save_from_excel import class_list_save_from_excel
from Backend.src.DataBase.scripts.student_list_save_from_excel import student_list_save_from_excel
from Backend.src.DataBase.src.utils.insert_classroom import insert_classroom_to_db
from Backend.src.DataBase.src.structures.classrooms import Classroom
import pandas as pd
from fastapi import APIRouter, Depends, Form, UploadFile, File
from Backend.src.DataBase.src.structures.user import User
from Backend.src.services.Utils.check_if_coordinator import require_coordinator
from Backend.src.DataBase.src.utils.search_classroom import search_classroom as db_search_classroom
from Backend.src.DataBase.src.utils.delete_classroom import delete_classroom as db_delete_classroom
from Backend.src.DataBase.src.utils.get_all_classrooms import get_all_classrooms 
import io

router = APIRouter(prefix="/department_coordinator", tags=["department_coordinator"])


@router.post("/upload_classes_list") 
async def upload_classes_list(user: User = Depends(require_coordinator), file: UploadFile = File(...)):
    contents = await file.read()
    
    df = pd.read_excel(io.BytesIO(contents), sheet_name="Ders Listesi", header=None)
    
    status, msg = class_list_save_from_excel(df, department=user.department)
    
    if status == 'error' and status != 'success':
        return {"message": "Error while uploading class list.", 'status': status, 'detail': msg}
    
    return {"message": "Class list uploaded successfully", 'status': status, 'detail': msg}


@router.post("/upload_students_list")
async def upload_students_list(user: User = Depends(require_coordinator), file: UploadFile = File(...)):
    contents = await file.read()
    
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
            return {
                "classrooms": [],
                "message": "Error while fetching exam classrooms.",
                'status': 'error',
                'detail': msg
            }
        
        return {
            "classrooms": classrooms_list,
            "message": "Exam classrooms fetched successfully.",
            'status': 'success',
            'detail': msg
        }
        
    except Exception as e:
        return {
            "classrooms": [],
            "message": "Error while fetching exam classrooms.",
            'status': 'error',
            'detail': str(e)
        }