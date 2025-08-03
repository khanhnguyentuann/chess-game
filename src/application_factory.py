"""
Application Factory
Manages application lifecycle and provides access to application services.
"""

import logging
from typing import Optional

from .composition_root import get_container, reset_container, ServiceContainer
from .application.services.game_application_service import IGameApplicationService
from .presentation.controllers.game_controller import GameController
from .presentation.viewmodels.game_view_model import GameViewModel


class ApplicationFactory:
    """Factory for creating and managing application components."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize application factory."""
        self._container: Optional[ServiceContainer] = None
        self._config_path = config_path
        self._logger = logging.getLogger(__name__)
    
    def initialize(self) -> None:
        """Initialize the application and dependency injection container."""
        try:
            self._container = get_container(self._config_path)
            self._logger.info("Application factory initialized successfully")
        except Exception as e:
            self._logger.error(f"Failed to initialize application factory: {e}")
            raise
    
    def get_game_service(self) -> IGameApplicationService:
        """Get the game application service."""
        if not self._container:
            raise RuntimeError("Application factory not initialized")
        
        return self._container.get("game_application_service")
    
    def create_game_controller(self) -> GameController:
        """Create a new game controller instance."""
        if not self._container:
            raise RuntimeError("Application factory not initialized")
        
        game_service = self.get_game_service()
        return GameController(game_service)
    
    def create_game_view_model(self) -> GameViewModel:
        """Create a new game view model instance."""
        return GameViewModel()
    
    def get_container(self) -> ServiceContainer:
        """Get the dependency injection container."""
        if not self._container:
            raise RuntimeError("Application factory not initialized")
        
        return self._container
    
    def shutdown(self) -> None:
        """Shutdown the application and cleanup resources."""
        if self._container:
            self._container.shutdown()
            self._container = None
        
        reset_container()
        self._logger.info("Application factory shutdown complete")


# Global application factory instance
_app_factory: Optional[ApplicationFactory] = None


def get_application_factory(config_path: Optional[str] = None) -> ApplicationFactory:
    """Get the global application factory instance."""
    global _app_factory
    
    if _app_factory is None:
        _app_factory = ApplicationFactory(config_path)
        _app_factory.initialize()
    
    return _app_factory


def shutdown_application_factory() -> None:
    """Shutdown the global application factory."""
    global _app_factory
    
    if _app_factory:
        _app_factory.shutdown()
        _app_factory = None 