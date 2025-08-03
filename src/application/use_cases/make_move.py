"""
Make Move Use Case
Handles the business logic for making a move in chess game.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import chess

from ...domain.entities.game import Game
from ...domain.events.event_dispatcher import get_event_dispatcher
from ...domain.events.game_events import EventType, GameEvent, MoveEvent
from ...domain.interfaces.repositories import IGameRepository, IMoveHistoryRepository
from ...domain.interfaces.services import IMoveValidationService, INotificationService
from ...shared.exceptions.game_exceptions import (
    GameEndedException,
    InvalidMoveException,
)
from ...shared.types.enums import GameState
from ..contracts.move_contracts import MoveRequest
from ..commands.base_command import CommandExecutor, CommandResult
from ..commands.move_command import MakeMoveCommand


class MakeMoveUseCase:
    """
    Use case for making a move in the chess game.
    Orchestrates move validation, execution, persistence, and notifications.
    """

    def __init__(
        self,
        move_validator: IMoveValidationService,
        game_repository: IGameRepository,
        move_history_repository: IMoveHistoryRepository,
        notification_service: INotificationService,
        command_executor: CommandExecutor,
        move_analyzer=None,
    ):
        self.move_validator = move_validator
        self.move_analyzer = move_analyzer
        self.game_repository = game_repository
        self.move_history_repository = move_history_repository
        self.notification_service = notification_service
        self.command_executor = command_executor
        self.event_dispatcher = get_event_dispatcher()
        self.logger = logging.getLogger(__name__)

    async def execute(
        self, game: Game, move_request: MoveRequest, save_game: bool = True
    ) -> Dict[str, Any]:
        """
        Execute a move in the chess game.

        Args:
            game: Current game instance
            move_request: Move to execute
            save_game: Whether to persist the game state

        Returns:
            Dictionary with move result and game status

        Raises:
            InvalidMoveException: If move is invalid
            GameEndedException: If game has already ended
        """
        try:
            # Check if game has ended
            if game.is_ended:
                raise GameEndedException("Cannot make move: game has ended")

            self.logger.info(f"Attempting move: {move_request}")

            # Create and execute move command
            move_command = MakeMoveCommand(
                game=game, move_request=move_request, validator=self.move_validator
            )

            # Execute command with undo/redo support
            result = await self.command_executor.execute(move_command)

            if not result.success:
                # Notify about invalid move
                await self.notification_service.notify_error(
                    result.message,
                    {"move_request": move_request.__dict__, "game_id": game.game_id},
                )
                raise InvalidMoveException(result.message)

            # Move executed successfully
            self.logger.info(f"Move executed successfully: {result.message}")

            # Create move event
            move_event = MoveEvent(
                event_type=EventType.MOVE_MADE,
                timestamp=datetime.now(),
                data={
                    "move": result.data["move"],
                    "game_id": game.game_id,
                    "player": game.current_player.value,
                    "move_number": len(game.move_history.moves),
                },
            )

            # Publish event
            await self.event_dispatcher.publish(move_event)

            # Save game state if requested
            if save_game:
                await self._save_game_state(game)

            # Notify about successful move
            await self.notification_service.notify_success(
                f"Move executed: {result.data['move']['san']}",
                {
                    "move": result.data["move"],
                    "game_id": game.game_id,
                    "game_state": game.game_state.value,
                },
            )

            # Return move result
            return {
                "success": True,
                "move": result.data["move"],
                "game_state": game.game_state.value,
                "current_player": game.current_player.value,
                "move_number": len(game.move_history.moves),
                "is_check": game.board.is_check(),
                "is_checkmate": game.board.is_checkmate(),
                "is_stalemate": game.board.is_stalemate(),
                "is_draw": game.board.is_draw(),
            }

        except Exception as e:
            self.logger.error(f"Error executing move: {e}")
            await self.notification_service.notify_error(
                f"Move execution failed: {str(e)}",
                {"move_request": move_request.__dict__, "game_id": game.game_id},
            )
            raise

    async def _save_game_state(self, game: Game) -> None:
        """Save game state to repository."""
        try:
            await self.game_repository.save(game)
            await self.move_history_repository.save(game.move_history)
            self.logger.info(f"Game state saved for game {game.game_id}")
        except Exception as e:
            self.logger.error(f"Error saving game state: {e}")
            # Don't raise here - move was successful, just couldn't save
