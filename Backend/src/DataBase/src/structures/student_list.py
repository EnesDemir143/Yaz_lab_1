from pydantic import BaseModel, Field
from typing import List

class Student(BaseModel):
    student_num : int = Field(alias='ÖĞRENCİ NO')
    name_surname : str = Field(alias='Ad Soyad')
    year : int = Field(alias='SINIF')
    classes: List[int] = Field(default_factory=list, alias='DERSLER')
    
    class Config:
        populate_by_name = True
        extra = "ignore"