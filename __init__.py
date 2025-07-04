from .router import router
from .schemas.floorplan_component import FloorPlanComponent
from services.component_registry import ComponentRegistry
import logging

logger = logging.getLogger("coffeebreak.floor-plan")

PLUGIN_TITLE = "floor-plan-plugin"
NAME = "Floor Plan Plugin"
DESCRIPTION = "A plugin to display a floor plan of the building."

async def register_plugin():
    ComponentRegistry.register_component(FloorPlanComponent)
    logger.debug("Floor plan plugin registered.")
    return router

async def unregister_plugin():
    ComponentRegistry.unregister_component("FloorPlanComponent")
    logger.debug("Floor plan plugin unregistered.")

REGISTER = register_plugin
UNREGISTER = unregister_plugin

CONFIG_PAGE = True
