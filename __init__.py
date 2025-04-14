from utils.api import Router
from .router import router
from .schemas.floorplan_component import FloorPlanComponent
from services.component_registry import ComponentRegistry
from services.ui.plugin_settings import create_plugin_setting, delete_plugin_setting_by_title
from schemas.plugin_setting import PluginSetting
import logging

logger = logging.getLogger("coffeebreak.plugins.floorplan")

PLUGIN_TITLE = "Floor Plan"
PLUGIN_DESCRIPTION = "A plugin to display a floor plan of the building."

async def register_plugin():
    ComponentRegistry.register_component(FloorPlanComponent)
    logger.debug("Floor plan plugin registered.")

    setting = PluginSetting(
        title=PLUGIN_TITLE,
        description=PLUGIN_DESCRIPTION,
        inputs=[]
    )
    await create_plugin_setting(setting)

    return router

async def unregister_plugin():
    ComponentRegistry.unregister_component("FloorPlanComponent")
    await delete_plugin_setting_by_title(PLUGIN_TITLE)
    logger.debug("Floor plan plugin unregistered.")

REGISTER = register_plugin
UNREGISTER = unregister_plugin

SETTINGS = {}
DESCRIPTION = PLUGIN_DESCRIPTION
