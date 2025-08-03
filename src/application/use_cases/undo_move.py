"""
Undo Move Use Case
Handles the business logic for undoing moves in chess game.
"""

import logging
from typing import Any, Dict, Optional

from ...domain.entities.game import Game
from ...domain.events.event_dispatcher import get_event_dispatcher
from ...domain.events.game_events import EventType, GameEvent
from ...domain.interfaces.repositories import IGameRepository, IMoveHistoryRepository
from ...domain.interfaces.services import INotificationService
from ..commands.base_command import CommandExecutor


class UndoMoveUseCase:
    """
    Use case for undoing moves in the chess game.
    Handles undo operations with event publishing and notifications.
    """

    def __init__(
        self,
        command_executor: CommandExecutor,
        game_repository: IGameRepository,
        move_history_repository: IMoveHistoryRepository,
        notification_service: INotificationService,
    ):
        self.command_executor = command_executor
        self.game_repository = game_repository
        self.move_history_repository = move_history_repository
        self.notification_service = notification_service
        self.event_dispatcher = get_event_dispatcher()
        self.logger = logging.getLogger(__name__)

    async def execute(self, game: Game) -> Dict[str, Any]:
        """
        Undo the last move in the game.

        Args:
            game: Current game instance

        Returns:
            Dictionary with undo result
        """
        try:
            if not self.command_executor.can_undo():
                return {
                    "success": False,
                    "message": "No move to undo",
                    "can_undo": False,
                    "can_redo": self.command_executor.can_redo(),
                }

            result = await self.command_executor.undo()

            if result and result.success:
                self.logger.info(f"Move undone: {result.message}")

                # Create undo event
                undo_event = GameEvent(
                    event_type=EventType.MOVE_UNDONE,
                    timestamp=result.timestamp,
                    data={
                        "undone_move": result.data.get("undone_move"),
                        "game_id": game.game_id,
                        "move_number": len(game.move_history.moves),
                    },
                )

                await self.event_dispatcher.publish(undo_event)

                # Save updated game state
                await self._save_game_state(game)

                # Notify about successful undo
                await self.notification_service.notify_success(
                    f"Move undone: {result.message}",
                    {
                        "game_id": game.game_id,
                        "game_state": game.game_state.value,
                        "can_undo": self.command_executor.can_undo(),
                        "can_redo": self.command_executor.can_redo(),
                    },
                )

                return {
                    "success": True,
                    "message": result.message,
                    "undone_move": result.data.get("undone_move"),
                    "game_state": game.game_state.value,
                    "current_player": game.current_player.value,
                    "move_number": len(game.move_history.moves),
                    "can_undo": self.command_executor.can_undo(),
                    "can_redo": self.command_executor.can_redo(),
                }
            else:
                return {
                    "success": False,
                    "message": result.message if result else "Undo failed",
                    "can_undo": self.command_executor.can_undo(),
                    "can_redo": self.command_executor.can_redo(),
                }

        except Exception as e:
            self.logger.error(f"Error undoing move: {e}")
            await self.notification_service.notify_error(
                f"Undo failed: {str(e)}",
                {"game_id": game.game_id},
            )
            return {
                "success": False,
                "message": f"Undo failed: {str(e)}",
                "can_undo": self.command_executor.can_undo(),
                "can_redo": self.command_executor.can_redo(),
            }

    async def _save_game_state(self, game: Game) -> None:
        """Save game state to repository."""
        try:
            await self.game_repository.save(game)
            await self.move_history_repository.save(game.move_history)
            self.logger.info(f"Game state saved after undo for game {game.game_id}")
        except Exception as e:
            self.logger.error(f"Error saving game state after undo: {e}")
            # Don't raise here - undo was successful, just couldn't save 