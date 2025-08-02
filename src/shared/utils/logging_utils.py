"""
Logging utilities for the chess game application.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    format_string: Optional[str] = None,
    console_output: bool = True,
) -> None:
    """
    Setup application logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        max_file_size: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
        format_string: Custom format string for log messages
        console_output: Whether to output logs to console
    """

    # Default format
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Create formatter
    formatter = logging.Formatter(format_string)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # File handler with rotation
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_path, maxBytes=max_file_size, backupCount=backup_count, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Prevent duplicate logs
    root_logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class GameLogger:
    """
    Specialized logger for game events with structured logging.
    """

    def __init__(self, name: str = "chess.game"):
        self.logger = logging.getLogger(name)

    def log_move(self, game_id: str, player: str, move: str, fen: str) -> None:
        """Log a game move."""
        self.logger.info(
            f"Move made - Game: {game_id}, Player: {player}, Move: {move}, FEN: {fen}"
        )

    def log_game_start(
        self, game_id: str, white_player: str, black_player: str
    ) -> None:
        """Log game start."""
        self.logger.info(
            f"Game started - ID: {game_id}, White: {white_player}, Black: {black_player}"
        )

    def log_game_end(self, game_id: str, winner: Optional[str], reason: str) -> None:
        """Log game end."""
        winner_str = winner if winner else "Draw"
        self.logger.info(
            f"Game ended - ID: {game_id}, Winner: {winner_str}, Reason: {reason}"
        )

    def log_error(
        self, game_id: str, error_type: str, message: str, details: Optional[str] = None
    ) -> None:
        """Log game error."""
        error_msg = (
            f"Game error - ID: {game_id}, Type: {error_type}, Message: {message}"
        )
        if details:
            error_msg += f", Details: {details}"
        self.logger.error(error_msg)

    def log_performance(
        self, operation: str, duration: float, details: Optional[str] = None
    ) -> None:
        """Log performance metrics."""
        perf_msg = f"Performance - Operation: {operation}, Duration: {duration:.3f}s"
        if details:
            perf_msg += f", Details: {details}"
        self.logger.debug(perf_msg)
