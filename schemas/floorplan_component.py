from pydantic import BaseModel, Field
from schemas.ui.page import BaseComponentSchema

class FloorPlanComponent(BaseComponentSchema):
    name: str = Field(..., description="Name of the floor plan")
    details: str = Field(..., description="Details of the floor plan")
    image: str = Field(..., description="Image URL or UUID of the floor plan")