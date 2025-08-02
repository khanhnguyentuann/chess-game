"""
Chess Move Commands
Implements command pattern for chess moves with undo/redo support.
"""

from typing import Any, Dict, Optional

import chess

from ...domain.entities.board import Board
from ...domain.entities.game import Game
from ...domain.interfaces.services import IMoveValidationService
from ...shared.types.enums import Player
from ...shared.types.type_definitions import MoveRequest
from .base_command import CommandResult, ICommand


class MakeMoveCommand(ICommand):
    """Command for making a chess move."""

    def __init__(
        self, game: Game, move_request: MoveRequest, validator: IMoveValidationService
    ):
        super().__init__()
        self.game = game
        self.move_request = move_request
        self.validator = validator
        self.previous_board_state: Optional[str] = None
        self.captured_piece: Optional[chess.Piece] = None
        self.move_executed: Optional[chess.Move] = None

    async def execute(self) -> CommandResult:
        try:
            # Validate the move
            if not self.validator.validate_move_request(self.game, self.move_request):
                return CommandResult(success=False, message="Invalid move request")

            # Store current board state for undo
            self.previous_board_state = self.game.board.to_fen()

            # Check for capture
            self.captured_piece = self.game.board.get_piece_at(
                self.move_request.to_square
            )

            # Create chess move object
            move = chess.Move(
                self.move_request.from_square,
                self.move_request.to_square,
                self.move_request.promotion,
            )

            # Get move notation BEFORE executing
            move_notation = self._get_move_notation(move)

            # Execute the move
            success = self.game.board.execute_move(move)

            if success:
                self.move_executed = move

                # Update game state (using pre-calculated notation)
                self.game.switch_player()
                self._add_move_to_history_with_notation(move, move_notation)

                # Check for game end conditions
                await self._check_game_end_conditions()

                return CommandResult(
                    success=True,
                    message=f"Move executed: {move_notation}",
                    data={
                        "move": self._move_to_dict(move),
                        "captured_piece": str(self.captured_piece)
                        if self.captured_piece
                        else None,
                        "game_status": self.game.get_status(),
                    },
                )
            else:
                return CommandResult(
                    success=False, message="Failed to execute move on board"
                )

        except Exception as e:
            return CommandResult(
                success=False, message=f"Move execution failed: {str(e)}", error=e
            )

    async def undo(self) -> CommandResult:
        """Undo the move command."""
        try:
            if not self.previous_board_state or not self.move_executed:
                return CommandResult(
                    success=False, message="Cannot undo: no previous state stored"
                )

            # Restore board state
            self.game.board.load_from_fen(self.previous_board_state)

            # Switch player back
            self.game.switch_player()

            # Remove move from history
            self.game.remove_last_move_from_history()

            return CommandResult(
                success=True,
                message=f"Move undone: {self._get_move_notation(self.move_executed)}",
                data={
                    "undone_move": self._move_to_dict(self.move_executed),
                    "game_status": self.game.get_status(),
                },
            )

        except Exception as e:
            return CommandResult(
                success=False, message=f"Move undo failed: {str(e)}", error=e
            )

    def can_undo(self) -> bool:
        """Check if move can be undone."""
        return (
            self.previous_board_state is not None
            and self.move_executed is not None
            and self.status.value == "completed"
        )

    def get_description(self) -> str:
        """Get move description."""
        if self.move_executed:
            return f"Move: {self._get_move_notation(self.move_executed)}"
        return (
            f"Move: {chess.square_name(self.move_request.from_square)}"
            + f"-{chess.square_name(self.move_request.to_square)}"
        )

    def _get_move_notation(self, move: chess.Move) -> str:
        """Get algebraic notation for move."""
        try:
            return self.game.board.internal_board.san(move)
        except:
            return f"{chess.square_name(move.from_square)}{chess.square_name(move.to_square)}"

    def _add_move_to_history_with_notation(
        self, move: chess.Move, notation: str
    ) -> None:
        """Add move to history with pre-calculated notation."""
        # Just use the game's built-in method which is simpler
        self.game.add_move_to_history(move)

    def _move_to_dict(self, move: chess.Move) -> Dict[str, Any]:
        """Convert move to dictionary."""
        return {
            "from_square": move.from_square,
            "to_square": move.to_square,
            "promotion": move.promotion,
            "from_square_name": chess.square_name(move.from_square),
            "to_square_name": chess.square_name(move.to_square),
            "notation": self._get_move_notation(move),
        }

    async def _check_game_end_conditions(self) -> None:
        """Check if game has ended after move."""
        if self.game.board.is_checkmate():
            winner = (
                Player.BLACK
                if self.game.current_player == Player.WHITE
                else Player.WHITE
            )
            self.game.end_game(winner, "Checkmate")
        elif self.game.board.is_stalemate():
            self.game.end_game(None, "Stalemate")
        elif self.game.board.is_insufficient_material():
            self.game.end_game(None, "Insufficient material")
        elif self.game.board.is_seventyfive_moves():
            self.game.end_game(None, "75-move rule")
        elif self.game.board.is_fivefold_repetition():
            self.game.end_game(None, "Fivefold repetition")


