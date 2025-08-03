"""
Move Value Object
Represents a chess move with validation and utility methods.
"""

from dataclasses import dataclass
from typing import Optional

import chess

from ...shared.types.enums import PieceType, Player
from .square import Square


@dataclass(frozen=True)
class Move:
    """Immutable value object representing a chess move."""
    
    from_square: Square
    to_square: Square
    promotion: Optional[PieceType] = None
    
    def __post_init__(self):
        """Validate move."""
        if self.from_square == self.to_square:
            raise ValueError("From and to squares cannot be the same")
        
        if self.promotion and self.promotion not in [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT]:
            raise ValueError("Invalid promotion piece")
    
    @classmethod
    def from_squares(cls, from_square: Square, to_square: Square, promotion: Optional[PieceType] = None) -> "Move":
        """Create move from squares."""
        return cls(from_square=from_square, to_square=to_square, promotion=promotion)
    
    @classmethod
    def from_indices(cls, from_index: int, to_index: int, promotion: Optional[PieceType] = None) -> "Move":
        """Create move from indices."""
        from_square = Square(from_index)
        to_square = Square(to_index)
        return cls(from_square=from_square, to_square=to_square, promotion=promotion)
    
    @classmethod
    def from_chess_move(cls, chess_move: chess.Move) -> "Move":
        """Create move from python-chess Move object."""
        from_square = Square(chess_move.from_square)
        to_square = Square(chess_move.to_square)
        promotion = PieceType(chess_move.promotion) if chess_move.promotion else None
        return cls(from_square=from_square, to_square=to_square, promotion=promotion)
    
    def to_chess_move(self) -> chess.Move:
        """Convert to python-chess Move object."""
        promotion_value = self.promotion.value if self.promotion else None
        return chess.Move(self.from_square.index, self.to_square.index, promotion_value)
    
    @property
    def is_capture(self) -> bool:
        """Check if move is a capture (to be determined by board state)."""
        # This is a placeholder - actual capture detection requires board state
        return False
    
    @property
    def is_castling(self) -> bool:
        """Check if move is castling."""
        return (
            self.from_square.index in [4, 60] and  # King starting positions
            self.to_square.index in [2, 6, 58, 62]  # Castling destination squares
        )
    
    @property
    def is_en_passant(self) -> bool:
        """Check if move is en passant (to be determined by board state)."""
        # This is a placeholder - actual en passant detection requires board state
        return False
    
    @property
    def is_pawn_promotion(self) -> bool:
        """Check if move is a pawn promotion."""
        # Pawn promotion: from rank 6 to rank 7 (white) or rank 1 to rank 0 (black)
        from_rank = self.from_square.rank
        to_rank = self.to_square.rank
        return (from_rank == 6 and to_rank == 7) or (from_rank == 1 and to_rank == 0)
    
    def get_notation(self) -> str:
        """Get algebraic notation for the move."""
        from_notation = self.from_square.algebraic_notation
        to_notation = self.to_square.algebraic_notation
        
        if self.promotion:
            promotion_symbol = self.promotion.symbol.upper()
            return f"{from_notation}{to_notation}={promotion_symbol}"
        
        return f"{from_notation}{to_notation}"
    
    def __str__(self) -> str:
        return self.get_notation()
    
    def __repr__(self) -> str:
        promotion_str = f", promotion={self.promotion}" if self.promotion else ""
        return f"Move({self.from_square} -> {self.to_square}{promotion_str})" 