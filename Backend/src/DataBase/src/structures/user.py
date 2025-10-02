from pydantic import BaseModel, Field

class User(BaseModel):
    email: str = Field(..., description="Kullanıcı e-posta adresi")
    password: str = Field(..., description="Kullanıcı şifresi")