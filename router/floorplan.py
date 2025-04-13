from fastapi import Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from utils.api import Router
from dependencies.database import get_db
from dependencies.auth import check_role
from ..models.floorplan import FloorPlan as FloorPlanModel
from ..schemas.floorplan import FloorPlanCreate, FloorPlan as FloorPlanSchema
from services.media import MediaService
from ..utils.uuid import is_valid_uuid

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

from ..utils.uuid import is_valid_uuid

@router.put("/{floorplan_id}", response_model=FloorPlanSchema)
def update_floorplan(
    floorplan_id: int,
    data: FloorPlanCreate,
    db: Session = Depends(get_db),
    user=Depends(check_role(["admin"]))
):
    """
    Update an existing floor plan.
    - If 'image' is a UUID, we assume it's managed by MediaService and skip updating it.
    """
    fp = db.query(FloorPlanModel).filter_by(id=floorplan_id).first()
    if not fp:
        raise HTTPException(status_code=404, detail="Floor plan not found")

    update_data = data.dict()

    # Evita substituir o UUID se já for uma imagem gerida
    if is_valid_uuid(fp.image):
        update_data.pop("image", None)

    for key, value in update_data.items():
        setattr(fp, key, value)

    db.commit()
    db.refresh(fp)
    return fp

@router.put("/{floorplan_id}/upload-image", response_model=FloorPlanSchema)
def upload_floorplan_image(
    floorplan_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(check_role(["admin"]))
):
    """
    Upload or replace the image associated with a floor plan.
    - If current image UUID is valid, replace it.
    - Otherwise, register and assign a new media UUID.
    """

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only images are allowed.")

    fp = db.query(FloorPlanModel).filter_by(id=floorplan_id).first()
    if not fp:
        raise HTTPException(status_code=404, detail="Floor plan not found")

    if is_valid_uuid(fp.image):
        # Replace the existing media
        MediaService.create_or_replace(db, fp.image, file.file, file.filename)
    else:
        # Register a new media file
        media = MediaService.register(
            db=db,
            max_size=10 * 1024 * 1024,
            allows_rewrite=True,
            valid_extensions=['.jpg', '.jpeg', '.png', '.webp'],
            alias=file.filename
        )
        MediaService.create(db=db, uuid=media.uuid, data=file.file, filename=file.filename)
        fp.image = media.uuid

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