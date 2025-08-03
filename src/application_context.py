"""
Application Context
Manages application state and provides access to application services.
"""

import logging
from typing import Any, Dict, Optional

from .application_factory import ApplicationFactory
from .shared.config.game_config import GameConfig


class ApplicationContext:
    """Manages application context and state."""
    
    def __init__(self, app_factory: ApplicationFactory):
        """Initialize application context."""
        self._app_factory = app_factory
        self._state: Dict[str, Any] = {}
        self._logger = logging.getLogger(__name__)
    
    def get_game_service(self):
        """Get the game application service."""
        return self._app_factory.get_game_service()
    
    def create_game_controller(self):
        """Create a new game controller."""
        return self._app_factory.create_game_controller()
    
    def create_game_view_model(self):
        """Create a new game view model."""
        return self._app_factory.create_game_view_model()
    
    def get_config(self) -> GameConfig:
        """Get application configuration."""
        return self._app_factory.get_container().get_config()
    
    def set_state(self, key: str, value: Any) -> None:
        """Set application state."""
        self._state[key] = value
        self._logger.debug(f"State set: {key} = {value}")
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get application state."""
        return self._state.get(key, default)
    
    def has_state(self, key: str) -> bool:
        """Check if state key exists."""
        return key in self._state
    
    def remove_state(self, key: str) -> None:
        """Remove application state."""
        if key in self._state:
            del self._state[key]
            self._logger.debug(f"State removed: {key}")
    
    def clear_state(self) -> None:
        """Clear all application state."""
        self._state.clear()
        self._logger.debug("All state cleared")
    
    def get_all_state(self) -> Dict[str, Any]:
        """Get all application state."""
        return self._state.copy()


# Global application context
_app_context: Optional[ApplicationContext] = None


def get_application_context() -> ApplicationContext:
    """Get the global application context."""
    global _app_context
    
    if _app_context is None:
        from .application_factory import get_application_factory
        app_factory = get_application_factory()
        _app_context = ApplicationContext(app_factory)
    
    return _app_context


def set_application_context(context: ApplicationContext) -> None:
    """Set the global application context."""
    global _app_context
    _app_context = context


def clear_application_context() -> None:
    """Clear the global application context."""
    global _app_context
    _app_context = None 