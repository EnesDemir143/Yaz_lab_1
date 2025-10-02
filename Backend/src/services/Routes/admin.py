from fastapi import APIRouter, Depends
from Backend.src.DataBase.src.structures.user import User
from Backend.src.services.Utils.check_if_admin import require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/")
def admin_dashboard(user: User = Depends(require_admin)):
    return {"message": f"Welcome, {user.name} (Admin)"}