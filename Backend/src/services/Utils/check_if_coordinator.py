from fastapi import Depends, HTTPException
from Backend.src.DataBase.src.structures.user import User
from Backend.src.services.Utils.check_if_coordinator import check_if_coordinator

def require_coordinator(user: User):
    if not check_if_coordinator(user):
        raise HTTPException(status_code=403, detail="Not authorized")
    return user