class CastlingCommand(ICommand):
    """Command for castling moves."""

    def __init__(
        self,
        game: Game,
        castling_side: str,  # 'kingside' or 'queenside'
        validator: IMoveValidationService,
    ):
        super().__init__()
        self.game = game
        self.castling_side = castling_side
        self.validator = validator
        self.previous_board_state: Optional[str] = None
        self.king_move: Optional[chess.Move] = None
        self.rook_move: Optional[chess.Move] = None

    async def execute(self) -> CommandResult:
        """Execute castling command."""
        try:
            # Store board state
            self.previous_board_state = self.game.board.to_fen()

            # Determine king and rook squares
            current_player = self.game.current_player
            if current_player == Player.WHITE:
                king_from = chess.E1
                if self.castling_side == "kingside":
                    king_to = chess.G1
                    rook_from = chess.H1
                    rook_to = chess.F1
                else:  # queenside
                    king_to = chess.C1
                    rook_from = chess.A1
                    rook_to = chess.D1
            else:  # BLACK
                king_from = chess.E8
                if self.castling_side == "kingside":
                    king_to = chess.G8
                    rook_from = chess.H8
                    rook_to = chess.F8
                else:  # queenside
                    king_to = chess.C8
                    rook_from = chess.A8
                    rook_to = chess.D8

            # Create move objects
            self.king_move = chess.Move(king_from, king_to)

            # Validate castling is legal
            if not self.game.board.is_move_legal(self.king_move):
                return CommandResult(
                    success=False, message=f"Castling {self.castling_side} is not legal"
                )

            # Execute the castling move (python-chess handles rook automatically)
            success = self.game.board.execute_move(self.king_move)

            if success:
                # Update game state
                self.game.switch_player()
                self.game.add_move_to_history(self.king_move)

                return CommandResult(
                    success=True,
                    message=f"Castled {self.castling_side}",
                    data={
                        "castling_side": self.castling_side,
                        "king_move": self._move_to_dict(self.king_move),
                        "game_status": self.game.get_status(),
                    },
                )
            else:
                return CommandResult(
                    success=False, message="Failed to execute castling"
                )

        except Exception as e:
            return CommandResult(
                success=False, message=f"Castling failed: {str(e)}", error=e
            )

    async def undo(self) -> CommandResult:
        """Undo castling command."""
        try:
            if not self.previous_board_state:
                return CommandResult(
                    success=False, message="Cannot undo castling: no previous state"
                )

            # Restore board state
            self.game.board.load_from_fen(self.previous_board_state)

            # Switch player back
            self.game.switch_player()

            # Remove move from history
            self.game.remove_last_move_from_history()

            return CommandResult(
                success=True,
                message=f"Castling {self.castling_side} undone",
                data={"game_status": self.game.get_status()},
            )

        except Exception as e:
            return CommandResult(
                success=False, message=f"Castling undo failed: {str(e)}", error=e
            )

    def can_undo(self) -> bool:
        """Check if castling can be undone."""
        return (
            self.previous_board_state is not None and self.status.value == "completed"
        )

    def get_description(self) -> str:
        """Get castling description."""
        return f"Castle {self.castling_side}"

    def _move_to_dict(self, move: chess.Move) -> Dict[str, Any]:
        """Convert move to dictionary."""
        return {
            "from_square": move.from_square,
            "to_square": move.to_square,
            "from_square_name": chess.square_name(move.from_square),
            "to_square_name": chess.square_name(move.to_square),
        }


class ResignCommand(ICommand):
    """Command for resigning the game."""

    def __init__(self, game: Game, resigning_player: Player):
        super().__init__()
        self.game = game
        self.resigning_player = resigning_player
        self.previous_game_state: Optional[Dict[str, Any]] = None

    async def execute(self) -> CommandResult:
        """Execute resign command."""
        try:
            # Store game state
            self.previous_game_state = {
                "is_ended": self.game.is_ended,
                "winner": self.game.winner,
                "end_reason": self.game.end_reason,
            }

            # End game with opponent as winner
            winner = (
                Player.BLACK if self.resigning_player == Player.WHITE else Player.WHITE
            )
            self.game.end_game(winner, f"{self.resigning_player.value} resigned")

            return CommandResult(
                success=True,
                message=f"{self.resigning_player.value} resigned. {winner.value} wins!",
                data={
                    "resigning_player": self.resigning_player.value,
                    "winner": winner.value,
                    "game_status": self.game.get_status(),
                },
            )

        except Exception as e:
            return CommandResult(
                success=False, message=f"Resignation failed: {str(e)}", error=e
            )

    async def undo(self) -> CommandResult:
        """Undo resignation (restore game state)."""
        try:
            if not self.previous_game_state:
                return CommandResult(
                    success=False, message="Cannot undo resignation: no previous state"
                )

            # Restore game state
            self.game.is_ended = self.previous_game_state["is_ended"]
            self.game.winner = self.previous_game_state["winner"]
            self.game.end_reason = self.previous_game_state["end_reason"]

            return CommandResult(
                success=True,
                message="Resignation undone, game continues",
                data={"game_status": self.game.get_status()},
            )

        except Exception as e:
            return CommandResult(
                success=False, message=f"Resignation undo failed: {str(e)}", error=e
            )

    def can_undo(self) -> bool:
        """Check if resignation can be undone."""
        return self.previous_game_state is not None and self.status.value == "completed"

    def get_description(self) -> str:
        """Get resignation description."""
        return f"{self.resigning_player.value} resigns"
