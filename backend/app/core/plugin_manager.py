from typing import Dict, Any, List, Optional
from .plugin_base import BasePlugin

class PluginManager:
    """Manages the registration and routing of plugins."""
    
    def __init__(self):
        self._plugins: Dict[str, BasePlugin] = {}
        self._capabilities: Dict[str, Dict[str, Any]] = {}
    
    def register_plugin(self, plugin: BasePlugin) -> None:
        """Register a new plugin with the manager."""
        if plugin.name in self._plugins:
            raise ValueError(f"Plugin '{plugin.name}' is already registered")
        
        # Register the plugin and store its capabilities
        capabilities = plugin.register_plugin()
        self._plugins[plugin.name] = plugin
        self._capabilities[plugin.name] = capabilities
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Get a registered plugin by name."""
        return self._plugins.get(plugin_name)
    
    def get_all_plugins(self) -> Dict[str, BasePlugin]:
        """Get all registered plugins."""
        return self._plugins.copy()
    
    def get_all_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """Get capabilities of all registered plugins."""
        return self._capabilities.copy()
    
    def route_command(self, plugin_name: str, action: str, **kwargs) -> Any:
        """Route a command to the appropriate plugin and action."""
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            raise ValueError(f"Plugin '{plugin_name}' not found")
        
        if not plugin.validate_action(action):
            raise ValueError(f"Action '{action}' not found in plugin '{plugin_name}'")
        
        # Get the method from the plugin
        method = getattr(plugin, action)
        if not callable(method):
            raise ValueError(f"Action '{action}' in plugin '{plugin_name}' is not callable")
        
        # Execute the method with provided arguments
        return method(**kwargs)
    
    def list_available_actions(self, plugin_name: str) -> List[str]:
        """List all available actions for a specific plugin."""
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            raise ValueError(f"Plugin '{plugin_name}' not found")
        return plugin.get_available_actions() 