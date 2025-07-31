"""
Game Entity - Game state and orchestration
MIGRATED FROM: models/chess_board.py (game state management logic)
"""

import uuid
import random
from datetime import datetime
from typing import Optional, List, Dict, Any
import chess

from .board import Board
from .move_history import MoveHistory
from ..events.game_events import GameEvent, EventType
from ...shared.types.enums import GameState, Player, GameResult
from ...shared.types.type_definitions import EventPublisher, GameStateResponse


class Game:
    """
    Game entity that orchestrates game state and rules.
    Contains game-level logic while delegating board operations to Board entity.
    """
    
    def __init__(self, 
                 white_player: str = "White",
                 black_player: str = "Black",
                 game_id: Optional[str] = None,
                 board: Optional[Board] = None,
                 event_publisher: Optional[EventPublisher] = None,
                 random_first_player: bool = True):
        """Initialize a new chess game."""
        self.game_id = game_id or str(uuid.uuid4())
        self.id = self.game_id  # Backward compatibility
        self.white_player = white_player
        self.black_player = black_player
        
        # Randomly choose first player if requested
        if random_first_player:
            self._current_player = random.choice([Player.WHITE, Player.BLACK])
        else:
            self._current_player = Player.WHITE
        self.is_ended = False
        self.winner: Optional[Player] = None
        self.end_reason: Optional[str] = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        self._board = board or Board(event_publisher)
        
        # If we created a new board and want a random first player,
        # we need to reset it with the chosen player
        if board is None and random_first_player:
            self._board.reset_to_starting_position(self._current_player)
        
        self._state = GameState.PLAYING
        self._selected_square: Optional[int] = None
        self._valid_moves_from_selected: List[chess.Move] = []
        self._event_publisher = event_publisher
        
        # Game statistics
        self._move_count = 0
        self._white_time_remaining: Optional[float] = None
        self._black_time_remaining: Optional[float] = None

        try:
            self._board.internal_board.turn = self._current_player.chess_value
        except Exception:
            pass

        # Move history
        self.move_history = MoveHistory(game_id=self.game_id)
    
    @property
    def board(self) -> Board:
        """Get the game board."""
        return self._board
    
    @property
    def state(self) -> GameState:
        """Get current game state."""
        return self._state
    
    @property
    def current_player(self) -> Player:
        """Get current player to move."""
        return self._current_player
    
    @current_player.setter
    def current_player(self, player: Player) -> None:
        if player != self._current_player:
            self._current_player = player
            try:
                # True for white, False for black
                self._board.internal_board.turn = player.chess_value
            except Exception:
                pass
            self.updated_at = datetime.now()
    
    @property
    def selected_square(self) -> Optional[int]:
        """Get currently selected square."""
        return self._selected_square
    
    @property
    def valid_moves_from_selected(self) -> List[chess.Move]:
        """Get valid moves from selected square."""
        return self._valid_moves_from_selected.copy()
    
    @property
    def move_count(self) -> int:
        """Get total number of moves played."""
        return self._move_count
    
    @property
    def is_game_over(self) -> bool:
        """Check if game is over."""
        return self._state in [
            GameState.CHECKMATE, 
            GameState.STALEMATE, 
            GameState.DRAW
        ] or self._board.is_game_over()
    
    def select_square(self, square: int) -> bool:
        """
        Select a square for move input.
        
        Args:
            square: Square index to select
            
        Returns:
            True if selection was successful
        """
        if self._state != GameState.PLAYING:
            return False
        
        # Check if square has a piece of current player
        if not self._board.is_square_occupied_by_player(square, self.current_player):
            return False
        
        # Update selection
        self._selected_square = square
        self._valid_moves_from_selected = self._board.get_legal_moves_from_square(square)
        self._update_timestamp()
        
        # Publish selection event
        if self._event_publisher:
            self._event_publisher.publish(
                EventType.SQUARE_SELECTED.value,
                {
                    'game_id': self.id,
                    'square': square,
                    'valid_moves': self._valid_moves_from_selected
                }
            )
        
        return True
    
    def clear_selection(self) -> None:
        """Clear current square selection."""
        self._selected_square = None
        self._valid_moves_from_selected.clear()
        
        if self._event_publisher:
            self._event_publisher.publish(
                EventType.SELECTION_CLEARED.value,
                {'game_id': self.id}
            )
    
    def make_move(self, to_square: int, promotion: Optional[int] = None) -> bool:
        """
        Attempt to make a move from selected square to target square.
        
        Args:
            to_square: Target square index
            promotion: Promotion piece type if applicable
            
        Returns:
            True if move was successful
        """
        if self._state != GameState.PLAYING or self._selected_square is None:
            return False
        
        # Create move
        move = chess.Move(self._selected_square, to_square, promotion)
        
        # Check if move is in valid moves
        if move not in self._valid_moves_from_selected:
            return False
        
        # Execute move on board
        if not self._board.execute_move(move):
            return False
        
        # Update game state
        self._move_count += 1
        self._update_timestamp()
        self.clear_selection()
        
        # Switch to the other player
        self.switch_player()
        
        # Check for game end conditions
        self._update_game_state()
        
        # Publish move event
        if self._event_publisher:
            self._event_publisher.publish(
                EventType.MOVE_MADE.value,
                {
                    'game_id': self.id,
                    'move': move,
                    'move_count': self._move_count,
                    'new_state': self._state,
                    'current_player': self.current_player
                }
            )
        
        return True
    
    def make_move_from_squares(self, from_square: int, to_square: int, 
                              promotion: Optional[int] = None) -> bool:
        """
        Make a move directly from square coordinates.
        
        Args:
            from_square: Source square
            to_square: Target square  
            promotion: Promotion piece type
            
        Returns:
            True if move was successful
        """
        # First select the from_square
        if not self.select_square(from_square):
            return False
        
        # Then make the move
        return self.make_move(to_square, promotion)
    
    def undo_last_move(self) -> bool:
        if self._state != GameState.PLAYING or self._move_count == 0:
            return False
        
        if self._board.undo_last_move():
            self._move_count -= 1
            self._update_timestamp()
            self.clear_selection()
            self._current_player = Player.WHITE if self._board.internal_board.turn else Player.BLACK
            
            # Update game state (might change from checkmate back to playing)
            self._update_game_state()
            
            if self._event_publisher:
                self._event_publisher.publish(
                    EventType.MOVE_UNDONE.value,
                    {
                        'game_id': self.id,
                        'move_count': self._move_count,
                        'new_state': self._state
                    }
                )
            
            return True
        
        return False
    
    def reset_game(self, random_first_player: bool = True) -> None:
        """Reset game to initial state."""
        # Randomly choose first player if requested
        if random_first_player:
            self._current_player = random.choice([Player.WHITE, Player.BLACK])
        else:
            self._current_player = Player.WHITE
        
        # Reset board with the chosen first player
        self._board.reset_to_starting_position(self._current_player)
        
        self._state = GameState.PLAYING
        self._move_count = 0
        self._selected_square = None
        self._valid_moves_from_selected.clear()
        self._current_player = Player.WHITE if self._board.internal_board.turn else Player.BLACK
        self._update_timestamp()
        
        if self._event_publisher:
            self._event_publisher.publish(
                EventType.GAME_RESET.value,
                {'game_id': self.id}
            )
    
    def pause_game(self) -> bool:
        """Pause the game if it's currently playing."""
        if self._state == GameState.PLAYING:
            self._state = GameState.PAUSED
            self._update_timestamp()
            return True
        return False
    
    def resume_game(self) -> bool:
        """Resume the game if it's paused."""
        if self._state == GameState.PAUSED:
            self._state = GameState.PLAYING
            self._update_timestamp()
            return True
        return False
    
    def get_game_result(self) -> GameResult:
        """
        Get the current game result.
        
        Returns:
            GameResult enum value
        """
        if not self.is_game_over:
            return GameResult.ONGOING
        
        if self._board.is_checkmate():
            # Winner is opposite of current player (who is in checkmate)
            if self.current_player == Player.WHITE:
                return GameResult.BLACK_WINS
            else:
                return GameResult.WHITE_WINS
        elif self._board.is_stalemate():
            return GameResult.DRAW_STALEMATE
        elif self._board.is_insufficient_material():
            return GameResult.DRAW_INSUFFICIENT_MATERIAL
        elif self._board.is_seventyfive_moves():
            return GameResult.DRAW_FIFTY_MOVES
        elif self._board.is_fivefold_repetition():
            return GameResult.DRAW_REPETITION
        else:
            return GameResult.ONGOING
    
    def get_result_message(self) -> str:
        """Get human-readable game result message."""
        result = self.get_game_result()
        
        messages = {
            GameResult.WHITE_WINS: "Checkmate! White wins!",
            GameResult.BLACK_WINS: "Checkmate! Black wins!",
            GameResult.DRAW_STALEMATE: "Stalemate! It's a draw!",
            GameResult.DRAW_INSUFFICIENT_MATERIAL: "Draw due to insufficient material!",
            GameResult.DRAW_FIFTY_MOVES: "Draw due to 75-move rule!",
            GameResult.DRAW_REPETITION: "Draw due to fivefold repetition!",
            GameResult.ONGOING: "Game in progress"
        }
        
        return messages.get(result, "Unknown result")
    
    def is_valid_selection(self, square: int) -> bool:
        """
        Check if a square can be selected by current player.
        
        Args:
            square: Square index to check
            
        Returns:
            True if square contains a piece of current player
        """
        if self._state != GameState.PLAYING:
            return False
        
        return self._board.is_square_occupied_by_player(square, self.current_player)
    
    def get_state_response(self) -> GameStateResponse:
        """
        Get complete game state for queries.
        
        Returns:
            GameStateResponse with current game state
        """
        return GameStateResponse(
            state=self._state,
            current_player=self.current_player,
            board_fen=self._board.fen,
            selected_square=self._selected_square,
            valid_moves=self._valid_moves_from_selected,
            last_move=self._board.last_move,
            result=self.get_game_result() if self.is_game_over else None
        )
    
    def set_time_control(self, white_time: float, black_time: float) -> None:
        """
        Set time control for players.
        
        Args:
            white_time: Time in seconds for white
            black_time: Time in seconds for black
        """
        self._white_time_remaining = white_time
        self._black_time_remaining = black_time
    
    def get_time_remaining(self, player: Player) -> Optional[float]:
        """Get time remaining for player."""
        if player == Player.WHITE:
            return self._white_time_remaining
        else:
            return self._black_time_remaining
    
    def _update_game_state(self) -> None:
        """Update game state based on board position."""
        if self._board.is_checkmate():
            self._state = GameState.CHECKMATE
        elif (self._board.is_stalemate() or 
              self._board.is_insufficient_material() or
              self._board.is_seventyfive_moves() or
              self._board.is_fivefold_repetition()):
            self._state = GameState.DRAW
        elif self._board.is_game_over():
            self._state = GameState.GAME_OVER
        # Otherwise keep current state (PLAYING, PAUSED, etc.)
    
    def _update_timestamp(self) -> None:
        """Update the last modified timestamp."""
        self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert game to dictionary for serialization."""
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'fen': self._board.fen,
            'state': self._state.value,
            'move_count': self._move_count,
            'selected_square': self._selected_square,
            'white_time': self._white_time_remaining,
            'black_time': self._black_time_remaining
        }
    
    @classmethod
    def from_dict(cls, data: dict, event_publisher: Optional[EventPublisher] = None) -> 'Game':
        """Create game from dictionary."""
        game = cls(game_id=data['id'], event_publisher=event_publisher)
        game.created_at = datetime.fromisoformat(data['created_at'])
        game.updated_at = datetime.fromisoformat(data['updated_at'])
        game._board.set_position_from_fen(data['fen'])
        game._state = GameState(data['state'])
        game._move_count = data['move_count']
        game._selected_square = data.get('selected_square')
        game._white_time_remaining = data.get('white_time')
        game._black_time_remaining = data.get('black_time')
        game._current_player = Player.WHITE if game._board.internal_board.turn else Player.BLACK
        
        return game
    
    def __str__(self) -> str:
        """String representation of game."""
        return f"Game({self.id}, {self._state.value}, moves: {self._move_count})"
    
    def add_move_to_history(self, move: chess.Move) -> None:
        """Add a move to the game history."""
        # Use simple notation for now
        notation = str(move)
        fen_current = self._board.to_fen()
        
        # Get captured piece before making the move
        captured_piece = None
        if self._board.internal_board.piece_at(move.to_square):
            captured_piece = self._board.internal_board.piece_at(move.to_square).symbol()
        
        # Add move to history with simple implementation
        self.move_history.add_move(
            move=move,
            player=self._current_player,
            fen_before=fen_current,
            fen_after=fen_current,  # Will be updated after move is made
            captured_piece=captured_piece,
            is_check=False,  # Will be updated after move 
            is_checkmate=False,  # Will be updated after move
            annotation=notation
        )
        self._move_count += 1
    
    def remove_last_move_from_history(self) -> Optional[chess.Move]:
        """Remove the last move from history."""
        undone_move = self.move_history.undo_move()
        if undone_move:
            self._move_count -= 1
            return undone_move.move
        return None
    
    def get_move_history(self) -> MoveHistory:
        """Get the complete move history."""
        return self.move_history
    
    def switch_player(self) -> None:
        self._current_player = Player.WHITE if self._board.internal_board.turn else Player.BLACK
        self.updated_at = datetime.now()
    
    def get_previous_player(self) -> Player:
        """Get the previous player (who just made a move)."""
        return Player.BLACK if self._current_player == Player.WHITE else Player.WHITE
    
    def end_game(self, winner: Optional[Player], reason: str) -> None:
        """End the game with specified result."""
        self.is_ended = True
        self.winner = winner
        self.end_reason = reason
        self._state = GameState.GAME_OVER
        self.updated_at = datetime.now()
    
    def get_result(self) -> GameResult:
        """Get the game result."""
        if not self.is_ended:
            return GameResult.IN_PROGRESS
        elif self.winner == Player.WHITE:
            return GameResult.WHITE_WINS
        elif self.winner == Player.BLACK:
            return GameResult.BLACK_WINS
        else:
            return GameResult.DRAW
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive game status."""
        return {
            "game_id": self.game_id,
            "white_player": self.white_player,
            "black_player": self.black_player,
            "current_player": self._current_player.value,
            "is_ended": self.is_ended,
            "winner": self.winner.value if self.winner else None,
            "end_reason": self.end_reason,
            "move_count": self._move_count,
            "fen": self._board.fen,
            "state": self._state.value,
            "in_check": self._board.is_in_check() if hasattr(self._board, 'is_in_check') else False
        }
    
    def __repr__(self) -> str:
        """Debug representation."""
        return f"Game(id='{self.id}', state={self._state}, move_count={self._move_count})"