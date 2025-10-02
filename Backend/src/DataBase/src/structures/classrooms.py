from pydantic import BaseModel, Field

class Classroom(BaseModel):
    classroom_id: str = Field(alias='DERSLİK KODU')
    classroom_name: str = Field(alias='DERSLİK ADI')
    capacity: int = Field(alias='KAPASİTE', description='Sınav yapılabilecek maksimum öğrenci sayısı')   
    desks_per_row: int = Field(alias='SIRA SATIR SAYISI', description='Bir sırada bulunan masa sayısı')
    desk_per_column: int = Field(alias='SIRA SÜTUN SAYISI', description='Bir sütunda bulunan masa sayısı')
    desk_structure: str = Field(alias='MASA YAPISI', description='Masa yapısı örn: 2x2, 3x3, 2x3')
    

    class Config:
        populate_by_name = True
        extra = "ignore"