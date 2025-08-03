"""
Game Exceptions
Domain exceptions for game-related business rule violations.
"""


class InvalidGameStateException(Exception):
    """Base exception for invalid game state operations."""
    pass


class GameAlreadyEndedException(InvalidGameStateException):
    """Exception raised when trying to perform actions on an ended game."""
    
    def __init__(self, message: str = "Game has already ended"):
        super().__init__(message)


class GameNotStartedException(InvalidGameStateException):
    """Exception raised when trying to perform actions on a game that hasn't started."""
    
    def __init__(self, message: str = "Game has not started"):
        super().__init__(message)


class InvalidPlayerException(InvalidGameStateException):
    """Exception raised when player information is invalid."""
    
    def __init__(self, message: str = "Invalid player"):
        super().__init__(message) 