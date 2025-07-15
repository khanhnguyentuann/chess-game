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
        # Use algebraic notation for more reliable moves
        moves = ["e4", "e5", "Bc4", "Nc6", "Qh5", "a6", "Qxf7#"]
        
        for move in moves:
            if self.chess_board.is_game_over():
                break
            success = self.chess_board.make_move_from_notation(move)
            assert success, f"Failed to make move: {move}"
        
        # Should be checkmate
        assert self.chess_board.is_game_over()
        result = self.chess_board.get_game_result()
        assert "Checkmate" in result
        assert "White wins" in result
    
    def test_castling_kingside(self):
        """Test kingside castling (O-O)."""
        # Set up position for white kingside castling
        moves = ["e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5"]
        
        for move in moves:
            self.chess_board.make_move_from_notation(move)
        
        # White should be able to castle kingside
        assert self.chess_board.can_castle_kingside()
        
        # Perform castling
        success = self.chess_board.make_move_from_notation("O-O")
        assert success
        
        # Verify king and rook positions after castling
        assert self.chess_board.get_piece_at(6).piece_type == chess.KING  # King on g1
        assert self.chess_board.get_piece_at(5).piece_type == chess.ROOK  # Rook on f1
        assert self.chess_board.get_piece_at(4) is None  # Original king square empty
        assert self.chess_board.get_piece_at(7) is None  # Original rook square empty
    
    def test_castling_queenside(self):
        """Test queenside castling (O-O-O)."""
        # Set up position for black queenside castling
        moves = ["e4", "d5", "Nf3", "Nc6", "Bc4", "Bg4", "d3", "Qd7", "Be3", "O-O-O"]
        
        for move in moves[:-1]:  # All moves except the last castling
            self.chess_board.make_move_from_notation(move)
        
        # Black should be able to castle queenside
        assert self.chess_board.can_castle_queenside()
        
        # Perform queenside castling
        success = self.chess_board.make_move_from_notation("O-O-O")
        assert success
        
        # Verify king and rook positions after castling
        assert self.chess_board.get_piece_at(58).piece_type == chess.KING  # King on c8
        assert self.chess_board.get_piece_at(59).piece_type == chess.ROOK  # Rook on d8
    
    def test_en_passant_capture(self):
        """Test en passant pawn capture."""
        # Set up en passant scenario
        moves = ["e4", "a6", "e5", "d5"]  # White pawn on e5, black pawn moves d7-d5
        
        for move in moves:
            self.chess_board.make_move_from_notation(move)
        
        # There should be an en passant square available
        en_passant_square = self.chess_board.get_en_passant_square()
        assert en_passant_square is not None
        assert en_passant_square == chess.D6  # d6 square
        
        # Perform en passant capture
        success = self.chess_board.make_move_from_notation("exd6")
        assert success
        
        # Verify the captured pawn is removed
        assert self.chess_board.get_piece_at(chess.D5) is None  # Captured pawn gone
        assert self.chess_board.get_piece_at(chess.D6).piece_type == chess.PAWN  # Capturing pawn moved
    
    def test_pawn_promotion_to_queen(self):
        """Test pawn promotion to queen."""
        # Set up a position where white pawn can promote
        fen = "8/P7/8/8/8/8/8/K6k w - - 0 1"  # White pawn on a7, ready to promote
        self.chess_board.set_board_from_fen(fen)
        
        # Check if promotion move is detected
        assert self.chess_board.is_pawn_promotion_move(chess.A7, chess.A8)
        
        # Promote pawn to queen
        self.chess_board.select_square(chess.A7)
        success = self.chess_board.make_move(chess.A8, chess.QUEEN)
        assert success
        
        # Verify promotion
        promoted_piece = self.chess_board.get_piece_at(chess.A8)
        assert promoted_piece.piece_type == chess.QUEEN
        assert promoted_piece.color == chess.WHITE
    
    def test_pawn_promotion_to_rook(self):
        """Test pawn promotion to rook."""
        # Set up a position where black pawn can promote
        fen = "k6K/8/8/8/8/8/p7/8 b - - 0 1"  # Black pawn on a2, ready to promote
        self.chess_board.set_board_from_fen(fen)
        
        # Promote pawn to rook
        self.chess_board.select_square(chess.A2)
        success = self.chess_board.make_move(chess.A1, chess.ROOK)
        assert success
        
        # Verify promotion
        promoted_piece = self.chess_board.get_piece_at(chess.A1)
        assert promoted_piece.piece_type == chess.ROOK
        assert promoted_piece.color == chess.BLACK
    
    def test_pawn_promotion_default_queen(self):
        """Test that pawn promotion defaults to queen when no piece specified."""
        # Set up a position where white pawn can promote
        fen = "8/P7/8/8/8/8/8/K6k w - - 0 1"
        self.chess_board.set_board_from_fen(fen)
        
        # Promote without specifying piece (should default to queen)
        self.chess_board.select_square(chess.A7)
        success = self.chess_board.make_move(chess.A8)  # No promotion piece specified
        assert success
        
        # Should default to queen
        promoted_piece = self.chess_board.get_piece_at(chess.A8)
        assert promoted_piece.piece_type == chess.QUEEN
    
    def test_castling_rights_lost_after_king_move(self):
        """Test that castling rights are lost after king moves."""
        # Set up for castling
        moves = ["e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5"]
        for move in moves:
            self.chess_board.make_move_from_notation(move)
        
        # Initially can castle
        assert self.chess_board.can_castle_kingside()
        
        # Move king - this should permanently lose castling rights
        self.chess_board.make_move_from_notation("Kf1")
        
        # Check that we're now on black's turn and white can't castle
        assert self.chess_board.get_current_player() == False  # Black's turn
        
        # Make a black move to get back to white's turn
        self.chess_board.make_move_from_notation("d6")
        
        # Now it's white's turn again, but should not be able to castle
        assert self.chess_board.get_current_player() == True  # White's turn
        assert not self.chess_board.can_castle_kingside()
    
    def test_castling_rights_lost_after_rook_move(self):
        """Test that castling rights are lost after rook moves."""
        # Set up for queenside castling - need to clear queenside first
        moves = ["d4", "d5", "Nc3", "Nc6", "Bf4", "Bf5", "Qd2", "Qd7", "Bd2", "Be6"]
        for move in moves:
            self.chess_board.make_move_from_notation(move)
        
        # Initially can castle queenside
        assert self.chess_board.can_castle_queenside()
        
        # Move queenside rook - this should lose castling rights
        self.chess_board.make_move_from_notation("Rb1")
        
        # Check that we're now on black's turn and white can't castle queenside
        assert self.chess_board.get_current_player() == False  # Black's turn
        
        # Make a black move to get back to white's turn
        self.chess_board.make_move_from_notation("Rd8")
        
        # Now it's white's turn again, but should not be able to castle queenside
        assert self.chess_board.get_current_player() == True  # White's turn
        assert not self.chess_board.can_castle_queenside()
    
    def test_fen_import_export(self):
        """Test FEN import and export functionality."""
        # Test standard starting position
        starting_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        
        # Export current position
        current_fen = self.chess_board.get_board_fen()
        assert current_fen == starting_fen
        
        # Test custom position
        custom_fen = "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4"
        success = self.chess_board.set_board_from_fen(custom_fen)
        assert success
        
        # Verify the position was set correctly
        exported_fen = self.chess_board.get_board_fen()
        assert exported_fen == custom_fen
    
    def test_algebraic_notation_moves(self):
        """Test making moves using algebraic notation."""
        # Test various move types
        moves = [
            "e4",      # Pawn move
            "e5",      # Pawn move
            "Nf3",     # Knight move
            "Nc6",     # Knight move
            "Bb5",     # Bishop move
            "a6",      # Pawn move
            "Ba4",     # Bishop move
            "Nf6",     # Knight move
            "O-O",     # Castling
            "Be7",     # Bishop move
            "Re1",     # Rook move
            "b5",      # Pawn move
            "Bb3",     # Bishop move
        ]
        
        for move in moves:
            success = self.chess_board.make_move_from_notation(move)
            assert success, f"Failed to make move: {move}"
    
    def test_stalemate_detection(self):
        """Test stalemate detection."""
        # Set up a classic stalemate position
        stalemate_fen = "k7/P7/K7/8/8/8/8/8 b - - 0 1"  # Black king in stalemate
        self.chess_board.set_board_from_fen(stalemate_fen)
        
        assert self.chess_board.is_game_over()
        result = self.chess_board.get_game_result()
        assert "Stalemate" in result


if __name__ == "__main__":
    pytest.main([__file__])
