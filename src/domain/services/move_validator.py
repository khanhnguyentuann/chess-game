"""
Move Validator Service
Domain service for validating chess moves according to business rules.
"""

from typing import List, Optional

import chess

from ...shared.types.enums import PieceType, Player
from ..entities.board import Board
from ..entities.game import Game
from ..exceptions.move_exceptions import (
    IllegalMoveException,
    InvalidSquareException,
    NoPieceAtSquareException,
    WrongPlayerException,
)
from ..value_objects.move import Move
from ..value_objects.square import Square


class MoveValidatorService:
    """
    Service for validating chess moves and providing move suggestions.
    Extracted from chess_board.py for better separation of concerns.
    """

    def validate_move(self, game: Game, move: Move) -> bool:
        """
        Validate a move against game rules.

        Args:
            game: Current game state
            move: Move to validate

        Returns:
            True if move is valid

        Raises:
            InvalidMoveException: If move is invalid with specific reason
        """
        board = game.board

        # Basic validation
        if not self._validate_square(move.from_square.index):
            raise InvalidSquareException(move.from_square.index)
        
        if not self._validate_square(move.to_square.index):
            raise InvalidSquareException(move.to_square.index)

        # Check if there's a piece at from_square
        piece = board.get_piece_at(move.from_square.index)
        if piece is None:
            raise NoPieceAtSquareException(move.from_square.index)

        # Check if piece belongs to current player
        piece_color = Player.WHITE if piece.color else Player.BLACK
        if piece_color != game.current_player:
            raise WrongPlayerException()

        # Create chess.Move object
        chess_move = move.to_chess_move()

        # Validate move is legal
        if not board.is_move_legal(chess_move):
            raise IllegalMoveException("Move is not legal in current position")

        # Special validation for pawn promotion
        if self._is_pawn_promotion_move(board, move):
            if move.promotion is None:
                raise IllegalMoveException("Pawn promotion requires promotion piece")
            if move.promotion not in [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT]:
                raise IllegalMoveException("Invalid promotion piece")

        return True

    def get_legal_moves_for_square(self, board: Board, square: Square) -> List[chess.Move]:
        """
        Get all legal moves for a piece at given square.

        Args:
            board: Board state
            square: Square to check

        Returns:
            List of legal moves from that square
        """
        if not self._validate_square(square.index):
            return []

        return board.get_legal_moves_from_square(square.index)

    def get_all_legal_moves(self, board: Board) -> List[chess.Move]:
        """Get all legal moves in current position."""
        return board.get_legal_moves()

    def is_square_attackable(
        self, board: Board, square: Square, by_player: Player
    ) -> bool:
        """
        Check if a square is attackable by a player.

        Args:
            board: Board state
            square: Target square
            by_player: Attacking player

        Returns:
            True if square can be attacked by player
        """
        if not self._validate_square(square.index):
            return False

        # Get all legal moves for the player
        all_moves = board.get_legal_moves()
        player_moves = [
            move
            for move in all_moves
            if self._move_belongs_to_player(board, move, by_player)
        ]

        # Check if any move attacks the target square
        return any(move.to_square == square.index for move in player_moves)

    def is_square_defended(self, board: Board, square: Square) -> bool:
        """
        Check if a square is defended by the piece's own side.

        Args:
            board: Board state
            square: Square to check

        Returns:
            True if square is defended
        """
        piece = board.get_piece_at(square.index)
        if piece is None:
            return False

        piece_player = Player.WHITE if piece.color else Player.BLACK
        return self.is_square_attackable(board, square, piece_player)

    def get_attacking_pieces(self, board: Board, square: Square) -> List[int]:
        """
        Get all pieces attacking a square.

        Args:
            board: Board state
            square: Target square

        Returns:
            List of square indices of attacking pieces
        """
        attackers = []
        all_moves = board.get_legal_moves()

        for move in all_moves:
            if move.to_square == square.index:
                attackers.append(move.from_square)

        return attackers

    def is_move_capture(self, board: Board, move: chess.Move) -> bool:
        """Check if a move is a capture."""
        return board.get_piece_at(move.to_square) is not None

    def is_move_castling(self, move: chess.Move) -> bool:
        """Check if a move is castling."""
        return abs(move.to_square - move.from_square) == 2 and move.from_square in [
            4,
            60,
        ]  # King starting squares

    def is_move_en_passant(self, board: Board, move: chess.Move) -> bool:
        """Check if a move is en passant capture."""
        piece = board.get_piece_at(move.from_square)
        if piece is None or piece.piece_type != chess.PAWN:
            return False

        return move.to_square == board.get_en_passant_square()

    def get_move_notation(self, board: Board, move: chess.Move) -> str:
        """
        Get algebraic notation for a move.

        Args:
            board: Board state
            move: Move to notate

        Returns:
            Move in algebraic notation
        """
        try:
            # Use python-chess to generate proper algebraic notation
            temp_board = board.internal_board.copy()
            return temp_board.san(move)
        except ValueError:
            # Fallback to basic notation
            return f"{chess.square_name(move.from_square)}{chess.square_name(move.to_square)}"

    def validate_selection(self, game: Game, square: int) -> bool:
        """
        Validate if a square can be selected by current player.

        Args:
            game: Current game
            square: Square to select

        Returns:
            True if selection is valid
        """
        if not self._validate_square(square):
            return False

        return game.is_valid_selection(square)

    def get_move_threats(self, board: Board, move: chess.Move) -> List[int]:
        """
        Get squares that would be threatened after making a move.

        Args:
            board: Current board state
            move: Move to analyze

        Returns:
            List of threatened square indices
        """
        # Create a copy and make the move
        temp_board = board.copy()
        if not temp_board.execute_move(move):
            return []

        # Get all legal moves in new position
        new_moves = temp_board.get_legal_moves()
        threatened_squares = [move.to_square for move in new_moves]

        return list(set(threatened_squares))  # Remove duplicates

    def _validate_square(self, square: int) -> bool:
        """Validate square index."""
        return 0 <= square <= 63

    def _validate_squares(self, from_square: int, to_square: int) -> bool:
        """Validate both squares."""
        return self._validate_square(from_square) and self._validate_square(to_square)

    def _is_pawn_promotion_move(self, board: Board, move: Move) -> bool:
        """Check if move is pawn promotion."""
        piece = board.get_piece_at(move.from_square.index)
        if piece is None or piece.piece_type != chess.PAWN:
            return False

        to_rank = move.to_square.rank
        return (piece.color and to_rank == 7) or (not piece.color and to_rank == 0)

    def _move_belongs_to_player(
        self, board: Board, move: chess.Move, player: Player
    ) -> bool:
        """Check if a move belongs to a specific player."""
        piece = board.get_piece_at(move.from_square)
        if piece is None:
            return False

        piece_player = Player.WHITE if piece.color else Player.BLACK
        return piece_player == player


