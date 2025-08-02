"""
Move History Entity
Domain entity representing the history of moves in a chess game.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import chess

from ...shared.types.enums import Player
from ..events.game_events import EventType


class MoveRecord:
    """Individual move record within move history."""

    def __init__(
        self,
        move: chess.Move,
        player: Player,
        fen_before: str,
        fen_after: str,
        move_number: int,
        timestamp: Optional[datetime] = None,
        captured_piece: Optional[str] = None,
        is_check: bool = False,
        is_checkmate: bool = False,
        annotation: Optional[str] = None,
    ):
        self.move = move
        self.player = player
        self.fen_before = fen_before
        self.fen_after = fen_after
        self.move_number = move_number
        self.timestamp = timestamp or datetime.now()
        self.captured_piece = captured_piece
        self.is_check = is_check
        self.is_checkmate = is_checkmate
        self.annotation = annotation

    def to_dict(self) -> Dict[str, Any]:
        """Convert move record to dictionary."""
        return {
            "move": str(self.move),
            "player": self.player.value,
            "fen_before": self.fen_before,
            "fen_after": self.fen_after,
            "move_number": self.move_number,
            "timestamp": self.timestamp.isoformat(),
            "captured_piece": self.captured_piece,
            "is_check": self.is_check,
            "is_checkmate": self.is_checkmate,
            "annotation": self.annotation,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MoveRecord":
        """Create move record from dictionary."""
        return cls(
            move=chess.Move.from_uci(data["move"]),
            player=Player(data["player"]),
            fen_before=data["fen_before"],
            fen_after=data["fen_after"],
            move_number=data["move_number"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            captured_piece=data.get("captured_piece"),
            is_check=data.get("is_check", False),
            is_checkmate=data.get("is_checkmate", False),
            annotation=data.get("annotation"),
        )

    def __str__(self) -> str:
        return f"{self.move_number}. {self.move}"

    def __repr__(self) -> str:
        return f"MoveRecord(move={self.move}, player={self.player}, move_number={self.move_number})"


class MoveHistory:
    """
    Move history entity for tracking all moves in a chess game.
    This is an aggregate root that contains the complete history of moves.
    """

    def __init__(
        self,
        game_id: str,
        history_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ):
        self.history_id = history_id or str(uuid.uuid4())
        self.game_id = game_id
        self.moves: List[MoveRecord] = []
        self.created_at = created_at or datetime.now()
        self.current_position = 0  # For undo/redo navigation

    def add_move(
        self,
        move: chess.Move,
        player: Player,
        fen_before: str,
        fen_after: str,
        captured_piece: Optional[str] = None,
        is_check: bool = False,
        is_checkmate: bool = False,
        annotation: Optional[str] = None,
    ) -> MoveRecord:
        """
        Add a new move to the history.

        Args:
            move: Chess move
            player: Player who made the move
            fen_before: Board position before move
            fen_after: Board position after move
            captured_piece: Piece captured (if any)
            is_check: Whether move puts opponent in check
            is_checkmate: Whether move is checkmate
            annotation: Optional move annotation

        Returns:
            Created MoveRecord
        """
        move_number = len(self.moves) + 1

        move_record = MoveRecord(
            move=move,
            player=player,
            fen_before=fen_before,
            fen_after=fen_after,
            move_number=move_number,
            captured_piece=captured_piece,
            is_check=is_check,
            is_checkmate=is_checkmate,
            annotation=annotation,
        )

        # If we're not at the end of history (due to undo), truncate future moves
        if self.current_position < len(self.moves):
            self.moves = self.moves[: self.current_position]

        self.moves.append(move_record)
        self.current_position = len(self.moves)

        return move_record

    def undo_move(self) -> Optional[MoveRecord]:
        """
        Undo the last move.

        Returns:
            Undone move record or None if no moves to undo
        """
        if self.current_position > 0:
            self.current_position -= 1
            return self.moves[self.current_position]
        return None

    def redo_move(self) -> Optional[MoveRecord]:
        """
        Redo the next move.

        Returns:
            Redone move record or None if no moves to redo
        """
        if self.current_position < len(self.moves):
            move_record = self.moves[self.current_position]
            self.current_position += 1
            return move_record
        return None

    def can_undo(self) -> bool:
        """Check if undo is possible."""
        return self.current_position > 0

    def can_redo(self) -> bool:
        """Check if redo is possible."""
        return self.current_position < len(self.moves)

    def get_move_count(self) -> int:
        """Get total number of moves played (not including undone moves)."""
        return self.current_position

    def get_total_moves(self) -> int:
        """Get total number of moves in history (including undone moves)."""
        return len(self.moves)

    def get_current_move(self) -> Optional[MoveRecord]:
        """Get the current move (last played move)."""
        if self.current_position > 0:
            return self.moves[self.current_position - 1]
        return None

    def get_move_at_position(self, position: int) -> Optional[MoveRecord]:
        """Get move at specific position."""
        if 0 <= position < len(self.moves):
            return self.moves[position]
        return None

    def get_active_moves(self) -> List[MoveRecord]:
        """Get only the currently active moves (excluding undone moves)."""
        return self.moves[: self.current_position]

    def get_all_moves(self) -> List[MoveRecord]:
        """Get all moves in history."""
        return self.moves.copy()

    def clear(self) -> None:
        """Clear all move history."""
        self.moves.clear()
        self.current_position = 0

    def get_pgn(self) -> str:
        """
        Get PGN representation of the move history.

        Returns:
            PGN string of active moves
        """
        pgn_moves = []
        active_moves = self.get_active_moves()

        for i, move_record in enumerate(active_moves):
            if i % 2 == 0:  # White's move
                move_number = (i // 2) + 1
                pgn_moves.append(f"{move_number}.")

            pgn_moves.append(str(move_record.move))

            if move_record.is_checkmate:
                pgn_moves[-1] += "#"
            elif move_record.is_check:
                pgn_moves[-1] += "+"

        return " ".join(pgn_moves)

    def to_dict(self) -> Dict[str, Any]:
        """Convert move history to dictionary."""
        return {
            "history_id": self.history_id,
            "game_id": self.game_id,
            "moves": [move.to_dict() for move in self.moves],
            "current_position": self.current_position,
            "created_at": self.created_at.isoformat(),
            "move_count": self.get_move_count(),
            "total_moves": self.get_total_moves(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MoveHistory":
        """Create move history from dictionary."""
        history = cls(
            game_id=data["game_id"],
            history_id=data["history_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
        )

        # Restore moves
        for move_data in data["moves"]:
            move_record = MoveRecord.from_dict(move_data)
            history.moves.append(move_record)

        history.current_position = data.get("current_position", len(history.moves))

        return history

    def __str__(self) -> str:
        return f"MoveHistory(game_id={self.game_id}, moves={self.get_move_count()})"

    def __repr__(self) -> str:
        return f"MoveHistory(history_id={self.history_id}, game_id={self.game_id}, moves={len(self.moves)})"
