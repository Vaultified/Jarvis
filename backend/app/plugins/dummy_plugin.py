from typing import Dict, Any, List
from ..core.plugin_base import BasePlugin

class DummyPlugin(BasePlugin):
    """A dummy plugin for testing the plugin system."""
    
    @property
    def name(self) -> str:
        return "dummy"
    
    @property
    def description(self) -> str:
        return "A dummy plugin for testing purposes"
    
    def register_plugin(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "version": "1.0.0",
            "actions": self.get_available_actions()
        }
    
    def get_available_actions(self) -> List[str]:
        return ["echo", "add_numbers"]
    
    def echo(self, message: str) -> str:
        """Echo back the provided message."""
        return f"Dummy plugin received: {message}"
    
    def add_numbers(self, a: int, b: int) -> int:
        """Add two numbers together."""
        return a + b 