"""
Move Contracts
Defines contracts for move-related operations.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ...shared.types.enums import Player
from .base_contracts import BaseRequest, BaseResponse


@dataclass(kw_only=True)
class MoveRequest(BaseRequest):
    """Request contract for making a move."""

    from_square: int
    to_square: int
    promotion_piece: Optional[str] = None
    player: Optional[Player] = None
    game_id: Optional[str] = None
    
    def validate(self) -> bool:
        """Validate move request data."""
        return len(self.get_validation_errors()) == 0
    
    def get_validation_errors(self) -> list[str]:
        """Get validation errors for move request."""
        errors = []
        
        # Validate square coordinates
        if not (0 <= self.from_square <= 63):
            errors.append("from_square must be between 0 and 63")
        
        if not (0 <= self.to_square <= 63):
            errors.append("to_square must be between 0 and 63")
        
        if self.from_square == self.to_square:
            errors.append("from_square and to_square cannot be the same")
        
        # Validate promotion piece if provided
        if self.promotion_piece and self.promotion_piece not in ['q', 'r', 'b', 'n']:
            errors.append("promotion_piece must be one of: q, r, b, n")
        
        return errors


@dataclass
class MoveResponse(BaseResponse):
    """Response contract for move operations."""
    
    move_data: Optional[Dict[str, Any]] = None
    legal_moves: Optional[List[Dict[str, Any]]] = None
    game_state: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_move_data(cls, move_data: Dict[str, Any], message: str = "Move executed successfully") -> "MoveResponse":
        """Create response from move data."""
        return cls(
            success=True,
            data=move_data,
            move_data=move_data,
            message=message
        )
    
    @classmethod
    def from_legal_moves(cls, legal_moves: List[Dict[str, Any]], message: str = "Legal moves retrieved") -> "MoveResponse":
        """Create response from legal moves data."""
        return cls(
            success=True,
            data={"legal_moves": legal_moves},
            legal_moves=legal_moves,
            message=message
        ) 