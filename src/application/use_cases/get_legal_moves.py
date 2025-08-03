"""
Get Legal Moves Use Case
Handles the business logic for retrieving legal moves in chess game.
"""

import logging
from typing import Any, Dict, List, Optional

import chess

from ...domain.entities.game import Game
from ...domain.interfaces.services import IMoveValidationService


class GetLegalMovesUseCase:
    """
    Use case for getting legal moves in the chess game.
    Provides legal moves for the current position.
    """

    def __init__(self, move_validator: IMoveValidationService):
        self.move_validator = move_validator
        self.logger = logging.getLogger(__name__)

    async def execute(
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
                moves = self.move_validator.get_legal_moves(game.board, square)
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

                move_list.append(move_dict)

            self.logger.info(f"Retrieved {len(move_list)} legal moves")
            return move_list

        except Exception as e:
            self.logger.error(f"Error getting legal moves: {e}")
            return [] 