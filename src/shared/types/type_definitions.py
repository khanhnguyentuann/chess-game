"""
Type Definitions and Protocols
Contains type hints, protocols, and data structures for the entire project
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    NamedTuple,
    Optional,
    Protocol,
    Tuple,
)

import chess
import pygame

from .enums import GameResult, GameState, InputAction, Player

if TYPE_CHECKING:
    from ...domain.events.game_events import GameEvent


# Basic type aliases
EventCallback = Callable[[Dict[str, Any]], None]
EventData = Dict[str, Any]


# Data structures
@dataclass
class Position:
    """Represents a position on the chess board."""

    file: int  # 0-7 (a-h)
    rank: int  # 0-7 (1-8)

    def to_square(self) -> int:
        """Convert to chess.py square index."""
        return self.rank * 8 + self.file

    @classmethod
    def from_square(cls, square: int) -> "Position":
        """Create Position from chess.py square index."""
        return cls(file=square % 8, rank=square // 8)

    def to_algebraic(self) -> str:
        """Convert to algebraic notation (e.g., 'e4')."""
        return chr(ord("a") + self.file) + str(self.rank + 1)


@dataclass
class MoveRequest:
    """Request to make a move."""

    from_square: int
    to_square: int
    promotion: Optional[int] = None  # Piece type for pawn promotion

    def to_chess_move(self) -> chess.Move:
        """Convert to python-chess Move object."""
        return chess.Move(self.from_square, self.to_square, self.promotion)


@dataclass
class MoveHistory:
    """Contains the complete move history of a game."""

    moves: List[chess.Move]
    timestamps: List[datetime]
    notations: List[str]  # Algebraic notation
    fens: List[str]  # FEN after each move

    def add_move(self, move: chess.Move, notation: str, fen: str) -> None:
        """Add a move to the history."""
        self.moves.append(move)
        self.timestamps.append(datetime.now())
        self.notations.append(notation)
        self.fens.append(fen)

    def get_last_move(self) -> Optional[chess.Move]:
        """Get the last move made."""
        return self.moves[-1] if self.moves else None

    def get_move_count(self) -> int:
        """Get total number of moves."""
        return len(self.moves)


@dataclass
class GameStateResponse:
    """Response object for game state queries."""

    game_id: str
    white_player: str
    black_player: str
    current_player: Player
    game_state: GameState
    is_ended: bool
    winner: Optional[Player]
    end_reason: Optional[str]
    move_count: int
    fen: str
    last_move: Optional[str]
    in_check: bool
    legal_moves_count: int


# Protocol definitions
class EventPublisher(Protocol):
    """Protocol for publishing game events."""

    def publish(self, event: "GameEvent") -> None:
        """Publish an event."""
        ...

    def subscribe(self, event_type: str, callback: EventCallback) -> None:
        """Subscribe to an event type."""
        ...


# Domain Protocols
class GameRepository(Protocol):
    """Protocol for game persistence."""

    def save_game(self, game_id: str, game_data: Dict[str, Any]) -> bool:
        """Save game state."""
        ...

    def load_game(self, game_id: str) -> Optional[Dict[str, Any]]:
        """Load game state."""
        ...

    def delete_game(self, game_id: str) -> bool:
        """Delete saved game."""
        ...


class MoveValidator(Protocol):
    """Protocol for move validation."""

    def is_valid_move(self, board: Any, from_square: int, to_square: int) -> bool:
        """Validate if a move is legal."""
        ...

    def get_legal_moves(self, board: Any, square: int) -> List[chess.Move]:
        """Get all legal moves from a square."""
        ...


class GameEngine(Protocol):
    """Protocol for chess engines (AI, analysis)."""

    def get_best_move(
        self, board: Any, time_limit: float = 1.0
    ) -> Optional[chess.Move]:
        """Get best move from engine."""
        ...

    def evaluate_position(self, board: Any) -> float:
        """Evaluate current position."""
        ...


# UI Protocols
class Renderer(Protocol):
    """Protocol for rendering components."""

    def render(self, surface: pygame.Surface, **kwargs) -> None:
        """Render component to surface."""
        ...


class InputHandler(Protocol):
    """Protocol for input handling."""

    def handle_input(self, event: pygame.event.Event) -> Optional[InputAction]:
        """Handle input event and return action."""
        ...


class ViewAdapter(Protocol):
    """Protocol for view adapters."""

    def show_screen(
        self, screen_type: str, data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Show a specific screen."""
        ...

    def update_display(self) -> None:
        """Update the display."""
        ...


# Application Layer Protocols
class UseCase(Protocol):
    """Base protocol for use cases."""

    def execute(self, request: Any) -> Any:
        """Execute the use case."""
        ...


class Command(Protocol):
    """Protocol for commands."""

    def execute(self) -> bool:
        """Execute the command."""
        ...

    def undo(self) -> bool:
        """Undo the command."""
        ...


class Query(Protocol):
    """Protocol for queries."""

    def execute(self) -> Any:
        """Execute the query."""
        ...


class EventPublisher(Protocol):
    """Protocol for event publishing."""

    def publish(self, event_type: str, data: EventData) -> None:
        """Publish an event."""
        ...

    def subscribe(self, event_type: str, callback: EventCallback) -> None:
        """Subscribe to an event."""
        ...


# Configuration Protocols
class ConfigProvider(Protocol):
    """Protocol for configuration providers."""

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        ...

    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        ...


# Data Transfer Objects
class MoveRequest:
    """Request object for making moves."""

    def __init__(
        self, from_square: int, to_square: int, promotion: Optional[int] = None
    ):
        self.from_square = from_square
        self.to_square = to_square
        self.promotion = promotion


class GameStateResponse:
    """Response object for game state queries."""

    def __init__(
        self,
        state: GameState,
        current_player: Player,
        board_fen: str,
        selected_square: Optional[int] = None,
        valid_moves: Optional[List[chess.Move]] = None,
        last_move: Optional[chess.Move] = None,
        result: Optional[GameResult] = None,
    ):
        self.state = state
        self.current_player = current_player
        self.board_fen = board_fen
        self.selected_square = selected_square
        self.valid_moves = valid_moves or []
        self.last_move = last_move
        self.result = result


class UIState:
    """UI state data object."""

    def __init__(self):
        self.selected_square: Optional[int] = None
        self.highlighted_squares: List[int] = []
        self.animations: List[Dict[str, Any]] = []
        self.show_coordinates: bool = False
        self.theme: str = "default"


# Exception types
class ChessGameException(Exception):
    """Base exception for chess game."""

    pass


class InvalidMoveException(ChessGameException):
    """Exception for invalid moves."""

    pass


class GameStateException(ChessGameException):
    """Exception for invalid game state."""

    pass


class UIException(ChessGameException):
    """Exception for UI-related errors."""

    pass


# Service interfaces
class IGameService(ABC):
    """Interface for game service."""

    @abstractmethod
    def create_new_game(self) -> str:
        """Create a new game and return game ID."""
        pass

    @abstractmethod
    def make_move(self, game_id: str, move_request: MoveRequest) -> bool:
        """Make a move in the game."""
        pass

    @abstractmethod
    def get_game_state(self, game_id: str) -> GameStateResponse:
        """Get current game state."""
        pass


class IEventService(ABC):
    """Interface for event service."""

    @abstractmethod
    def publish_event(self, event_type: str, data: EventData) -> None:
        """Publish an event."""
        pass

    @abstractmethod
    def subscribe_to_event(self, event_type: str, callback: EventCallback) -> None:
        """Subscribe to an event."""
        pass
