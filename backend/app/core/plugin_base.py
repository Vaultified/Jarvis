from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BasePlugin(ABC):
    """Base class for all Jarvis plugins."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the plugin."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Return a description of what the plugin does."""
        pass
    
    @abstractmethod
    def register_plugin(self) -> Dict[str, Any]:
        """Register the plugin and return its capabilities."""
        pass
    
    @abstractmethod
    def get_available_actions(self) -> List[str]:
        """Return a list of available actions/methods in this plugin."""
        pass
    
    def validate_action(self, action: str) -> bool:
        """Validate if an action exists in this plugin."""
        return action in self.get_available_actions() 