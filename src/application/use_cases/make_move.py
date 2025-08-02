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
from ...shared.types.type_definitions import MoveRequest
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
    ):  # Add analyzer for move safety analysis
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
                    "captured_piece": result.data.get("captured_piece"),
                    "game_status": result.data["game_status"],
                },
                game_id=game.game_id,
                game_state=GameState.PLAYING,
                move_data=result.data["move"],
                player=game.get_previous_player(),  # Player who made the move
                captured_piece=result.data.get("captured_piece"),
                is_check=game.board.is_in_check(),
                is_checkmate=game.is_ended and "checkmate" in game.end_reason.lower(),
                game_status=result.data["game_status"],
            )

            # Dispatch move event
            await self.event_dispatcher.dispatch(move_event)

            # Notify about the move
            await self.notification_service.notify_move_made(game, result.data["move"])

            # Check for special conditions
            if game.board.is_in_check():
                await self.notification_service.notify_check(game, game.current_player)

            if game.is_ended:
                await self.notification_service.notify_game_over(
                    game, game.get_result()
                )

            # Save game state if requested
            if save_game:
                await self._save_game_state(game)

            return {
                "success": True,
                "message": result.message,
                "move_data": result.data["move"],
                "game_status": result.data["game_status"],
                "can_undo": self.command_executor.can_undo(),
                "can_redo": self.command_executor.can_redo(),
                "captured_piece": result.data.get("captured_piece"),
                "is_check": game.board.is_in_check(),
                "is_game_over": game.is_ended,
                "winner": game.winner.value if game.winner else None,
                "end_reason": game.end_reason if game.is_ended else None,
            }

        except (InvalidMoveException, GameEndedException) as e:
            self.logger.warning(f"Move failed: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in make move: {str(e)}", exc_info=True)
            await self.notification_service.notify_error(
                f"Unexpected error: {str(e)}",
                {"move_request": move_request.__dict__, "game_id": game.game_id},
            )
            raise

    async def undo_last_move(self, game: Game) -> Dict[str, Any]:
        """
        Undo the last move in the game.

        Args:
            game: Current game instance

        Returns:
            Dictionary with undo result
        """
        try:
            if not self.command_executor.can_undo():
                return {"success": False, "message": "No move to undo"}

            result = await self.command_executor.undo()

            if result and result.success:
                self.logger.info(f"Move undone: {result.message}")

                # Create undo event
                undo_event = GameEvent(
                    event_type=EventType.MOVE_UNDONE,
                    game_id=game.game_id,
                    data={
                        "undone_move": result.data.get("undone_move"),
                        "game_status": result.data.get("game_status"),
                    },
                )

                await self.event_dispatcher.dispatch(undo_event)

                # Save updated game state
                await self._save_game_state(game)

                return {
                    "success": True,
                    "message": result.message,
                    "game_status": result.data.get("game_status"),
                    "can_undo": self.command_executor.can_undo(),
                    "can_redo": self.command_executor.can_redo(),
                }
            else:
                return {
                    "success": False,
                    "message": result.message if result else "Undo failed",
                }

        except Exception as e:
            self.logger.error(f"Error undoing move: {str(e)}", exc_info=True)
            return {"success": False, "message": f"Undo failed: {str(e)}"}

    async def redo_last_move(self, game: Game) -> Dict[str, Any]:
        """
        Redo the last undone move.

        Args:
            game: Current game instance

        Returns:
            Dictionary with redo result
        """
        try:
            if not self.command_executor.can_redo():
                return {"success": False, "message": "No move to redo"}

            result = await self.command_executor.redo()

            if result and result.success:
                self.logger.info(f"Move redone: {result.message}")

                # Create redo event
                redo_event = GameEvent(
                    event_type=EventType.MOVE_REDONE,
                    game_id=game.game_id,
                    data=result.data,
                )

                await self.event_dispatcher.dispatch(redo_event)

                # Save updated game state
                await self._save_game_state(game)

                return {
                    "success": True,
                    "message": result.message,
                    "game_status": result.data,
                    "can_undo": self.command_executor.can_undo(),
                    "can_redo": self.command_executor.can_redo(),
                }
            else:
                return {
                    "success": False,
                    "message": result.message if result else "Redo failed",
                }

        except Exception as e:
            self.logger.error(f"Error redoing move: {str(e)}", exc_info=True)
            return {"success": False, "message": f"Redo failed: {str(e)}"}

    async def get_legal_moves(
        self, game: Game, square: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get legal moves for the current position.

        Args:
            game: Current game instance
            square: Optional square to get moves from (if None, gets all legal moves)

        Returns:
            List of legal moves with metadata
        """
        try:
            if square is not None:
                moves = self.move_validator.get_legal_moves_for_square(
                    game.board, square
                )
            else:
                moves = self.move_validator.get_all_legal_moves(game.board)

            # Convert moves to dictionaries with additional metadata
            move_list = []
            for move in moves:
                move_dict = {
                    "from_square": move.from_square,
                    "to_square": move.to_square,
                    "from_square_name": chess.square_name(move.from_square),
                    "to_square_name": chess.square_name(move.to_square),
                    "promotion": move.promotion,
                    "is_capture": self.move_validator.is_move_capture(game.board, move),
                    "is_castling": self.move_validator.is_move_castling(move),
                    "is_en_passant": self.move_validator.is_move_en_passant(
                        game.board, move
                    ),
                    "notation": self.move_validator.get_move_notation(game.board, move),
                }

                # Add safety analysis
                if self.move_analyzer:
                    safety_analysis = self.move_analyzer.analyze_move_safety(
                        game.board, move
                    )
                    move_dict.update(safety_analysis)

                move_list.append(move_dict)

            return move_list

        except Exception as e:
            self.logger.error(f"Error getting legal moves: {str(e)}", exc_info=True)
            return []

    async def _save_game_state(self, game: Game) -> None:
        """Save current game state to repository."""
        try:
            await self.game_repository.save_game(game)
            await self.move_history_repository.save_move_history(
                game.game_id, game.get_move_history()
            )
        except Exception as e:
            self.logger.error(f"Failed to save game state: {str(e)}", exc_info=True)
