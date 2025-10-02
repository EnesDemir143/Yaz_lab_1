from fastapi import FastAPI
from Backend.src.services.Routes.department_coordinator import router as department_coordinator
from Backend.src.services.Routes.admin import router as admin


app = FastAPI()

app.include_router(department_coordinator)
app.include_router(admin)