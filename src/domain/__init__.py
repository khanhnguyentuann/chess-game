"""
Domain Layer
Core business logic and domain entities for the chess game.
"""

# Import entities
try:
    from .entities import Board, Game, MoveHistory
except ImportError:
    pass

# Import events
try:
    from .events import DomainEvent, GameStartedEvent, MoveMadeEvent, GameEndedEvent
except ImportError:
    pass

# Import exceptions
try:
    from .exceptions import (
        GameAlreadyEndedException,
        IllegalMoveException,
        InvalidMoveException,
        InvalidSquareException,
        NoPieceAtSquareException,
        WrongPlayerException,
    )
except ImportError:
    pass

# Import services
try:
    from .services import GameRulesService, MoveValidatorService
except ImportError:
    pass

# Import value objects
try:
    from .value_objects import Move, Position, Square
except ImportError:
    pass

__all__ = [
    # Entities
    "Board",
    "Game", 
    "MoveHistory",
    
    # Events
    "DomainEvent",
    "GameStartedEvent",
    "MoveMadeEvent", 
    "GameEndedEvent",
    
    # Exceptions
    "GameAlreadyEndedException",
    "IllegalMoveException",
    "InvalidMoveException",
    "InvalidSquareException",
    "NoPieceAtSquareException",
    "WrongPlayerException",
    
    # Services
    "GameRulesService",
    "MoveValidatorService",
    
    # Value Objects
    "Move",
    "Position",
    "Square",
] 