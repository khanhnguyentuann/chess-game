"""
Move Exceptions
Domain exceptions for move-related business rule violations.
"""


class InvalidMoveException(Exception):
    """Base exception for invalid move operations."""
    pass


class IllegalMoveException(InvalidMoveException):
    """Exception raised when a move is illegal according to chess rules."""
    
    def __init__(self, message: str = "Move is illegal"):
        super().__init__(message)


class InvalidSquareException(InvalidMoveException):
    """Exception raised when square coordinates are invalid."""
    
    def __init__(self, square: int, message: str = None):
        if message is None:
            message = f"Invalid square: {square}. Must be between 0 and 63."
        super().__init__(message)


class NoPieceAtSquareException(InvalidMoveException):
    """Exception raised when trying to move from an empty square."""
    
    def __init__(self, square: int, message: str = None):
        if message is None:
            message = f"No piece at square {square}"
        super().__init__(message)


class WrongPlayerException(InvalidMoveException):
    """Exception raised when trying to move opponent's piece."""
    
    def __init__(self, message: str = "Cannot move opponent's piece"):
        super().__init__(message) 