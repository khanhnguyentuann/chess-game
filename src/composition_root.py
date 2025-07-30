"""
Composition Root - Dependency Injection Container
Configures and wires all dependencies for the chess game application.
"""

from typing import Dict, Any, Optional
import logging
from pathlib import Path

# Domain services
from .domain.services.move_validator import MoveValidatorService, MoveAnalyzer
from .domain.events.event_dispatcher import EventDispatcher, get_event_dispatcher

# Application layer
from .application.commands.base_command import CommandExecutor
from .application.use_cases.make_move import MakeMoveUseCase

# Infrastructure
from .infrastructure.repositories.memory_game_repo import MemoryGameRepository
from .infrastructure.repositories.memory_move_history_repo import MemoryMoveHistoryRepository
from .infrastructure.dummy_notification_service import DummyNotificationService

# Shared
from .shared.config.game_config import GameConfig
from .shared.utils.logging_utils import setup_logging


class ServiceContainer:
    """
    Dependency injection container for the chess game application.
    Follows the composition root pattern to configure all dependencies.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self._services: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}
        self._config = GameConfig(config_path)
        self._setup_logging()
        self._wire_dependencies()
    
    def _setup_logging(self) -> None:
        """Setup application logging."""
        setup_logging(
            level=self._config.logging.level,
            log_file=self._config.logging.file_path,
            max_file_size=self._config.logging.max_file_size,
            backup_count=self._config.logging.backup_count
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Service container initialized")
    
    def _wire_dependencies(self) -> None:
        """Wire all application dependencies."""
        
        # Register repositories
        self._register_repositories()
        
        # Register domain services
        self._register_domain_services()
        
        # Register application services
        self._register_application_services()
        
        # Register infrastructure services
        self._register_infrastructure_services()
        
        # Setup event handlers
        self._setup_event_handlers()
    
    def _register_repositories(self) -> None:
        """Register repository implementations."""
        
        # Game repository
        if self._config.persistence.type == "memory":
            self._register_singleton("game_repository", MemoryGameRepository)
        elif self._config.persistence.type == "file":
            # TODO: Implement file repository
            self._register_singleton("game_repository", MemoryGameRepository)
        elif self._config.persistence.type == "database":
            # TODO: Implement database repository
            self._register_singleton("game_repository", MemoryGameRepository)
        else:
            self._register_singleton("game_repository", MemoryGameRepository)
        
        # Move history repository
        if self._config.persistence.type == "memory":
            self._register_singleton("move_history_repository", MemoryMoveHistoryRepository)
        elif self._config.persistence.type == "file":
            # TODO: Implement file move history repository
            self._register_singleton("move_history_repository", MemoryMoveHistoryRepository)
        elif self._config.persistence.type == "database":
            # TODO: Implement database move history repository
            self._register_singleton("move_history_repository", MemoryMoveHistoryRepository)
        else:
            self._register_singleton("move_history_repository", MemoryMoveHistoryRepository)
        
        # Settings repository  
        # TODO: Implement settings repository
    
    def _register_domain_services(self) -> None:
        """Register domain service implementations."""
        
        # Move validation service
        self._register_singleton("move_validator", MoveValidatorService)
        
        # Move analyzer
        self._register_singleton("move_analyzer", lambda: MoveAnalyzer(
            self.get("move_validator")
        ))
        
        # Event dispatcher (singleton)
        self._register_singleton("event_dispatcher", get_event_dispatcher)
        
        # Notification service
        self._register_singleton("notification_service", DummyNotificationService)
    
    def _register_application_services(self) -> None:
        """Register application layer services."""
        
        # Command executor
        self._register_singleton("command_executor", CommandExecutor)
        
        # Use cases
        self._register_singleton("make_move_use_case", lambda: MakeMoveUseCase(
            move_validator=self.get("move_validator"),
            game_repository=self.get("game_repository"),
            move_history_repository=self.get("move_history_repository"),
            notification_service=self.get("notification_service"),
            command_executor=self.get("command_executor"),
            move_analyzer=self.get("move_analyzer")
        ))
    
    def _register_infrastructure_services(self) -> None:
        """Register infrastructure services."""
        
        # UI services will be registered here
        # AI engine services will be registered here
        # External API services will be registered here
        pass
    
    def _setup_event_handlers(self) -> None:
        """Setup event handlers and subscribers."""
        
        event_dispatcher = self.get("event_dispatcher")
        
        # Game event handlers
        # TODO: Register event handlers for:
        # - Move made
        # - Game over
        # - Check/checkmate
        # - Error handling
        # - Logging
        # - UI updates
        
        self.logger.info("Event handlers configured")
    
    def _register_singleton(self, name: str, factory) -> None:
        """Register a singleton service."""
        self._services[name] = ("singleton", factory)
    
    def _register_transient(self, name: str, factory) -> None:
        """Register a transient service."""
        self._services[name] = ("transient", factory)
    
    def get(self, service_name: str) -> Any:
        """
        Get a service from the container.
        
        Args:
            service_name: Name of the service to retrieve
            
        Returns:
            Service instance
            
        Raises:
            KeyError: If service is not registered
        """
        if service_name not in self._services:
            raise KeyError(f"Service '{service_name}' not registered")
        
        service_type, factory = self._services[service_name]
        
        if service_type == "singleton":
            if service_name not in self._singletons:
                if callable(factory):
                    self._singletons[service_name] = factory()
                else:
                    self._singletons[service_name] = factory
            return self._singletons[service_name]
        
        elif service_type == "transient":
            if callable(factory):
                return factory()
            else:
                return factory
        
        else:
            raise ValueError(f"Unknown service type: {service_type}")
    
    def register_service(self, name: str, service_instance: Any) -> None:
        """Register a service instance directly."""
        self._singletons[name] = service_instance
        self._services[name] = ("singleton", service_instance)
    
    def has_service(self, service_name: str) -> bool:
        """Check if a service is registered."""
        return service_name in self._services
    
    def get_config(self) -> GameConfig:
        """Get application configuration."""
        return self._config
    
    def shutdown(self) -> None:
        """Cleanup and shutdown the container."""
        self.logger.info("Shutting down service container")
        
        # Cleanup singletons that need explicit cleanup
        for service_name, service in self._singletons.items():
            if hasattr(service, 'cleanup'):
                try:
                    service.cleanup()
                except Exception as e:
                    self.logger.error(f"Error cleaning up {service_name}: {e}")
        
        self._singletons.clear()
        self._services.clear()


# Global container instance
_container: Optional[ServiceContainer] = None


def get_container(config_path: Optional[str] = None) -> ServiceContainer:
    """
    Get the global service container instance.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        ServiceContainer instance
    """
    global _container
    if _container is None:
        _container = ServiceContainer(config_path)
    return _container


def reset_container() -> None:
    """Reset the global container (for testing)."""
    global _container
    if _container:
        _container.shutdown()
    _container = None


# Convenience functions for common services
def get_move_validator() -> MoveValidatorService:
    """Get move validator service."""
    return get_container().get("move_validator")


def get_game_repository() -> MemoryGameRepository:
    """Get game repository."""
    return get_container().get("game_repository")


def get_move_history_repository() -> MemoryMoveHistoryRepository:
    """Get move history repository."""
    return get_container().get("move_history_repository")


def get_make_move_use_case() -> MakeMoveUseCase:
    """Get make move use case."""
    return get_container().get("make_move_use_case")


def get_command_executor() -> CommandExecutor:
    """Get command executor."""
    return get_container().get("command_executor")
