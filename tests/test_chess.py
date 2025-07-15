"""
Test cases for the Chess Game Model
Tests the chess board logic, move validation, and game state management.
"""

import pytest
import chess
from models.chess_board import ChessBoard


class TestChessBoard:
    """Test cases for the ChessBoard model class."""
    
    def setup_method(self):
        """Set up a fresh chess board for each test."""
        self.chess_board = ChessBoard()
    
    def test_initial_board_state(self):
        """Test that the board is initialized correctly."""
        assert not self.chess_board.is_game_over()
        assert self.chess_board.get_current_player() == True  # White starts
        assert self.chess_board.selected_square is None
        assert len(self.chess_board.valid_moves) == 0
        assert not self.chess_board.is_in_check()
    
    def test_piece_placement(self):
        """Test that pieces are placed correctly on initial board."""
        # Test white pieces
        assert self.chess_board.get_piece_at(0).piece_type == chess.ROOK
        assert self.chess_board.get_piece_at(0).color == chess.WHITE
        assert self.chess_board.get_piece_at(4).piece_type == chess.KING
        assert self.chess_board.get_piece_at(4).color == chess.WHITE
        
        # Test black pieces
        assert self.chess_board.get_piece_at(56).piece_type == chess.ROOK
        assert self.chess_board.get_piece_at(56).color == chess.BLACK
        assert self.chess_board.get_piece_at(60).piece_type == chess.KING
        assert self.chess_board.get_piece_at(60).color == chess.BLACK
        
        # Test empty squares
        assert self.chess_board.get_piece_at(24) is None  # Middle of board
        assert self.chess_board.get_piece_at(32) is None
    
    def test_valid_selection(self):
        """Test piece selection validation."""
        # White's turn - should be able to select white pieces
        assert self.chess_board.is_valid_selection(8)   # White pawn
        assert self.chess_board.is_valid_selection(0)   # White rook
        assert not self.chess_board.is_valid_selection(48)  # Black pawn
        assert not self.chess_board.is_valid_selection(24)  # Empty square
    
    def test_square_selection(self):
        """Test square selection and valid move calculation."""
        # Select a white pawn
        success = self.chess_board.select_square(8)  # a2 pawn
        assert success
        assert self.chess_board.selected_square == 8
        assert len(self.chess_board.valid_moves) > 0
        
        # Try to select an invalid square (black piece on white's turn)
        success = self.chess_board.select_square(48)
        assert not success
    
    def test_pawn_moves(self):
        """Test pawn movement logic."""
        # Select pawn and check valid moves
        self.chess_board.select_square(8)  # a2 pawn
        
        # Pawn should have 1 or 2 moves (forward one or two squares)
        move_destinations = [move.to_square for move in self.chess_board.valid_moves]
        assert 16 in move_destinations  # One square forward
        assert 24 in move_destinations  # Two squares forward (initial pawn move)
    
    def test_make_valid_move(self):
        """Test making a valid move."""
        # Select pawn and make a move
        self.chess_board.select_square(8)  # a2 pawn
        success = self.chess_board.make_move(16)  # Move to a3
        
        assert success
        assert self.chess_board.selected_square is None  # Selection cleared
        assert len(self.chess_board.valid_moves) == 0
        assert self.chess_board.get_current_player() == False  # Turn changed to black
        
        # Verify piece moved
        assert self.chess_board.get_piece_at(8) is None  # Original square empty
        assert self.chess_board.get_piece_at(16) is not None  # New square has piece
        assert self.chess_board.get_piece_at(16).piece_type == chess.PAWN
    
    def test_make_invalid_move(self):
        """Test making an invalid move."""
        # Select pawn
        self.chess_board.select_square(8)  # a2 pawn
        
        # Try to move to invalid square
        success = self.chess_board.make_move(32)  # Invalid move
        assert not success
        assert self.chess_board.get_current_player() == True  # Turn unchanged
    
    def test_clear_selection(self):
        """Test clearing selection."""
        self.chess_board.select_square(8)
        assert self.chess_board.selected_square is not None
        
        self.chess_board.clear_selection()
        assert self.chess_board.selected_square is None
        assert len(self.chess_board.valid_moves) == 0
    
    
    def test_undo_move(self):
        """Test undoing moves."""
        # Make a move
        self.chess_board.select_square(8)
        self.chess_board.make_move(16)
        
        # Verify move was made
        assert self.chess_board.get_current_player() == False
        
        # Undo the move
        success = self.chess_board.undo_last_move()
        assert success
        assert self.chess_board.get_current_player() == True
        
        # Verify board state restored
        assert self.chess_board.get_piece_at(8) is not None  # Pawn back
        assert self.chess_board.get_piece_at(16) is None     # Target square empty
    
    def test_undo_no_moves(self):
        """Test undoing when no moves have been made."""
        success = self.chess_board.undo_last_move()
        assert not success
    
    def test_reset_board(self):
        """Test board reset functionality."""
        # Make some moves
        self.chess_board.select_square(8)
        self.chess_board.make_move(16)
        
        # Reset board
        self.chess_board.reset_board()
        
        # Verify reset state
        assert not self.chess_board.is_game_over()
        assert self.chess_board.get_current_player() == True
        assert self.chess_board.selected_square is None
        assert len(self.chess_board.valid_moves) == 0
    
    def test_scholar_mate_checkmate(self):
        """Test a simple checkmate scenario (Scholar's Mate)."""
        # Perform Scholar's Mate sequence
        moves = [
            (12, 28),  # e2-e4
            (52, 36),  # e7-e5
            (5, 26),   # f1-c4
            (57, 42),  # b8-c6
            (3, 39),   # d1-h5
            (49, 33),  # a7-a6
            (39, 61),  # h5xf7# (checkmate)
        ]
        
        for from_sq, to_sq in moves:
            if self.chess_board.is_game_over():
                break
            self.chess_board.select_square(from_sq)
            self.chess_board.make_move(to_sq)
        
        # Should be checkmate
        assert self.chess_board.is_game_over()
        result = self.chess_board.get_game_result()
        assert "Checkmate" in result
        assert "White wins" in result


if __name__ == "__main__":
    pytest.main([__file__])
