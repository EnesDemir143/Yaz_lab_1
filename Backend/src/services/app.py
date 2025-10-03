from fastapi import FastAPI, HTTPException
from Backend.src.DataBase.src.structures.user import User
from Backend.src.services.Routes.department_coordinator import router as department_coordinator
from Backend.src.services.Routes.admin import router as admin
from Backend.src.services.Utils.get_current_role import get_current_role
from Backend.src.DataBase.src.utils.hash_password import HashPassword

app = FastAPI()

app.include_router(department_coordinator)
app.include_router(admin)

@app.post("/login")
def login(user: User):
    role = get_current_role(user)

    if role == "admin":
        print("Admin logged in")
        return {"role": "admin"}
    elif role == "coordinator":
        print("Coordinator logged in")
        return {"role": "coordinator"}
    else:
        raise HTTPException(status_code=401, detail="Invalid role")
