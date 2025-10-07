import os
from fastapi import Depends, HTTPException, status, Header
from jose import jwt, JWTError
from Backend.src.DataBase.src.structures.user import User
from dotenv import load_dotenv

ENV_PATH = r'../../../../.env'

load_dotenv(ENV_PATH)

ALGORITHM = "HS256"

def require_coordinator(authorization: str = Header(...)) -> User:
    try:
        SECRET_KEY = os.getenv("SECRET_KEY")
        if SECRET_KEY is None:
            raise HTTPException(status_code=500, detail="Server configuration error")
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid auth scheme")

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        department: str = payload.get("department")
        role: str = payload.get("role")

        if role != "coordinator":
            raise HTTPException(status_code=403, detail="Not authorized for admin")

        return User(email=email, password="", department=department)

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")