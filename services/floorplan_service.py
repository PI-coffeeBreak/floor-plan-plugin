from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List
from uuid import uuid4

from ..models.floorplan import FloorPlan as FloorPlanModel
from ..schemas.floorplan import FloorPlanCreate
from services.media import MediaService
from ..utils.media import is_valid_uuid, is_valid_url, slugify

class FloorPlanService:
    def __init__(self, db: Session):
        self.db = db

    def list(self) -> List[FloorPlanModel]:
        return self.db.query(FloorPlanModel).order_by(FloorPlanModel.order).all()

    def get(self, floorplan_id: int) -> FloorPlanModel:
        fp = self.db.query(FloorPlanModel).filter_by(id=floorplan_id).first()
        if not fp:
            raise HTTPException(status_code=404, detail="Floor plan not found")
        return fp

    def create(self, data: FloorPlanCreate) -> FloorPlanModel:
        image = data.image
        if not image or not is_valid_url(image):
            alias = f"{slugify(data.name)}-{uuid4()}"
            media = MediaService.register(
                db=self.db,
                max_size=10 * 1024 * 1024,
                allows_rewrite=True,
                valid_extensions=['.jpg', '.jpeg', '.png', '.webp'],
                alias=alias
            )
            image = media.uuid

        max_order = self.db.query(FloorPlanModel).order_by(FloorPlanModel.order.desc()).first()
        new_order = (max_order.order + 1) if max_order else 1

        new_fp = FloorPlanModel(
            **data.dict(exclude={"image", "order"}),
            image=image,
            order=new_order
        )
        self.db.add(new_fp)
        self.db.commit()
        self.db.refresh(new_fp)
        return new_fp

    def update(self, floorplan_id: int, data: FloorPlanCreate) -> FloorPlanModel:
        fp = self.get(floorplan_id)
        update_data = data.dict(exclude_unset=True)

        new_image = update_data.get("image")
        if new_image:
            if is_valid_uuid(fp.image) and is_valid_url(new_image):
                MediaService.unregister(self.db, fp.image, force=True)
            elif is_valid_uuid(fp.image) and not is_valid_url(new_image):
                update_data.pop("image", None)
            elif is_valid_url(fp.image) and not is_valid_url(new_image):
                media = MediaService.register(
                    db=self.db,
                    max_size=10 * 1024 * 1024,
                    allows_rewrite=True,
                    valid_extensions=['.jpg', '.jpeg', '.png', '.webp'],
                    alias=f"{slugify(fp.name)}-{uuid4()}"
                )
                update_data["image"] = media.uuid

        for key, value in update_data.items():
            setattr(fp, key, value)

        self.db.commit()
        self.db.refresh(fp)
        return fp

    def delete(self, floorplan_id: int) -> FloorPlanModel:
        fp = self.get(floorplan_id)
        if is_valid_uuid(fp.image):
            MediaService.unregister(self.db, fp.image, force=True)
        self.db.delete(fp)
        self.db.commit()
        return fp
