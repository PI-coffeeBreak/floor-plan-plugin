from fastapi import Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from utils.api import Router
from dependencies.database import get_db
from dependencies.auth import check_role
from ..models.floorplan import FloorPlan as FloorPlanModel
from ..schemas.floorplan import FloorPlanCreate, FloorPlan as FloorPlanSchema
from services.media import MediaService
from ..utils.uuid import is_valid_uuid
from typing import Optional

router = Router()

@router.post("/", response_model=FloorPlanSchema)
def create_floorplan(
    floorplan: FloorPlanCreate,
    db: Session = Depends(get_db),
    user=Depends(check_role(["admin"])),
    file: UploadFile | None = File(None)
):
    image_url_or_id = floorplan.image

    if file:
        media = MediaService.register(
            db=db,
            max_size=10 * 1024 * 1024,
            allows_rewrite=False,
            valid_extensions=['.jpg', '.jpeg', '.png', '.webp'],
            alias=file.filename
        )
        MediaService.create(db=db, uuid=media.uuid, data=file.file, filename=file.filename)
        image_url_or_id = media.uuid

    new = FloorPlanModel(**floorplan.dict(exclude={"image"}), image=image_url_or_id)
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
    user=Depends(check_role(["admin"])),
    file: Optional[UploadFile] = File(None)
):
    """
    Update an existing floor plan.
    - If a file is uploaded, we handle the MediaService logic.
    - If floorplan.image is a valid UUID, we reuse it with create_or_replace.
    - Otherwise, we create a new UUID.
    """
    fp = db.query(FloorPlanModel).filter_by(id=floorplan_id).first()
    if not fp:
        raise HTTPException(status_code=404, detail="Floor plan not found")

    if not file:
        for key, value in data.dict().items():
            setattr(fp, key, value)
        db.commit()
        db.refresh(fp)
        return fp

    if is_valid_uuid(fp.image):
        media_uuid = fp.image
        MediaService.create_or_replace(db, media_uuid, file.file, file.filename)
    else:
        media = MediaService.register(
            db=db,
            max_size=10 * 1024 * 1024,
            allows_rewrite=True,
            valid_extensions=['.jpg', '.jpeg', '.png', '.webp'],
            alias=file.filename
        )
        MediaService.create(db=db, uuid=media.uuid, data=file.file, filename=file.filename)
        fp.image = media.uuid

    # Update other fields
    # We exclude the image field from the update to avoid overwriting it
    for key, value in data.dict(exclude={"image"}).items():
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
