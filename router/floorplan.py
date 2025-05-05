from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from utils.api import Router
from dependencies.database import get_db
from dependencies.auth import check_role
from ..schemas.floorplan import FloorPlanCreate, FloorPlan as FloorPlanSchema
from ..services.floorplan_service import FloorPlanService

router = Router()

@router.get("/", response_model=list[FloorPlanSchema])
def list_floorplans(db: Session = Depends(get_db)):
    return FloorPlanService(db).list()

@router.get("/{floorplan_id}", response_model=FloorPlanSchema)
def get_floorplan(floorplan_id: int, db: Session = Depends(get_db)):
    return FloorPlanService(db).get(floorplan_id)

@router.post("/", response_model=FloorPlanSchema)
def create_floorplan(
    floorplan: FloorPlanCreate,
    db: Session = Depends(get_db),
    user=Depends(check_role(["cb-manage_floorplans"]))
):
    return FloorPlanService(db).create(floorplan)

@router.put("/{floorplan_id}", response_model=FloorPlanSchema)
def update_floorplan(
    floorplan_id: int,
    floorplan: FloorPlanCreate,
    db: Session = Depends(get_db),
    user=Depends(check_role(["cb-manage_floorplans"]))
):
    return FloorPlanService(db).update(floorplan_id, floorplan)

@router.delete("/{floorplan_id}", response_model=FloorPlanSchema)
def delete_floorplan(
    floorplan_id: int,
    db: Session = Depends(get_db),
    user=Depends(check_role(["cb-manage_floorplans"]))
):
    return FloorPlanService(db).delete(floorplan_id)
