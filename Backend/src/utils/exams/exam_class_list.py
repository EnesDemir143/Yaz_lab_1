from fastapi import APIRouter, Depends
from Backend.src.DataBase.src.utils.class_list_menu import class_list_menu
from Backend.src.DataBase.src.structures.user import User
from Backend.src.services.Utils.check_if_admin import require_admin

router = APIRouter()

@router.post("/all_courses")
def all_courses(user: User = Depends(require_admin)):
    
    try:
        department = user.department
        courses = class_list_menu(department)

        course_list = [
            {
                "class_id": c['class_id'],
                "class_name": c['class_name']
            }
            for c in courses
        ]

        return {
            "courses": course_list,
            "message": f"{department} departmanına ait dersler getirildi.",
            "status": "success"
        }

    except Exception as e:
        return {
            "courses": [],
            "message": "Dersler alınırken hata oluştu.",
            "status": "error",
            "detail": str(e)
        }
