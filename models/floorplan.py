from dependencies.database import Base
from sqlalchemy import Column, Integer, String, Text

class FloorPlan(Base):
    __tablename__ = "floor_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    details = Column(Text, nullable=True)
    image = Column(String, nullable=True)
    order = Column(Integer, nullable=False, default=0, unique=True) 