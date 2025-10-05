import pandas as pd
from fastapi import APIRouter, Depends, UploadFile, File
from Backend.src.DataBase.src.structures.user import User
from Backend.src.services.Utils.check_if_admin import require_admin
from Backend.src.DataBase.scripts.class_list_save_from_excel import class_list_save_from_excel
from Backend.src.DataBase.scripts.student_list_save_from_excel import student_list_save_from_excel
import io

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/admin_dashboard")
def admin_dashboard(user: User = Depends(require_admin)):
    pass

@router.post("/upload_classes_list") 
async def upload_classes_list(department: str, user: User = Depends(require_admin), file: UploadFile = File(...)):
    
    contents = await file.file.read().decode("utf-8")
    
    df = pd.read_excel(io.BytesIO(contents), sheet_name="Ders Listesi", header=None)
    
    class_list_save_from_excel(df, department=department)
    
    return {"message": "Class list uploaded successfully", 'status': 'success'}


@router.post("/upload_students_list")
async def upload_students_list(department: str, user: User = Depends(require_admin), file: UploadFile = File(...)):
    contents = await file.file.read().decode("utf-8")
    
    df = pd.read_excel(io.BytesIO(contents))
    
    student_list_save_from_excel(df, department=department)
    
    return {"message": "Student list uploaded successfully", 'status': 'success'}