class MoveAnalyzer:
    """
    Advanced move analysis service.
    Provides deeper analysis of moves and positions.
    """

    def __init__(self, validator: MoveValidatorService):
        self.validator = validator

    def analyze_move_safety(self, board: Board, move: chess.Move) -> dict:
        """
        Analyze the safety of a move.

        Returns:
            Dictionary with safety analysis
        """
        analysis = {
            "is_safe": True,
            "creates_threats": [],
            "exposes_pieces": [],
            "tactical_motifs": [],
        }

        # Check if move exposes king
        temp_board = board.copy()
        temp_board.execute_move(move)

        current_player = Player.WHITE if board.internal_board.turn else Player.BLACK
        if temp_board.is_in_check():
            analysis["is_safe"] = False
            analysis["exposes_pieces"].append("king")

        # Add more analysis as needed
        return analysis

    def find_tactical_moves(self, board: Board) -> List[chess.Move]:
        """Find tactical moves (captures, checks, threats)."""
        tactical_moves = []
        legal_moves = board.get_legal_moves()

        for move in legal_moves:
            # Check for captures
            if self.validator.is_move_capture(board, move):
                tactical_moves.append(move)

            # Check for checks
            temp_board = board.copy()
            temp_board.execute_move(move)
            if temp_board.is_in_check():
                tactical_moves.append(move)

        return tactical_moves

    def analyze_move_safety(self, board: Board, move: chess.Move) -> dict:
        """
        Analyze the safety of a move.

        Returns:
            Dictionary with safety analysis
        """
        analysis = {
            "is_safe": True,
            "creates_threats": [],
            "exposes_pieces": [],
            "tactical_motifs": [],
        }

        # Check if move exposes king
        temp_board = board.copy()
        temp_board.execute_move(move)

        if temp_board.is_in_check():
            analysis["is_safe"] = False
            analysis["exposes_pieces"].append("king")

        # Add more analysis as needed
        return analysis
