"""
Simple test runner for the Chess Game Model
Runs basic tests without requiring pytest.
"""

import sys
import traceback
from models.chess_board import ChessBoard
import chess


def run_test(test_name, test_func):
    """Run a single test and report results."""
    try:
        test_func()
        print(f"✓ {test_name}")
        return True
    except Exception as e:
        print(f"✗ {test_name}: {str(e)}")
        traceback.print_exc()
        return False


def test_initial_board_state():
    """Test that the board is initialized correctly."""
    chess_board = ChessBoard()
    assert not chess_board.is_game_over()
    assert chess_board.get_current_player() == True  # White starts
    assert chess_board.selected_square is None
    assert len(chess_board.valid_moves) == 0
    assert not chess_board.is_in_check()


def test_piece_placement():
    """Test that pieces are placed correctly on initial board."""
    chess_board = ChessBoard()
    
    # Test white pieces
    assert chess_board.get_piece_at(0).piece_type == chess.ROOK
    assert chess_board.get_piece_at(0).color == chess.WHITE
    assert chess_board.get_piece_at(4).piece_type == chess.KING
    assert chess_board.get_piece_at(4).color == chess.WHITE
    
    # Test black pieces
    assert chess_board.get_piece_at(56).piece_type == chess.ROOK
    assert chess_board.get_piece_at(56).color == chess.BLACK
    assert chess_board.get_piece_at(60).piece_type == chess.KING
    assert chess_board.get_piece_at(60).color == chess.BLACK
    
    # Test empty squares
    assert chess_board.get_piece_at(24) is None  # Middle of board
    assert chess_board.get_piece_at(32) is None


def test_valid_selection():
    """Test piece selection validation."""
    chess_board = ChessBoard()
    
    # White's turn - should be able to select white pieces
    assert chess_board.is_valid_selection(8)   # White pawn
    assert chess_board.is_valid_selection(0)   # White rook
    assert not chess_board.is_valid_selection(48)  # Black pawn
    assert not chess_board.is_valid_selection(24)  # Empty square


def test_square_selection():
    """Test square selection and valid move calculation."""
    chess_board = ChessBoard()
    
    # Select a white pawn
    success = chess_board.select_square(8)  # a2 pawn
    assert success
    assert chess_board.selected_square == 8
    assert len(chess_board.valid_moves) > 0
    
    # Try to select an invalid square (black piece on white's turn)
    success = chess_board.select_square(48)
    assert not success


def test_make_valid_move():
    """Test making a valid move."""
    chess_board = ChessBoard()
    
    # Select pawn and make a move
    chess_board.select_square(8)  # a2 pawn
    success = chess_board.make_move(16)  # Move to a3
    
    assert success
    assert chess_board.selected_square is None  # Selection cleared
    assert len(chess_board.valid_moves) == 0
    assert chess_board.get_current_player() == False  # Turn changed to black
    
    # Verify piece moved
    assert chess_board.get_piece_at(8) is None  # Original square empty
    assert chess_board.get_piece_at(16) is not None  # New square has piece
    assert chess_board.get_piece_at(16).piece_type == chess.PAWN


def test_undo_move():
    """Test undoing moves."""
    chess_board = ChessBoard()
    
    # Make a move
    chess_board.select_square(8)  # a2 pawn
    chess_board.make_move(16)     # Move to a3
    
    # Verify move was made
    assert chess_board.get_current_player() == False  # Turn changed to black
    
    # Undo the move
    success = chess_board.undo_last_move()
    assert success
    assert chess_board.get_current_player() == True  # Turn back to white
    
    # Verify board state restored
    assert chess_board.get_piece_at(8) is not None   # Pawn back
    assert chess_board.get_piece_at(16) is None      # Target square empty


def main():
    """Run all tests."""
    print("Running Chess Game Model Tests...")
    print("=" * 50)
    
    tests = [
        ("Initial Board State", test_initial_board_state),
        ("Piece Placement", test_piece_placement),
        ("Valid Selection", test_valid_selection),
        ("Square Selection", test_square_selection),
        ("Make Valid Move", test_make_valid_move),
        ("Undo Move", test_undo_move),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if run_test(test_name, test_func):
            passed += 1
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
