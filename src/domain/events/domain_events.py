"""
Domain Events
Domain events that represent important business occurrences.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional

from ...shared.types.enums import GameState, Player
from ..value_objects.move import Move
from ..value_objects.square import Square


@dataclass
class DomainEvent(ABC):
    """Base class for all domain events."""
    
    event_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    aggregate_id: str = ""
    version: int = 1
    
    @abstractmethod
    def event_type(self) -> str:
        """Get the type of this event."""
        pass


@dataclass(kw_only=True)
class GameStartedEvent(DomainEvent):
    """Event raised when a new game starts."""
    
    white_player: str
    black_player: str
    first_player: Player
    
    def event_type(self) -> str:
        return "GameStarted"


@dataclass(kw_only=True)
class MoveMadeEvent(DomainEvent):
    """Event raised when a move is made."""
    
    from_square: Square
    to_square: Square
    player: Player
    move_notation: str
    is_capture: bool = False
    is_check: bool = False
    is_checkmate: bool = False
    promotion_piece: Optional[str] = None
    
    def event_type(self) -> str:
        return "MoveMade"


@dataclass(kw_only=True)
class GameStateChangedEvent(DomainEvent):
    """Event raised when game state changes."""
    
    old_state: GameState
    new_state: GameState
    reason: str
    
    def event_type(self) -> str:
        return "GameStateChanged"


@dataclass(kw_only=True)
class GameEndedEvent(DomainEvent):
    """Event raised when a game ends."""
    
    winner: Optional[Player]
    end_reason: str
    final_state: GameState
    
    def event_type(self) -> str:
        return "GameEnded"


@dataclass(kw_only=True)
class PieceSelectedEvent(DomainEvent):
    """Event raised when a piece is selected."""
    
    square: Square
    player: Player
    legal_moves_count: int
    
    def event_type(self) -> str:
        return "PieceSelected"


@dataclass(kw_only=True)
class MoveUndoneEvent(DomainEvent):
    """Event raised when a move is undone."""
    
    undone_move: Move
    player: Player
    
    def event_type(self) -> str:
        return "MoveUndone"


@dataclass(kw_only=True)
class MoveRedoneEvent(DomainEvent):
    """Event raised when a move is redone."""
    
    redone_move: Move
    player: Player
    
    def event_type(self) -> str:
        return "MoveRedone"


@dataclass(kw_only=True)
class InvalidMoveAttemptedEvent(DomainEvent):
    """Event raised when an invalid move is attempted."""
    
    attempted_move: Move
    player: Player
    reason: str
    
    def event_type(self) -> str:
        return "InvalidMoveAttempted"


@dataclass(kw_only=True)
class PlayerTurnChangedEvent(DomainEvent):
    """Event raised when player turn changes."""
    
    previous_player: Player
    current_player: Player
    
    def event_type(self) -> str:
        return "PlayerTurnChanged" 