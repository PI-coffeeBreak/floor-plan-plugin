from fastapi import Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from utils.api import Router
from dependencies.database import get_db
from dependencies.auth import check_role
from ..models.floorplan import FloorPlan as FloorPlanModel
from ..schemas.floorplan import FloorPlanCreate, FloorPlan as FloorPlanSchema
from services.media import MediaService
from ..utils.uuid_url import is_valid_uuid, is_valid_url
from uuid import uuid4

router = Router()

@router.post("/", response_model=FloorPlanSchema)
def create_floorplan(
    floorplan: FloorPlanCreate,
    db: Session = Depends(get_db),
    user=Depends(check_role(["admin"]))
):
    image = floorplan.image

    if not image or not is_valid_url(image):
        # Register new media entry
        media = MediaService.register(
            db=db,
            max_size=10 * 1024 * 1024,
            allows_rewrite=True,
            valid_extensions=['.jpg', '.jpeg', '.png', '.webp'],
            alias=f"{floorplan.name}-{uuid4()}"
        )
        image = media.uuid

    new = FloorPlanModel(**floorplan.dict(), image=image)
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

    update_data = data.dict(exclude_unset=True)

    new_image = update_data.get("image")
    if new_image:
        if is_valid_uuid(fp.image) and is_valid_url(new_image):
            MediaService.unregister(db, fp.image, force=True)
        elif is_valid_uuid(fp.image) and not is_valid_url(new_image):
            update_data.pop("image", None)
        elif is_valid_url(fp.image) and not is_valid_url(new_image):
            raise HTTPException(status_code=400, detail="Invalid image URL.")

    for key, value in update_data.items():
        setattr(fp, key, value)

    db.commit()
    db.refresh(fp)
    return fp

@router.delete("/{floorplan_id}", response_model=FloorPlanSchema)
def delete_floorplan(
    floorplan_id: int,
    db: Session = Depends(get_db),
    user=Depends(check_role(["admin"]))
):
    fp = db.query(FloorPlanModel).filter_by(id=floorplan_id).first()
    if not fp:
        raise HTTPException(status_code=404, detail="Floor plan not found")

    if is_valid_uuid(fp.image):
        MediaService.unregister(db, fp.image, force=True)

    db.delete(fp)
    db.commit()
    return fp

@router.delete("/{floorplan_id}/image", response_model=FloorPlanSchema)
def remove_floorplan_image(
    floorplan_id: int,
    db: Session = Depends(get_db),
    user=Depends(check_role(["admin"]))
):
    floorplan = db.query(FloorPlanModel).filter_by(id=floorplan_id).first()
    if not floorplan:
        raise HTTPException(status_code=404, detail="Floor plan not found")

    if is_valid_uuid(floorplan.image):
        MediaService.unregister(db, floorplan.image, force=True)
    else:
        raise HTTPException(status_code=404, detail="Current image is external or not was not found")

    floorplan.image = None
    db.commit()
    db.refresh(floorplan)
    return floorplan