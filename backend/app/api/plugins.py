from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from ..core.plugin_manager import PluginManager

router = APIRouter()
plugin_manager = PluginManager()

# Initialize with dummy plugin
from ..plugins.dummy_plugin import DummyPlugin
plugin_manager.register_plugin(DummyPlugin())

class PluginCommand(BaseModel):
    plugin_name: str
    action: str
    parameters: Dict[str, Any] = {}

class PluginResponse(BaseModel):
    result: Any

@router.get("/plugins", response_model=Dict[str, Dict[str, Any]])
async def list_plugins():
    """List all registered plugins and their capabilities."""
    return plugin_manager.get_all_capabilities()

@router.get("/plugins/{plugin_name}/actions", response_model=List[str])
async def list_plugin_actions(plugin_name: str):
    """List all available actions for a specific plugin."""
    try:
        return plugin_manager.list_available_actions(plugin_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/plugins/execute", response_model=PluginResponse)
async def execute_plugin_command(command: PluginCommand):
    """Execute a command on a specific plugin."""
    try:
        result = plugin_manager.route_command(
            command.plugin_name,
            command.action,
            **command.parameters
        )
        return PluginResponse(result=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 