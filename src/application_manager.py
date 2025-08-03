"""
Application Manager
Manages the complete application lifecycle and provides a unified interface.
"""

import logging
from typing import Optional

from .application_bootstrap import ApplicationBootstrap
from .application_factory import ApplicationFactory
from .application_context import ApplicationContext


class ApplicationManager:
    """Manages the complete application lifecycle."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize application manager."""
        self._config_path = config_path
        self._bootstrap: Optional[ApplicationBootstrap] = None
        self._app_factory: Optional[ApplicationFactory] = None
        self._app_context: Optional[ApplicationContext] = None
        self._logger = logging.getLogger(__name__)
        self._is_initialized = False
    
    def initialize(self) -> None:
        """Initialize the application."""
        try:
            # Bootstrap the application
            self._bootstrap = ApplicationBootstrap(self._config_path)
            self._bootstrap.initialize_application()
            
            # Get application factory
            from .application_factory import get_application_factory
            self._app_factory = get_application_factory(self._config_path)
            
            # Create application context
            self._app_context = ApplicationContext(self._app_factory)
            
            self._is_initialized = True
            self._logger.info("Application manager initialized successfully")
            
        except Exception as e:
            self._logger.error(f"Failed to initialize application manager: {e}")
            raise
    
    def get_context(self) -> ApplicationContext:
        """Get the application context."""
        if not self._is_initialized:
            raise RuntimeError("Application manager not initialized")
        
        return self._app_context
    
    def get_factory(self) -> ApplicationFactory:
        """Get the application factory."""
        if not self._is_initialized:
            raise RuntimeError("Application manager not initialized")
        
        return self._app_factory
    
    def get_bootstrap(self) -> ApplicationBootstrap:
        """Get the application bootstrap."""
        if not self._is_initialized:
            raise RuntimeError("Application manager not initialized")
        
        return self._bootstrap
    
    def is_initialized(self) -> bool:
        """Check if application manager is initialized."""
        return self._is_initialized
    
    def shutdown(self) -> None:
        """Shutdown the application."""
        try:
            if self._bootstrap:
                self._bootstrap.shutdown_application()
            
            self._is_initialized = False
            self._logger.info("Application manager shutdown complete")
            
        except Exception as e:
            self._logger.error(f"Error during application manager shutdown: {e}")


# Global application manager instance
_app_manager: Optional[ApplicationManager] = None


def get_application_manager(config_path: Optional[str] = None) -> ApplicationManager:
    """Get the global application manager instance."""
    global _app_manager
    
    if _app_manager is None:
        _app_manager = ApplicationManager(config_path)
        _app_manager.initialize()
    
    return _app_manager


def shutdown_application_manager() -> None:
    """Shutdown the global application manager."""
    global _app_manager
    
    if _app_manager:
        _app_manager.shutdown()
        _app_manager = None 