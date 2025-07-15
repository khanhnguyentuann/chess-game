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
    
    def make_move(self, to_square: int, promotion: Optional[int] = None) -> bool:
        """
        Attempt to make a move from selected square to target square.
        
        Args:
            to_square: Target square index
            promotion: Piece type for pawn promotion (chess.QUEEN, chess.ROOK, etc.)
            
        Returns:
            True if move was successful
        """
        if self.selected_square is None:
            return False
            
        # Create move with optional promotion
        if promotion:
            move = chess.Move(self.selected_square, to_square, promotion)
        else:
            move = chess.Move(self.selected_square, to_square)
            
        # Check if this is a pawn promotion move that needs promotion piece
        if move.from_square is not None:
            piece = self.board.piece_at(move.from_square)
            if (piece and piece.piece_type == chess.PAWN and 
                ((piece.color == chess.WHITE and chess.square_rank(to_square) == 7) or
                 (piece.color == chess.BLACK and chess.square_rank(to_square) == 0))):
                if promotion is None:
                    # Default to queen promotion if not specified
                    move = chess.Move(self.selected_square, to_square, chess.QUEEN)
        
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
    
    def can_castle_kingside(self) -> bool:
        """
        Check if current player can castle kingside.
        
        Returns:
            True if kingside castling is legal
        """
        return self.board.has_kingside_castling_rights(self.board.turn)
    
    def can_castle_queenside(self) -> bool:
        """
        Check if current player can castle queenside.
        
        Returns:
            True if queenside castling is legal
        """
        return self.board.has_queenside_castling_rights(self.board.turn)
    
    def get_en_passant_square(self) -> Optional[int]:
        """
        Get the en passant target square if available.
        
        Returns:
            Square index where en passant capture is possible, or None
        """
        return self.board.ep_square
    
    def is_pawn_promotion_move(self, from_square: int, to_square: int) -> bool:
        """
        Check if a move would result in pawn promotion.
        
        Args:
            from_square: Source square
            to_square: Target square
            
        Returns:
            True if move is a pawn promotion
        """
        piece = self.board.piece_at(from_square)
        if not piece or piece.piece_type != chess.PAWN:
            return False
            
        return ((piece.color == chess.WHITE and chess.square_rank(to_square) == 7) or
                (piece.color == chess.BLACK and chess.square_rank(to_square) == 0))
    
    def get_legal_moves_for_square(self, square: int) -> List[chess.Move]:
        """
        Get all legal moves for a piece at the given square.
        
        Args:
            square: Square index
            
        Returns:
            List of legal moves from that square
        """
        return [move for move in self.board.legal_moves if move.from_square == square]
    
    def make_move_from_notation(self, move_notation: str) -> bool:
        """
        Make a move using algebraic notation (e.g., 'e4', 'Nf3', 'O-O').
        
        Args:
            move_notation: Move in algebraic notation
            
        Returns:
            True if move was successful
        """
        try:
            move = self.board.parse_san(move_notation)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.clear_selection()
                return True
        except ValueError:
            pass
        return False
    
    def get_board_fen(self) -> str:
        """
        Get the current board position in FEN notation.
        
        Returns:
            FEN string representing current position
        """
        return self.board.fen()
    
    def set_board_from_fen(self, fen: str) -> bool:
        """
        Set board position from FEN notation.
        
        Args:
            fen: FEN string
            
        Returns:
            True if FEN was valid and board was set
        """
        try:
            self.board = chess.Board(fen)
            self.clear_selection()
            return True
        except ValueError:
            return False
