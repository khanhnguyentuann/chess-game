"""
Game Rules Service
Domain service for chess game rules and state management.
"""

from typing import List, Optional

import chess

from ...shared.types.enums import GameState, Player
from ..entities.board import Board
from ..entities.game import Game
from ..exceptions.game_exceptions import GameAlreadyEndedException, InvalidGameStateException
from ..value_objects.move import Move
from ..value_objects.square import Square


class GameRulesService:
    """Service for managing chess game rules and state transitions."""
    
    def __init__(self):
        """Initialize game rules service."""
        pass
    
    def can_make_move(self, game: Game) -> bool:
        """Check if a move can be made in the current game state."""
        if game.is_ended:
            raise GameAlreadyEndedException()
        
        if game.state != GameState.PLAYING:
            raise InvalidGameStateException(f"Cannot make move in state: {game.state}")
        
        return True
    
    def is_game_over(self, board: Board) -> bool:
        """Check if the game is over based on current position."""
        return (
            board.is_checkmate() or
            board.is_stalemate() or
            board.is_insufficient_material() or
            board.is_seventyfive_moves() or
            board.is_fivefold_repetition()
        )
    
    def get_game_state(self, board: Board) -> GameState:
        """Determine the current game state based on board position."""
        if board.is_checkmate():
            return GameState.CHECKMATE
        elif board.is_stalemate():
            return GameState.STALEMATE
        elif board.is_insufficient_material():
            return GameState.INSUFFICIENT_MATERIAL
        elif board.is_seventyfive_moves():
            return GameState.SEVENTYFIVE_MOVES
        elif board.is_fivefold_repetition():
            return GameState.FIVEFOLD_REPETITION
        elif board.is_in_check():
            return GameState.CHECK
        else:
            return GameState.PLAYING
    
    def get_winner(self, board: Board, current_player: Player) -> Optional[Player]:
        """Determine the winner based on current position."""
        if board.is_checkmate():
            # The player who is checkmated loses, so the other player wins
            return Player.BLACK if current_player == Player.WHITE else Player.WHITE
        return None
    
    def get_end_reason(self, board: Board) -> str:
        """Get the reason why the game ended."""
        if board.is_checkmate():
            return "Checkmate"
        elif board.is_stalemate():
            return "Stalemate"
        elif board.is_insufficient_material():
            return "Insufficient material"
        elif board.is_seventyfive_moves():
            return "Seventy-five moves rule"
        elif board.is_fivefold_repetition():
            return "Fivefold repetition"
        else:
            return "Unknown"
    
    def validate_move_timing(self, game: Game) -> bool:
        """Validate if move can be made based on timing rules."""
        # Add time control validation here if needed
        return True
    
    def get_legal_moves_for_player(self, board: Board, player: Player) -> List[chess.Move]:
        """Get all legal moves for a specific player."""
        legal_moves = board.get_legal_moves()
        player_moves = []
        
        for move in legal_moves:
            piece = board.get_piece_at(move.from_square)
            if piece:
                piece_color = Player.WHITE if piece.color else Player.BLACK
                if piece_color == player:
                    player_moves.append(move)
        
        return player_moves
    
    def is_player_in_check(self, board: Board, player: Player) -> bool:
        """Check if a specific player is in check."""
        # Set board to player's turn temporarily
        original_turn = board.internal_board.turn
        board.internal_board.turn = player.chess_value
        
        is_check = board.is_in_check()
        
        # Restore original turn
        board.internal_board.turn = original_turn
        
        return is_check
    
    def get_available_castling_moves(self, board: Board, player: Player) -> List[chess.Move]:
        """Get available castling moves for a player."""
        legal_moves = self.get_legal_moves_for_player(board, player)
        castling_moves = []
        
        for move in legal_moves:
            if self._is_castling_move(move):
                castling_moves.append(move)
        
        return castling_moves
    
    def _is_castling_move(self, move: chess.Move) -> bool:
        """Check if a move is a castling move."""
        return (
            abs(move.to_square - move.from_square) == 2 and
            move.from_square in [4, 60]  # King starting squares
        ) 