from fastapi import FastAPI
from Backend.src.services.Routes import department_coordinator
from Routes import admin

app = FastAPI()


app.include_router(department_coordinator.router)
app.include_router(admin.router)