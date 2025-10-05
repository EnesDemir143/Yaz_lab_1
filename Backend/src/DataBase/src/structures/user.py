from pydantic import BaseModel, Field

class User(BaseModel):
    email: str = Field(...)
    password: str = Field(...)
    department: str = Field(default=None)  # Default department for admin user