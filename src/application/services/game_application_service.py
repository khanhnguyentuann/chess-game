"""
Game Application Service
Orchestrates game operations using use cases and provides a unified interface.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ...domain.entities.game import Game
from ...domain.interfaces.repositories import IGameRepository
from ...shared.exceptions.game_exceptions import GameNotFoundException
from ..contracts.game_contracts import GameStateRequest, GameStateResponse, LegalMovesRequest, LegalMovesResponse
from ..contracts.move_contracts import MoveRequest, MoveResponse
from ..use_cases.make_move import MakeMoveUseCase
from ..use_cases.get_legal_moves import GetLegalMovesUseCase
from ..use_cases.undo_move import UndoMoveUseCase
from ..use_cases.redo_move import RedoMoveUseCase
from ..validators.game_validator import IGameStateValidator
from ..validators.move_validator import IApplicationMoveValidator


class IGameApplicationService(ABC):
    """Interface for game application service."""
    
    @abstractmethod
    async def make_move(self, request: MoveRequest) -> MoveResponse:
        """Make a move in the game."""
        pass
    
    @abstractmethod
    async def get_legal_moves(self, request: LegalMovesRequest) -> LegalMovesResponse:
        """Get legal moves for the current game state."""
        pass
    
    @abstractmethod
    async def get_game_state(self, request: GameStateRequest) -> GameStateResponse:
        """Get current game state."""
        pass
    
    @abstractmethod
    async def undo_last_move(self, game_id: str) -> MoveResponse:
        """Undo the last move."""
        pass
    
    @abstractmethod
    async def redo_last_move(self, game_id: str) -> MoveResponse:
        """Redo the last undone move."""
        pass


class GameApplicationService(IGameApplicationService):
    """Application service that orchestrates game operations."""
    
    def __init__(
        self,
        game_repository: IGameRepository,
        make_move_use_case: MakeMoveUseCase,
        get_legal_moves_use_case: GetLegalMovesUseCase,
        undo_move_use_case: UndoMoveUseCase,
        redo_move_use_case: RedoMoveUseCase,
        move_validator: IApplicationMoveValidator,
        game_validator: IGameStateValidator,
    ):
        self.game_repository = game_repository
        self.make_move_use_case = make_move_use_case
        self.get_legal_moves_use_case = get_legal_moves_use_case
        self.undo_move_use_case = undo_move_use_case
        self.redo_move_use_case = redo_move_use_case
        self.move_validator = move_validator
        self.game_validator = game_validator
        self.logger = logging.getLogger(__name__)
    
    async def make_move(self, request: MoveRequest) -> MoveResponse:
        """Make a move in the game."""
        try:
            # Get game
            game = await self._get_game(request.game_id)
            
            # Validate request
            if not self.move_validator.validate_move_request(request, game):
                errors = self.move_validator.get_validation_errors(request, game)
                return MoveResponse.error_response(
                    error="\n".join(errors),
                    message="Move validation failed"
                )
            
            # Execute move using use case
            result = await self.make_move_use_case.execute(game, request)
            
            return MoveResponse.from_move_data(
                move_data=result,
                message="Move executed successfully"
            )
            
        except Exception as e:
            self.logger.error(f"Error making move: {e}")
            return MoveResponse.error_response(
                error=str(e),
                message="Failed to execute move"
            )
    
    async def get_legal_moves(self, request: LegalMovesRequest) -> LegalMovesResponse:
        """Get legal moves for the current game state."""
        try:
            # Get game
            game = await self._get_game(request.game_id)
            
            # Validate request
            if not self.game_validator.validate_legal_moves_request(request, game):
                errors = self.game_validator.get_validation_errors(request, game)
                return LegalMovesResponse.error_response(
                    error="\n".join(errors),
                    message="Request validation failed"
                )
            
            # Get legal moves using use case
            legal_moves = await self.get_legal_moves_use_case.execute(game, request.square)
            
            return LegalMovesResponse.from_legal_moves(
                legal_moves=legal_moves,
                square=request.square,
                message="Legal moves retrieved successfully"
            )
            
        except Exception as e:
            self.logger.error(f"Error getting legal moves: {e}")
            return LegalMovesResponse.error_response(
                error=str(e),
                message="Failed to get legal moves"
            )
    
    async def get_game_state(self, request: GameStateRequest) -> GameStateResponse:
        """Get current game state."""
        try:
            # Get game
            game = await self._get_game(request.game_id)
            
            # Validate request
            if not self.game_validator.validate_game_state_request(request, game):
                errors = self.game_validator.get_validation_errors(request, game)
                return GameStateResponse.error_response(
                    error="\n".join(errors),
                    message="Request validation failed"
                )
            
            # Build game state response
            game_state = {
                "game_id": game.game_id,
                "current_player": game.current_player,
                "game_state": game.game_state,
                "move_count": len(game.move_history.moves),
                "board_state": game.board.to_dict(),
                "is_ended": game.is_ended,
            }
            
            return GameStateResponse.from_game_state(
                game_state=game_state,
                message="Game state retrieved successfully"
            )
            
        except Exception as e:
            self.logger.error(f"Error getting game state: {e}")
            return GameStateResponse.error_response(
                error=str(e),
                message="Failed to get game state"
            )
    
    async def undo_last_move(self, game_id: str) -> MoveResponse:
        """Undo the last move."""
        try:
            # Get game
            game = await self._get_game(game_id)
            
            # Execute undo using use case
            result = await self.undo_move_use_case.execute(game)
            
            return MoveResponse.from_move_data(
                move_data=result,
                message="Move undone successfully"
            )
            
        except Exception as e:
            self.logger.error(f"Error undoing move: {e}")
            return MoveResponse.error_response(
                error=str(e),
                message="Failed to undo move"
            )
    
    async def redo_last_move(self, game_id: str) -> MoveResponse:
        """Redo the last undone move."""
        try:
            # Get game
            game = await self._get_game(game_id)
            
            # Execute redo using use case
            result = await self.redo_move_use_case.execute(game)
            
            return MoveResponse.from_move_data(
                move_data=result,
                message="Move redone successfully"
            )
            
        except Exception as e:
            self.logger.error(f"Error redoing move: {e}")
            return MoveResponse.error_response(
                error=str(e),
                message="Failed to redo move"
            )
    
    async def _get_game(self, game_id: str) -> Game:
        """Get game by ID."""
        game = await self.game_repository.get_by_id(game_id)
        if not game:
            raise GameNotFoundException(f"Game with ID {game_id} not found")
        return game 