"""
Logging Service
Infrastructure service for application logging.
"""

import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional

from ...shared.utils.logging_utils import setup_logging


class LoggingService:
    """Service for managing application logging."""
    
    def __init__(self, config_service=None):
        """Initialize logging service."""
        self._config_service = config_service
        self._loggers: Dict[str, logging.Logger] = {}
        self._setup_root_logger()
    
    def _setup_root_logger(self) -> None:
        """Setup root logger with configuration."""
        if self._config_service:
            log_level = self._config_service.get_log_level()
            debug_mode = self._config_service.is_debug_mode()
        else:
            log_level = "INFO"
            debug_mode = False
        
        # Convert string level to logging constant
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        
        level = level_map.get(log_level.upper(), logging.INFO)
        
        # Setup logging
        setup_logging(
            level=level,
            debug_mode=debug_mode,
            log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get or create a logger with the specified name.
        
        Args:
            name: Logger name (usually module name)
            
        Returns:
            Logger instance
        """
        if name not in self._loggers:
            self._loggers[name] = logging.getLogger(name)
        return self._loggers[name]
    
    def log_game_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Log a game-related event.
        
        Args:
            event_type: Type of event (e.g., "move_made", "game_started")
            data: Event data
        """
        logger = self.get_logger("game")
        logger.info(f"Game Event - {event_type}: {data}")
    
    def log_move(self, from_square: str, to_square: str, player: str, notation: str) -> None:
        """
        Log a chess move.
        
        Args:
            from_square: Source square
            to_square: Destination square
            player: Player making the move
            notation: Algebraic notation
        """
        logger = self.get_logger("moves")
        logger.info(f"Move: {player} {from_square} -> {to_square} ({notation})")
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an error with context.
        
        Args:
            error: Exception that occurred
            context: Additional context information
        """
        logger = self.get_logger("errors")
        error_msg = f"Error: {type(error).__name__}: {str(error)}"
        
        if context:
            error_msg += f" | Context: {context}"
        
        logger.error(error_msg, exc_info=True)
    
    def log_performance(self, operation: str, duration: float, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Log performance metrics.
        
        Args:
            operation: Name of the operation
            duration: Duration in seconds
            details: Additional performance details
        """
        logger = self.get_logger("performance")
        perf_msg = f"Performance - {operation}: {duration:.3f}s"
        
        if details:
            perf_msg += f" | Details: {details}"
        
        logger.debug(perf_msg)
    
    def log_user_action(self, action: str, user_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Log user actions.
        
        Args:
            action: User action (e.g., "piece_selected", "game_started")
            user_id: User identifier
            details: Additional action details
        """
        logger = self.get_logger("user_actions")
        action_msg = f"User Action - {action}"
        
        if user_id:
            action_msg += f" | User: {user_id}"
        
        if details:
            action_msg += f" | Details: {details}"
        
        logger.info(action_msg)
    
    def log_system_event(self, event: str, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Log system events.
        
        Args:
            event: System event (e.g., "startup", "shutdown", "config_loaded")
            details: Additional event details
        """
        logger = self.get_logger("system")
        event_msg = f"System Event - {event}"
        
        if details:
            event_msg += f" | Details: {details}"
        
        logger.info(event_msg)
    
    def log_database_operation(self, operation: str, table: str, duration: float, success: bool) -> None:
        """
        Log database operations.
        
        Args:
            operation: Database operation (e.g., "SELECT", "INSERT", "UPDATE")
            table: Table name
            duration: Operation duration in seconds
            success: Whether operation was successful
        """
        logger = self.get_logger("database")
        status = "SUCCESS" if success else "FAILED"
        logger.debug(f"Database - {operation} on {table}: {duration:.3f}s [{status}]")
    
    def log_event_published(self, event_type: str, event_id: str, handler_count: int) -> None:
        """
        Log domain event publishing.
        
        Args:
            event_type: Type of domain event
            event_id: Event identifier
            handler_count: Number of handlers notified
        """
        logger = self.get_logger("events")
        logger.debug(f"Event Published - {event_type} (ID: {event_id}) to {handler_count} handlers")
    
    def set_level(self, logger_name: str, level: str) -> None:
        """
        Set log level for a specific logger.
        
        Args:
            logger_name: Name of the logger
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        
        if logger_name in self._loggers:
            self._loggers[logger_name].setLevel(level_map.get(level.upper(), logging.INFO))
    
    def get_all_loggers(self) -> Dict[str, logging.Logger]:
        """Get all registered loggers."""
        return self._loggers.copy()
    
    def clear_loggers(self) -> None:
        """Clear all registered loggers."""
        self._loggers.clear() 