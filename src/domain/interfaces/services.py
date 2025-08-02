"""
Domain Service Interfaces
Defines contracts for domain services without implementation details.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import chess

from ...shared.types.enums import GameResult, Player
from ...shared.types.type_definitions import MoveRequest, Position
from ..entities.board import Board
from ..entities.game import Game


class IGameService(ABC):
    """Interface for core game management."""

    @abstractmethod
    async def create_new_game(
        self,
        white_player: str,
        black_player: str,
        settings: Optional[Dict[str, Any]] = None,
    ) -> Game:
        """Create a new chess game."""
        pass

    @abstractmethod
    async def make_move(self, game: Game, move_request: MoveRequest) -> bool:
        """Execute a move in the game."""
        pass

    @abstractmethod
    async def get_game_status(self, game: Game) -> Dict[str, Any]:
        """Get current game status and metadata."""
        pass

    @abstractmethod
    async def end_game(self, game: Game, result: GameResult, reason: str) -> bool:
        """End the game with specified result."""
        pass


class IMoveValidationService(ABC):
    """Interface for move validation logic."""

    @abstractmethod
    def validate_move_request(self, game: Game, move_request: MoveRequest) -> bool:
        """Validate if a move request is legal."""
        pass

    @abstractmethod
    def get_legal_moves_for_square(self, board: Board, square: int) -> List[chess.Move]:
        """Get all legal moves from a square."""
        pass

    @abstractmethod
    def get_all_legal_moves(self, board: Board) -> List[chess.Move]:
        """Get all legal moves in current position."""
        pass

    @abstractmethod
    def is_square_attackable(
        self, board: Board, square: int, by_player: Player
    ) -> bool:
        """Check if square is attackable by player."""
        pass

    @abstractmethod
    def analyze_move_safety(self, board: Board, move: chess.Move) -> Dict[str, Any]:
        """Analyze safety implications of a move."""
        pass


class IBoardAnalysisService(ABC):
    """Interface for board position analysis."""

    @abstractmethod
    def evaluate_position(self, board: Board) -> float:
        """Evaluate board position (-infinity to +infinity)."""
        pass

    @abstractmethod
    def find_tactical_moves(self, board: Board) -> List[chess.Move]:
        """Find tactical opportunities (captures, checks, etc.)."""
        pass

    @abstractmethod
    def get_piece_activity(self, board: Board) -> Dict[str, Any]:
        """Analyze piece activity and coordination."""
        pass

    @abstractmethod
    def analyze_king_safety(self, board: Board, player: Player) -> Dict[str, Any]:
        """Analyze king safety for a player."""
        pass


class INotificationService(ABC):
    """Interface for game notifications and events."""

    @abstractmethod
    async def notify_move_made(self, game: Game, move_data: Dict[str, Any]) -> None:
        """Notify that a move was made."""
        pass

    @abstractmethod
    async def notify_game_over(self, game: Game, result: GameResult) -> None:
        """Notify that game ended."""
        pass

    @abstractmethod
    async def notify_check(self, game: Game, player: Player) -> None:
        """Notify that a player is in check."""
        pass

    @abstractmethod
    async def notify_error(self, error_message: str, context: Dict[str, Any]) -> None:
        """Notify about errors."""
        pass


class IAIEngineService(ABC):
    """Interface for AI chess engines."""

    @abstractmethod
    async def get_best_move(
        self, board: Board, time_limit: float = 1.0, depth: Optional[int] = None
    ) -> Optional[chess.Move]:
        """Get best move from AI engine."""
        pass

    @abstractmethod
    async def analyze_position(self, board: Board, depth: int = 15) -> Dict[str, Any]:
        """Get detailed position analysis."""
        pass

    @abstractmethod
    async def set_skill_level(self, level: int) -> None:
        """Set AI skill level (0-20)."""
        pass


class IGameStateSerializer(ABC):
    """Interface for game state serialization."""

    @abstractmethod
    def serialize_game(self, game: Game) -> str:
        """Serialize game to string format."""
        pass

    @abstractmethod
    def deserialize_game(self, data: str) -> Game:
        """Deserialize game from string format."""
        pass

    @abstractmethod
    def export_pgn(self, game: Game) -> str:
        """Export game to PGN format."""
        pass

    @abstractmethod
    def import_pgn(self, pgn_data: str) -> Game:
        """Import game from PGN format."""
        pass
