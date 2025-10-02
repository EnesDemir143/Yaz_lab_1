from pydantic import BaseModel, Field


class Class(BaseModel):
    class_id: int = Field(alias='DERS KODU')
    name: str = Field(alias='DERSİN ADI')
    teacher: str = Field(alias='DERSİ VEREN ÖĞR. ELEMANI')
    is_optional: bool = Field(alias='Seçmeli mi?')
    year: int = Field(alias='SINIF')

    class Config:
        populate_by_name = True
        extra = "ignore"