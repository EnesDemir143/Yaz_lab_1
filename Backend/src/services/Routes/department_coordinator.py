from fastapi import APIRouter, Depends
from Backend.src.DataBase.src.structures.user import User
from Backend.src.services.Utils.check_if_coordinator import require_coordinator

router = APIRouter(prefix="/department_coordinator", tags=["department_coordinator"])

@router.get("/")
def coordinator_dashboard(user: User = Depends(require_coordinator)):
    return {"message": f"Welcome, {user.name} (Coordinator)"}