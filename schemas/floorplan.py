from pydantic import BaseModel

class FloorPlanBase(BaseModel):
    name: str
    description: str
    image: str

class FloorPlanCreate(FloorPlanBase):
    pass

class FloorPlan(FloorPlanBase):
    id: int

    class Config:
        from_attributes = True