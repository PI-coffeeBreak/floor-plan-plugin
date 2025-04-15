from pydantic import BaseModel
from typing import Optional

class FloorPlanBase(BaseModel):
    name: str
    details: Optional[str] = None
    image: Optional[str] = None

class FloorPlanCreate(FloorPlanBase):
    pass

class FloorPlan(FloorPlanBase):
    id: int

    class Config:
        from_attributes = True