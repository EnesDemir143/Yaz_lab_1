from pydantic import BaseModel, Field

class Classroom(BaseModel):
    classroom_id: str = Field()
    classroom_name: str = Field()
    department_name: str = Field()
    capacity: int = Field()   
    desks_per_row: int = Field()
    desks_per_column: int = Field()
    desk_structure: str = Field()
    
    class Config:
        populate_by_name = True
        extra = "ignore"
        allow_population_by_field_name = True