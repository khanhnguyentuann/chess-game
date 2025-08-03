"""
Application Bootstrap
Handles application startup, configuration, and initialization.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional

from .application_factory import get_application_factory, shutdown_application_factory
from .shared.config.game_config import GameConfig


class ApplicationBootstrap:
    """Handles application startup and initialization."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize application bootstrap."""
        self._config_path = config_path
        self._logger = logging.getLogger(__name__)
    
    def setup_environment(self) -> None:
        """Setup application environment."""
        # Set pygame window to center on screen
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        
        # Add project root to Python path
        project_root = Path(__file__).parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        self._logger.info("Environment setup complete")
    
    def load_configuration(self) -> GameConfig:
        """Load application configuration."""
        try:
            config = GameConfig(self._config_path)
            self._logger.info("Configuration loaded successfully")
            return config
        except Exception as e:
            self._logger.error(f"Failed to load configuration: {e}")
            raise
    
    def initialize_application(self) -> None:
        """Initialize the application and all its components."""
        try:
            # Setup environment
            self.setup_environment()
            
            # Load configuration
            config = self.load_configuration()
            
            # Initialize application factory
            app_factory = get_application_factory(self._config_path)
            
            self._logger.info("Application initialization complete")
            
        except Exception as e:
            self._logger.error(f"Failed to initialize application: {e}")
            raise
    
    def shutdown_application(self) -> None:
        """Shutdown the application and cleanup resources."""
        try:
            shutdown_application_factory()
            self._logger.info("Application shutdown complete")
        except Exception as e:
            self._logger.error(f"Error during application shutdown: {e}")


def bootstrap_application(config_path: Optional[str] = None) -> ApplicationBootstrap:
    """Bootstrap the application."""
    bootstrap = ApplicationBootstrap(config_path)
    bootstrap.initialize_application()
    return bootstrap 