"""
Game Validator
Validates game state requests and operations.
"""

import logging
from abc import ABC, abstractmethod
from typing import List

from ...domain.entities.game import Game
from ..contracts.game_contracts import GameStateRequest, LegalMovesRequest


class IGameStateValidator(ABC):
    """Interface for game state validation."""
    
    @abstractmethod
    def validate_game_state_request(self, request: GameStateRequest, game: Game) -> bool:
        """Validate game state request."""
        pass
    
    @abstractmethod
    def validate_legal_moves_request(self, request: LegalMovesRequest, game: Game) -> bool:
        """Validate legal moves request."""
        pass
    
    @abstractmethod
    def get_validation_errors(self, request, game: Game) -> List[str]:
        """Get validation errors."""
        pass


class GameStateValidator(IGameStateValidator):
    """Validates game state requests at the application layer."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_game_state_request(self, request: GameStateRequest, game: Game) -> bool:
        """Validate game state request."""
        return len(self.get_validation_errors(request, game)) == 0
    
    def validate_legal_moves_request(self, request: LegalMovesRequest, game: Game) -> bool:
        """Validate legal moves request."""
        return len(self.get_validation_errors(request, game)) == 0
    
    def get_validation_errors(self, request, game: Game) -> List[str]:
        """Get validation errors for game requests."""
        errors = []
        
        # Validate request structure
        if not request.validate():
            errors.extend(request.get_validation_errors())
            return errors
        
        # Validate game exists
        if not game:
            errors.append("Game not found")
            return errors
        
        # Validate game ID matches if provided
        if hasattr(request, 'game_id') and request.game_id and game.game_id != request.game_id:
            errors.append("Game ID mismatch")
        
        # Additional validation for legal moves request
        if isinstance(request, LegalMovesRequest):
            if request.square is not None:
                # Validate square has a piece
                piece = game.board.get_piece_at(request.square)
                if not piece:
                    errors.append("No piece at specified square")
                elif piece.color != game.current_player:
                    errors.append("Cannot get legal moves for opponent's piece")
        
        return errors 