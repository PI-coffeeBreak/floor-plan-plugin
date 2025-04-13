from utils.api import Router
from .router import router
from .schemas.floorplan_component import FloorPlanComponent
from services.component_registry import ComponentRegistry
import logging

logger = logging.getLogger("coffeebreak.plugins.floorplan")

def register_plugin():
    ComponentRegistry.register_component(FloorPlanComponent)
    logger.debug("Floor plan plugin registered.")
    return router

def unregister_plugin():
    ComponentRegistry.unregister_component("FloorPlanComponent")
    logger.debug("Floor plan plugin unregistered.")

REGISTER = register_plugin
UNREGISTER = unregister_plugin