from pydantic import BaseModel, Field

class User(BaseModel):
    email: str = Field(...)
    password: str = Field(...)