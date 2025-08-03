"""
Move Validator
Validates move requests according to business rules.
"""

import logging
from abc import ABC, abstractmethod
from typing import List

from ...domain.entities.game import Game
from ...domain.interfaces.services import IMoveValidationService
from ...shared.exceptions.game_exceptions import InvalidMoveException
from ..contracts.move_contracts import MoveRequest


class IApplicationMoveValidator(ABC):
    """Interface for application-level move validation."""
    
    @abstractmethod
    def validate_move_request(self, request: MoveRequest, game: Game) -> bool:
        """Validate move request against business rules."""
        pass
    
    @abstractmethod
    def get_validation_errors(self, request: MoveRequest, game: Game) -> List[str]:
        """Get detailed validation errors."""
        pass


class MoveRequestValidator(IApplicationMoveValidator):
    """Validates move requests at the application layer."""
    
    def __init__(self, domain_move_validator: IMoveValidationService):
        self.domain_move_validator = domain_move_validator
        self.logger = logging.getLogger(__name__)
    
    def validate_move_request(self, request: MoveRequest, game: Game) -> bool:
        """Validate move request against business rules."""
        return len(self.get_validation_errors(request, game)) == 0
    
    def get_validation_errors(self, request: MoveRequest, game: Game) -> List[str]:
        """Get detailed validation errors for move request."""
        errors = []
        
        # Validate request structure
        if not request.validate():
            errors.extend(request.get_validation_errors())
            return errors
        
        # Validate game state
        if game.is_ended:
            errors.append("Cannot make move: game has ended")
            return errors
        
        # Validate player turn
        if request.player and request.player != game.current_player:
            errors.append(f"Not {request.player.value}'s turn")
        
        # Validate move using domain validator
        try:
            # Check if move is legal using domain validation
            legal_moves = self.domain_move_validator.get_legal_moves(game.board, request.from_square)
            move_is_legal = any(
                move['to_square'] == request.to_square 
                for move in legal_moves
            )
            
            if not move_is_legal:
                errors.append("Move is not legal according to chess rules")
                
        except Exception as e:
            self.logger.error(f"Error validating move with domain validator: {e}")
            errors.append("Error validating move with chess engine")
        
        return errors 