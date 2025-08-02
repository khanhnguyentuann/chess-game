"""
Domain Events - Game and Board Events
NEW FILE - Event system for domain layer communication
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

import chess

from ...shared.types.enums import GameResult, GameState, Player


class EventType(Enum):
    """Domain event types."""

    # Board events
    MOVE_MADE = "move_made"
    MOVE_UNDONE = "move_undone"
    MOVE_REDONE = "move_redone"
    BOARD_RESET = "board_reset"
    POSITION_SET = "position_set"

    # Game events
    GAME_STARTED = "game_started"
    GAME_ENDED = "game_ended"
    GAME_PAUSED = "game_paused"
    GAME_RESUMED = "game_resumed"
    GAME_RESET = "game_reset"

    # Selection events
    SQUARE_SELECTED = "square_selected"
    SELECTION_CLEARED = "selection_cleared"

    # State change events
    PLAYER_TURN_CHANGED = "player_turn_changed"
    CHECK_DETECTED = "check_detected"
    CHECKMATE_DETECTED = "checkmate_detected"
    STALEMATE_DETECTED = "stalemate_detected"
    DRAW_DETECTED = "draw_detected"


@dataclass
class DomainEvent:
    """Base domain event."""

    event_type: EventType
    timestamp: datetime
    data: Dict[str, Any]
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self):
        if not isinstance(self.timestamp, datetime):
            self.timestamp = datetime.now()


@dataclass
class BoardEvent(DomainEvent):
    """Board-specific events."""

    fen: str = field(default="")
    current_player: Player = field(default=Player.WHITE)

    @classmethod
    def move_made(
        cls, move: chess.Move, fen: str, current_player: Player
    ) -> "BoardEvent":
        return cls(
            event_type=EventType.MOVE_MADE,
            timestamp=datetime.now(),
            data={"move": move},
            fen=fen,
            current_player=current_player,
        )

    @classmethod
    def move_undone(
        cls, undone_move: chess.Move, fen: str, current_player: Player
    ) -> "BoardEvent":
        return cls(
            event_type=EventType.MOVE_UNDONE,
            timestamp=datetime.now(),
            data={"undone_move": undone_move},
            fen=fen,
            current_player=current_player,
        )

    @classmethod
    def board_reset(cls, fen: str, current_player: Player) -> "BoardEvent":
        return cls(
            event_type=EventType.BOARD_RESET,
            timestamp=datetime.now(),
            data={},
            fen=fen,
            current_player=current_player,
        )


@dataclass
class GameEvent(DomainEvent):
    """Game-specific events."""

    game_id: str = field(default="")
    game_state: GameState = field(default=GameState.PLAYING)

    @classmethod
    def game_started(cls, game_id: str) -> "GameEvent":
        return cls(
            event_type=EventType.GAME_STARTED,
            timestamp=datetime.now(),
            data={},
            game_id=game_id,
            game_state=GameState.PLAYING,
        )

    @classmethod
    def game_ended(
        cls, game_id: str, result: GameResult, winner: Optional[Player] = None
    ) -> "GameEvent":
        return cls(
            event_type=EventType.GAME_ENDED,
            timestamp=datetime.now(),
            data={"result": result, "winner": winner},
            game_id=game_id,
            game_state=GameState.GAME_OVER,
        )

    @classmethod
    def square_selected(
        cls, game_id: str, square: int, valid_moves: list
    ) -> "GameEvent":
        return cls(
            event_type=EventType.SQUARE_SELECTED,
            timestamp=datetime.now(),
            data={"square": square, "valid_moves": valid_moves},
            game_id=game_id,
            game_state=GameState.PLAYING,
        )


@dataclass
class CheckEvent(DomainEvent):
    """Check/Checkmate/Stalemate events."""

    player_in_check: Player = field(default=Player.WHITE)
    is_checkmate: bool = field(default=False)
    is_stalemate: bool = field(default=False)

    @classmethod
    def check_detected(cls, player: Player) -> "CheckEvent":
        return cls(
            event_type=EventType.CHECK_DETECTED,
            timestamp=datetime.now(),
            data={},
            player_in_check=player,
            is_checkmate=False,
            is_stalemate=False,
        )

    @classmethod
    def checkmate_detected(cls, player: Player) -> "CheckEvent":
        return cls(
            event_type=EventType.CHECKMATE_DETECTED,
            timestamp=datetime.now(),
            data={},
            player_in_check=player,
            is_checkmate=True,
            is_stalemate=False,
        )

    @classmethod
    def stalemate_detected(cls) -> "CheckEvent":
        return cls(
            event_type=EventType.STALEMATE_DETECTED,
            timestamp=datetime.now(),
            data={},
            player_in_check=Player.WHITE,  # Dummy value, not relevant for stalemate
            is_checkmate=False,
            is_stalemate=True,
        )


# Event factory for convenience
class EventFactory:
    """Factory for creating domain events."""

    @staticmethod
    def create_move_event(
        move: chess.Move, fen: str, current_player: Player
    ) -> BoardEvent:
        """Create a move made event."""
        return BoardEvent.move_made(move, fen, current_player)

    @staticmethod
    def create_selection_event(
        game_id: str, square: int, valid_moves: list
    ) -> GameEvent:
        """Create a square selection event."""
        return GameEvent.square_selected(game_id, square, valid_moves)

    @staticmethod
    def create_game_end_event(
        game_id: str, result: GameResult, winner: Optional[Player] = None
    ) -> GameEvent:
        """Create a game ended event."""
        return GameEvent.game_ended(game_id, result, winner)

    @staticmethod
    def create_check_event(player: Player, is_checkmate: bool = False) -> CheckEvent:
        """Create a check or checkmate event."""
        if is_checkmate:
            return CheckEvent.checkmate_detected(player)
        else:
            return CheckEvent.check_detected(player)


# Event publisher interface implementation will be in infrastructure layer
class EventDispatcher:
    """Simple event dispatcher for domain events."""

    def __init__(self):
        self._subscribers: Dict[EventType, list] = {}

    def subscribe(self, event_type: EventType, callback):
        """Subscribe to an event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def publish(self, event: DomainEvent):
        """Publish a domain event."""
        if event.event_type in self._subscribers:
            for callback in self._subscribers[event.event_type]:
                try:
                    callback(event)
                except Exception as e:
                    # Log error but don't stop other subscribers
                    print(f"Error in event subscriber: {e}")

    def unsubscribe(self, event_type: EventType, callback):
        """Unsubscribe from an event type."""
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(callback)
            except ValueError:
                pass  # Callback not found

    def clear_subscribers(self, event_type: Optional[EventType] = None):
        """Clear subscribers for event type or all."""
        if event_type:
            self._subscribers[event_type] = []
        else:
            self._subscribers.clear()


@dataclass
class MoveEvent(GameEvent):
    """Specialized event for move-related actions."""

    move_data: Dict[str, Any] = field(default_factory=dict)
    player: Player = field(default=Player.WHITE)
    captured_piece: Optional[str] = field(default=None)
    is_check: bool = field(default=False)
    is_checkmate: bool = field(default=False)
    game_status: Optional[Dict[str, Any]] = field(default=None)
