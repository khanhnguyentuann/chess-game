"""
Board Entity - Pure board state representation
MIGRATED FROM: models/chess_board.py (board state logic only)
"""

import chess
from typing import Optional, List
from ..events.game_events import BoardEvent, EventType
from ...shared.types.enums import Player, PieceType
from ...shared.types.type_definitions import EventPublisher


class Board:
    """
    Pure board entity representing chess board state.
    Contains only board state and basic operations.
    Business logic moved to services.
    """
    
    def __init__(self, event_publisher: Optional[EventPublisher] = None):
        """Initialize board in starting position."""
        self._board = chess.Board()
        self._event_publisher = event_publisher
        self._move_history: List[chess.Move] = []
    
    @property
    def internal_board(self) -> chess.Board:
        """Get internal python-chess board (read-only access)."""
        return self._board
    
    @property
    def fen(self) -> str:
        """Get current position in FEN notation."""
        return self._board.fen()
    
    @property
    def current_player(self) -> Player:
        """Get current player to move."""
        return Player.WHITE if self._board.turn else Player.BLACK
    
    @property
    def move_history(self) -> List[chess.Move]:
        """Get copy of move history."""
        return self._move_history.copy()
    
    @property
    def last_move(self) -> Optional[chess.Move]:
        """Get the last move played."""
        return self._move_history[-1] if self._move_history else None
    
    def get_piece_at(self, square: int) -> Optional[chess.Piece]:
        """
        Get piece at square.
        
        Args:
            square: Square index (0-63)
            
        Returns:
            Piece at square or None if empty
        """
        if not self._is_valid_square(square):
            return None
        return self._board.piece_at(square)
    
    def get_piece_color(self, square: int) -> Optional[Player]:
        """
        Get color of piece at square.
        
        Args:
            square: Square index
            
        Returns:
            Player color or None if no piece
        """
        piece = self.get_piece_at(square)
        if piece is None:
            return None
        return Player.WHITE if piece.color else Player.BLACK
    
    def get_piece_type(self, square: int) -> Optional[PieceType]:
        """
        Get type of piece at square.
        
        Args:
            square: Square index
            
        Returns:
            PieceType or None if no piece
        """
        piece = self.get_piece_at(square)
        if piece is None:
            return None
        return PieceType(piece.piece_type)
    
    def is_square_empty(self, square: int) -> bool:
        """Check if square is empty."""
        return self.get_piece_at(square) is None
    
    def is_square_occupied_by_player(self, square: int, player: Player) -> bool:
        """Check if square is occupied by specific player."""
        piece_color = self.get_piece_color(square)
        return piece_color == player
    
    def execute_move(self, move: chess.Move) -> bool:
        """
        Execute a move on the board.
        Does not validate - assumes move is legal.
        
        Args:
            move: Chess move to execute
            
        Returns:
            True if move was executed successfully
        """
        if move not in self._board.legal_moves:
            return False
        
        # Store move in history
        self._move_history.append(move)
        
        # Execute move
        self._board.push(move)
        
        # Publish event
        if self._event_publisher:
            self._event_publisher.publish(
                EventType.MOVE_MADE.value,
                {
                    'move': move,
                    'fen': self.fen,
                    'current_player': self.current_player
                }
            )
        
        return True
    
    def undo_last_move(self) -> bool:
        """
        Undo the last move.
        
        Returns:
            True if undo was successful
        """
        if not self._move_history:
            return False
        
        try:
            # Remove from history
            undone_move = self._move_history.pop()
            
            # Undo on board
            self._board.pop()
            
            # Publish event
            if self._event_publisher:
                self._event_publisher.publish(
                    EventType.MOVE_UNDONE.value,
                    {
                        'undone_move': undone_move,
                        'fen': self.fen,
                        'current_player': self.current_player
                    }
                )
            
            return True
        except IndexError:
            return False
    
    def reset_to_starting_position(self, first_player: Optional[Player] = None) -> None:
        """Reset board to starting position."""
        if first_player == Player.BLACK:
            # Use FEN with black to move
            starting_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 1"
            self._board = chess.Board(starting_fen)
        else:
            # Default starting position (white to move)
            self._board = chess.Board()
        
        self._move_history.clear()
        
        if self._event_publisher:
            self._event_publisher.publish(
                EventType.BOARD_RESET.value,
                {
                    'fen': self.fen,
                    'current_player': self.current_player
                }
            )
    
    def set_position_from_fen(self, fen: str) -> bool:
        """
        Set board position from FEN.
        
        Args:
            fen: FEN string
            
        Returns:
            True if FEN was valid
        """
        try:
            new_board = chess.Board(fen)
            self._board = new_board
            self._move_history.clear()  # Clear history when setting new position
            
            if self._event_publisher:
                self._event_publisher.publish(
                    EventType.POSITION_SET.value,
                    {
                        'fen': self.fen,
                        'current_player': self.current_player
                    }
                )
            
            return True
        except ValueError:
            return False
    
    def get_legal_moves(self) -> List[chess.Move]:
        """Get all legal moves in current position."""
        return list(self._board.legal_moves)
    
    def get_legal_moves_from_square(self, square: int) -> List[chess.Move]:
        """Get legal moves from specific square."""
        if not self._is_valid_square(square):
            return []
        
        return [
            move for move in self._board.legal_moves 
            if move.from_square == square
        ]
    
    def is_move_legal(self, move: chess.Move) -> bool:
        """Check if a move is legal in current position."""
        return move in self._board.legal_moves
    
    def is_in_check(self) -> bool:
        """Check if current player is in check."""
        return self._board.is_check()
    
    def is_checkmate(self) -> bool:
        """Check if current position is checkmate."""
        return self._board.is_checkmate()
    
    def is_stalemate(self) -> bool:
        """Check if current position is stalemate."""
        return self._board.is_stalemate()
    
    def is_insufficient_material(self) -> bool:
        """Check if position has insufficient material for checkmate."""
        return self._board.is_insufficient_material()
    
    def is_seventyfive_moves(self) -> bool:
        """Check if 75-move rule applies."""
        return self._board.is_seventyfive_moves()
    
    def is_fivefold_repetition(self) -> bool:
        """Check if position has been repeated 5 times."""
        return self._board.is_fivefold_repetition()
    
    def is_game_over(self) -> bool:
        """Check if game is over by any condition."""
        return self._board.is_game_over()
    
    def has_castling_rights(self, player: Player, kingside: bool = True) -> bool:
        color = player.chess_value
        if kingside:
            return self._board.has_kingside_castling_rights(color)
        else:
            return self._board.has_queenside_castling_rights(color)
    
    def get_en_passant_square(self) -> Optional[int]:
        """Get en passant target square if available."""
        return self._board.ep_square
    
    def copy(self) -> 'Board':
        """Create a copy of the board."""
        new_board = Board(self._event_publisher)
        new_board._board = self._board.copy()
        new_board._move_history = self._move_history.copy()
        return new_board
    
    def _is_valid_square(self, square: int) -> bool:
        """Check if square index is valid."""
        return 0 <= square <= 63
    
    def __eq__(self, other) -> bool:
        """Check board equality."""
        if not isinstance(other, Board):
            return False
        return self.fen == other.fen
    
    def __str__(self) -> str:
        """String representation of board."""
        return str(self._board)
    
    def __repr__(self) -> str:
        """Debug representation."""
        return f"Board(fen='{self.fen}')"
    
    def to_fen(self) -> str:
        # Call the python‑chess Board.fen() method to get the FEN string.
        return self._board.fen()
    
    def load_from_fen(self, fen: str) -> bool:
        """Load board position from FEN string."""
        try:
            self._board.set_fen(fen)
            return True
        except ValueError:
            return False
    
    def is_in_check(self) -> bool:
        """Check if current player is in check."""
        return self._board.is_check()
    
    def is_checkmate(self) -> bool:
        """Check if current position is checkmate."""
        return self._board.is_checkmate()
    
    def is_stalemate(self) -> bool:
        """Check if current position is stalemate."""
        return self._board.is_stalemate()
    
    def is_insufficient_material(self) -> bool:
        """Check if position has insufficient material for checkmate."""
        return self._board.is_insufficient_material()
    
    def is_seventyfive_moves(self) -> bool:
        """Check if 75-move rule applies."""
        return self._board.is_seventyfive_moves()
    
    def is_fivefold_repetition(self) -> bool:
        """Check if position has been repeated 5 times."""
        return self._board.is_fivefold_repetition()