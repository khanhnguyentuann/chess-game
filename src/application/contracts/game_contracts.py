"""
Game Contracts
Defines contracts for game state and legal moves operations.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ...shared.types.enums import GameState, Player
from .base_contracts import BaseRequest, BaseResponse


@dataclass(kw_only=True)
class GameStateRequest(BaseRequest):
    """Request contract for getting game state."""
    
    game_id: str
    
    def validate(self) -> bool:
        """Validate game state request."""
        return bool(self.game_id and self.game_id.strip())
    
    def get_validation_errors(self) -> list[str]:
        """Get validation errors for game state request."""
        errors = []
        if not self.game_id or not self.game_id.strip():
            errors.append("game_id is required")
        return errors


@dataclass
class GameStateResponse(BaseResponse):
    """Response contract for game state."""
    
    game_state: Optional[Dict[str, Any]] = None
    current_player: Optional[Player] = None
    game_status: Optional[GameState] = None
    move_count: int = 0
    
    @classmethod
    def from_game_state(cls, game_state: Dict[str, Any], message: str = "Game state retrieved") -> "GameStateResponse":
        """Create response from game state data."""
        return cls(
            success=True,
            data=game_state,
            game_state=game_state,
            message=message
        )


@dataclass(kw_only=True)
class LegalMovesRequest(BaseRequest):
    """Request contract for getting legal moves."""
    
    game_id: str
    square: Optional[int] = None  # If None, get all legal moves
    
    def validate(self) -> bool:
        """Validate legal moves request."""
        return len(self.get_validation_errors()) == 0
    
    def get_validation_errors(self) -> list[str]:
        """Get validation errors for legal moves request."""
        errors = []
        
        if not self.game_id or not self.game_id.strip():
            errors.append("game_id is required")
        
        if self.square is not None and not (0 <= self.square <= 63):
            errors.append("square must be between 0 and 63")
        
        return errors


@dataclass
class LegalMovesResponse(BaseResponse):
    """Response contract for legal moves."""
    
    legal_moves: List[Dict[str, Any]] = None
    square: Optional[int] = None
    
    def __post_init__(self):
        if self.legal_moves is None:
            self.legal_moves = []
    
    @classmethod
    def from_legal_moves(cls, legal_moves: List[Dict[str, Any]], square: Optional[int] = None, message: str = "Legal moves retrieved") -> "LegalMovesResponse":
        """Create response from legal moves data."""
        return cls(
            success=True,
            data={"legal_moves": legal_moves, "square": square},
            legal_moves=legal_moves,
            square=square,
            message=message
        ) 