"""
Game-specific exceptions for chess application.
"""


class ChessGameException(Exception):
    """Base exception for chess game errors."""
    pass


class InvalidMoveException(ChessGameException):
    """Raised when an invalid move is attempted."""
    
    def __init__(self, message: str, move_request=None):
        super().__init__(message)
        self.move_request = move_request


class GameEndedException(ChessGameException):
    """Raised when attempting to play a move in an ended game."""
    pass


class InvalidGameStateException(ChessGameException):
    """Raised when game state is invalid or corrupted."""
    pass


class PlayerNotFoundException(ChessGameException):
    """Raised when a player is not found."""
    pass


class GameNotFoundException(ChessGameException):
    """Raised when a game is not found."""
    pass


class PersistenceException(ChessGameException):
    """Raised when there's an error with game persistence."""
    pass


class ConfigurationException(ChessGameException):
    """Raised when there's a configuration error."""
    pass


class ValidationException(ChessGameException):
    """Raised when validation fails."""
    pass
