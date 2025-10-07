from fastapi import FastAPI, HTTPException
from Backend.src.DataBase.src.structures.user import User
from Backend.src.services.Routes.department_coordinator import router as department_coordinator
from Backend.src.services.Routes.admin import router as admin
from Backend.src.services.Utils.get_current_role import get_current_role
from jose import jwt
import os
import datetime
from dotenv import load_dotenv

app = FastAPI()

app.include_router(department_coordinator)
app.include_router(admin)

load_dotenv(r'../../../../.env')
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_minutes: int = 60):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.post("/login")
def login(user: User):
    role, department = get_current_role(user)

    if role not in ["admin", "coordinator"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "email": user.email,
        "department": department,
        "role": role
    })

    return {
        "message": "Login successful",
        "role": role,
        "email": user.email,
        "department": department,
        "token": token
    }
