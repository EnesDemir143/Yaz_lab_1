from fastapi import HTTPException
from Backend.src.DataBase.src.structures.user import User
from Backend.src.services.Utils.get_current_role import get_current_role

def require_coordinator(user: User):
    if get_current_role(user) != 'coordinator':
        raise HTTPException(status_code=403, detail="Not authorized for coordinator")
    return user