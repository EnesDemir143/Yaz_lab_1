from Backend.src.DataBase.src.structures.user import User
from fastapi import Depends, HTTPException
from Backend.src.services.Utils.check_if_admin import check_if_admin

def require_admin(user: User):
    if not check_if_admin(user):
        raise HTTPException(status_code=403, detail="Not authorized")
    return user