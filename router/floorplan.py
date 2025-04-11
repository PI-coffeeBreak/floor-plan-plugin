from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from utils.api import Router
from dependencies.database import get_db
from dependencies.auth import check_role
from ..models.floorplan import FloorPlan as FloorPlanModel
from ..schemas.floorplan import FloorPlanCreate, FloorPlan as FloorPlanSchema

router = Router()

@router.post("/", response_model=FloorPlanSchema)
def create_floorplan(
    floorplan: FloorPlanCreate,
    db: Session = Depends(get_db),
    user=Depends(check_role(["admin"]))
):
    new = FloorPlanModel(**floorplan.dict())
    db.add(new)
    db.commit()
    db.refresh(new)
    return new

@router.get("/", response_model=list[FloorPlanSchema])
def list_floorplans(db: Session = Depends(get_db)):
    return db.query(FloorPlanModel).all()

@router.get("/{floorplan_id}", response_model=FloorPlanSchema)
def get_floorplan(floorplan_id: int, db: Session = Depends(get_db)):
    fp = db.query(FloorPlanModel).filter_by(id=floorplan_id).first()
    if not fp:
        raise HTTPException(status_code=404, detail="Floor plan not found")
    return fp

@router.put("/{floorplan_id}", response_model=FloorPlanSchema)
def update_floorplan(
    floorplan_id: int,
    data: FloorPlanCreate,
    db: Session = Depends(get_db),
    user=Depends(check_role(["admin"]))
):
    fp = db.query(FloorPlanModel).filter_by(id=floorplan_id).first()
    if not fp:
        raise HTTPException(status_code=404, detail="Floor plan not found")

    for key, value in data.dict().items():
        setattr(fp, key, value)

    db.commit()
    db.refresh(fp)
    return fp

@router.delete("/{floorplan_id}", response_model=FloorPlanSchema)
def delete_floorplan(floorplan_id: int, db: Session = Depends(get_db), user=Depends(check_role(["admin"]))):
    fp = db.query(FloorPlanModel).filter_by(id=floorplan_id).first()
    if not fp:
        raise HTTPException(status_code=404, detail="Floor plan not found")

    db.delete(fp)
    db.commit()
    return fp
