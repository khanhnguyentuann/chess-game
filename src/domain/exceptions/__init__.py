"""
Domain Exceptions
Domain-specific exceptions for business rule violations.
"""

from .game_exceptions import (
    GameAlreadyEndedException,
    GameNotStartedException,
    InvalidGameStateException,
    InvalidPlayerException,
)
from .move_exceptions import (
    IllegalMoveException,
    InvalidMoveException,
    InvalidSquareException,
    NoPieceAtSquareException,
    WrongPlayerException,
)

__all__ = [
    # Game exceptions
    "GameAlreadyEndedException",
    "GameNotStartedException", 
    "InvalidGameStateException",
    "InvalidPlayerException",
    
    # Move exceptions
    "IllegalMoveException",
    "InvalidMoveException",
    "InvalidSquareException",
    "NoPieceAtSquareException",
    "WrongPlayerException",
] 