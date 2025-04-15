from dependencies.database import Base
from sqlalchemy import Column, Integer, String, Text

class FloorPlan(Base):
    __tablename__ = "floor_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    image = Column(String, nullable=False)