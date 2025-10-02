from pydantic import BaseModel, Field
from Backend.src.DataBase.src.structures.classes import Class
from typing import List

class Student(BaseModel):
    student_num : int = Field(alias='ÖĞRENCİ NO')
    name_surname : str = Field(alias='Ad Soyad')
    year : int = Field(alias='SINIF')
    classes : List[Class] = Field(alias='DERS')
    
    class Config:
        populate_by_name = True
        extra = "ignore"