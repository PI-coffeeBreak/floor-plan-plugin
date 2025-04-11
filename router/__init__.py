from utils.api import router
from .floorplan import router as floor_plan_router

router = Router()
router.include_router(floor_plan_router, prefix="/floor_plan")

__all__ = ["router"]