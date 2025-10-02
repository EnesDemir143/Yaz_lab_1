from pydantic import BaseModel, Field


class Class(BaseModel):
    id: int = Field(alias='DERS KODU')
    name: str = Field(alias='DERSİN ADI')
    teacher: str = Field(alias='DERSİ VEREN ÖĞR. ELEMANI')
    is_optional: bool = Field(alias='Seçmeli mi?')
    year: int = Field(alias='SINIF')
