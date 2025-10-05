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
        return {"message": "Error while uploading class list.", 'status': 'error', 'detail': msg}
    
    return {"message": "Class list uploaded successfully", 'status': 'success'}


@router.post("/upload_students_list")
async def upload_students_list(user: User = Depends(require_coordinator), file: UploadFile = File(...)):
    
    contents = await file.file.read().decode("utf-8")
    
    df = pd.read_excel(io.BytesIO(contents))
    
    student_list_save_from_excel(df, department=user.department)
    
    return {"message": "Student list uploaded successfully", 'status': 'success'}