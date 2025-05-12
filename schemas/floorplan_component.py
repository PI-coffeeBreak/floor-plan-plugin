from pydantic import Field
from schemas.ui.page import BaseComponentSchema
from schemas.ui.components.title import Title
from schemas.ui.components.text import Text
from schemas.ui.components.image import Image


class FloorPlanComponent(BaseComponentSchema):
    title: Title = Field(..., description="Title of the floor plan section")
    description: Text = Field(..., description="Descriptive text for the floor plan")
    image: Image = Field(..., description="Floor plan image component")
    show_selector: bool = Field(default=True, description="Whether to show the floor plan selector")
