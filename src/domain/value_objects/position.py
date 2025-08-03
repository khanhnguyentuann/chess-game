"""
Position Value Object
Represents a chess position with validation and utility methods.
"""

from dataclasses import dataclass
from typing import List, Optional

import chess

from ...shared.types.enums import Player
from .square import Square


@dataclass(frozen=True)
class Position:
    """Immutable value object representing a chess position."""
    
    fen: str
    current_player: Player
    
    def __post_init__(self):
        """Validate position."""
        try:
            # Validate FEN format
            chess.Board(self.fen)
        except ValueError as e:
            raise ValueError(f"Invalid FEN string: {e}")
    
    @classmethod
    def from_fen(cls, fen: str) -> "Position":
        """Create position from FEN string."""
        board = chess.Board(fen)
        current_player = Player.WHITE if board.turn else Player.BLACK
        return cls(fen=fen, current_player=current_player)
    
    @classmethod
    def starting_position(cls) -> "Position":
        """Create starting position."""
        return cls.from_fen(chess.STARTING_FEN)
    
    def to_board(self) -> chess.Board:
        """Convert to python-chess Board object."""
        return chess.Board(self.fen)
    
    @property
    def is_check(self) -> bool:
        """Check if current player is in check."""
        board = self.to_board()
        return board.is_check()
    
    @property
    def is_checkmate(self) -> bool:
        """Check if current player is checkmated."""
        board = self.to_board()
        return board.is_checkmate()
    
    @property
    def is_stalemate(self) -> bool:
        """Check if position is stalemate."""
        board = self.to_board()
        return board.is_stalemate()
    
    @property
    def is_insufficient_material(self) -> bool:
        """Check if position has insufficient material."""
        board = self.to_board()
        return board.is_insufficient_material()
    
    @property
    def is_game_over(self) -> bool:
        """Check if game is over."""
        board = self.to_board()
        return board.is_game_over()
    
    def get_legal_moves(self) -> List[chess.Move]:
        """Get all legal moves in current position."""
        board = self.to_board()
        return list(board.legal_moves)
    
    def get_legal_moves_from_square(self, square: Square) -> List[chess.Move]:
        """Get legal moves from specific square."""
        board = self.to_board()
        return [move for move in board.legal_moves if move.from_square == square.index]
    
    def is_move_legal(self, move: chess.Move) -> bool:
        """Check if move is legal in current position."""
        board = self.to_board()
        return move in board.legal_moves
    
    def apply_move(self, move: chess.Move) -> "Position":
        """Apply move and return new position."""
        board = self.to_board()
        board.push(move)
        new_fen = board.fen()
        new_player = Player.BLACK if self.current_player == Player.WHITE else Player.WHITE
        return Position(fen=new_fen, current_player=new_player)
    
    def get_piece_at(self, square: Square) -> Optional[chess.Piece]:
        """Get piece at square."""
        board = self.to_board()
        return board.piece_at(square.index)
    
    def get_piece_color(self, square: Square) -> Optional[Player]:
        """Get color of piece at square."""
        piece = self.get_piece_at(square)
        if piece is None:
            return None
        return Player.WHITE if piece.color else Player.BLACK
    
    def is_square_empty(self, square: Square) -> bool:
        """Check if square is empty."""
        return self.get_piece_at(square) is None
    
    def __str__(self) -> str:
        return f"Position({self.fen[:20]}..., {self.current_player})"
    
    def __repr__(self) -> str:
        return f"Position(fen='{self.fen}', current_player={self.current_player})" 