"""
Chess Board Model - Handles chess logic, board state, rules, and moves.
This module encapsulates all chess-related business logic using the python-chess library.
"""

import chess
from typing import List, Optional


class ChessBoard:
    """
    Model class that handles all chess game logic including:
    - Board state management
    - Move validation
    - Game status checking
    - Turn management
    """
    
    def __init__(self):
        """Initialize a new chess board in starting position."""
        self.board = chess.Board()
        self.selected_square: Optional[int] = None
        self.valid_moves: List[chess.Move] = []
    
    def get_piece_at(self, square: int) -> Optional[chess.Piece]:
        """
        Get the piece at a specific square.
        
        Args:
            square: Square index (0-63)
            
        Returns:
            Chess piece at the square or None if empty
        """
        return self.board.piece_at(square)
    
    def is_valid_selection(self, square: int) -> bool:
        """
        Check if a square can be selected (contains a piece of current player).
        
        Args:
            square: Square index to check
            
        Returns:
            True if square contains a piece of the current player
        """
        piece = self.board.piece_at(square)
        return piece is not None and piece.color == self.board.turn
    
    def select_square(self, square: int) -> bool:
        """
        Select a square and calculate valid moves.
        
        Args:
            square: Square index to select
            
        Returns:
            True if selection was successful
        """
        if self.is_valid_selection(square):
            self.selected_square = square
            self.valid_moves = [
                move for move in self.board.legal_moves 
                if move.from_square == square
            ]
            return True
        return False
    
    def make_move(self, to_square: int) -> bool:
        """
        Attempt to make a move from selected square to target square.
        
        Args:
            to_square: Target square index
            
        Returns:
            True if move was successful
        """
        if self.selected_square is None:
            return False
            
        move = chess.Move(self.selected_square, to_square)
        if move in self.valid_moves:
            self.board.push(move)
            self.clear_selection()
            return True
        return False
    
    def clear_selection(self) -> None:
        """Clear current selection and valid moves."""
        self.selected_square = None
        self.valid_moves = []
    
    def get_current_player(self) -> bool:
        """
        Get current player's turn.
        
        Returns:
            True for white, False for black
        """
        return self.board.turn
    
    def is_game_over(self) -> bool:
        """
        Check if the game is over.
        
        Returns:
            True if game is finished
        """
        return self.board.is_game_over()
    
    def get_game_result(self) -> Optional[str]:
        """
        Get the game result if game is over.
        
        Returns:
            String describing the game result or None if game is ongoing
        """
        if not self.is_game_over():
            return None
            
        if self.board.is_checkmate():
            winner = "Black" if self.board.turn else "White"
            return f"Checkmate! {winner} wins!"
        elif self.board.is_stalemate():
            return "Stalemate! It's a draw!"
        elif self.board.is_insufficient_material():
            return "Draw due to insufficient material!"
        elif self.board.is_seventyfive_moves():
            return "Draw due to 75-move rule!"
        elif self.board.is_fivefold_repetition():
            return "Draw due to fivefold repetition!"
        else:
            return "Game over!"
    
    def is_in_check(self) -> bool:
        """
        Check if current player is in check.
        
        Returns:
            True if current player is in check
        """
        return self.board.is_check()
    
    
    def undo_last_move(self) -> bool:
        """
        Undo the last move if possible.
        
        Returns:
            True if undo was successful
        """
        try:
            self.board.pop()
            self.clear_selection()
            return True
        except IndexError:
            return False
    
    def reset_board(self) -> None:
        """Reset the board to starting position."""
        self.board = chess.Board()
        self.clear_selection()
