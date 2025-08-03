"""
Game Controller
Handles user interactions and coordinates between UI and application layer.
"""

import asyncio
from typing import Any, Dict, List, Optional, Tuple

from ...application.services.game_application_service import IGameApplicationService
from ...domain.entities.game import Game
from ...domain.value_objects.square import Square
from ...shared.types.enums import Player
from ...shared.exceptions.game_exceptions import GameNotFoundException


class GameController:
    """Controller for handling game-related user interactions."""
    
    def __init__(self, game_service: IGameApplicationService):
        """Initialize game controller."""
        self._game_service = game_service
        self._current_game: Optional[Game] = None
        self._selected_square: Optional[Square] = None
        self._legal_moves: List[Square] = []
        self._is_game_active = False
    
    async def start_new_game(self, white_player: str = "Player 1", black_player: str = "Player 2") -> Dict[str, Any]:
        """
        Start a new game.
        
        Args:
            white_player: Name of white player
            black_player: Name of black player
            
        Returns:
            Game state information
        """
        try:
            # Create new game using application service
            game_state = await self._game_service.get_game_state(
                game_id=None,  # New game
                white_player=white_player,
                black_player=black_player
            )
            
            self._current_game = game_state.game
            self._is_game_active = True
            self._selected_square = None
            self._legal_moves = []
            
            return {
                "success": True,
                "game_id": game_state.game.game_id,
                "current_player": game_state.current_player,
                "board_state": game_state.board_state,
                "message": "New game started"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to start new game"
            }
    
    async def load_game(self, game_id: str) -> Dict[str, Any]:
        """
        Load an existing game.
        
        Args:
            game_id: ID of the game to load
            
        Returns:
            Game state information
        """
        try:
            game_state = await self._game_service.get_game_state(game_id=game_id)
            
            self._current_game = game_state.game
            self._is_game_active = not game_state.game.is_ended
            self._selected_square = None
            self._legal_moves = []
            
            return {
                "success": True,
                "game_id": game_state.game.game_id,
                "current_player": game_state.current_player,
                "board_state": game_state.board_state,
                "message": "Game loaded successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to load game"
            }
    
    async def select_square(self, square_index: int) -> Dict[str, Any]:
        """
        Select a square on the board.
        
        Args:
            square_index: Index of the square to select
            
        Returns:
            Selection result with legal moves
        """
        if not self._is_game_active or not self._current_game:
            return {
                "success": False,
                "error": "No active game",
                "message": "Please start or load a game first"
            }
        
        try:
            square = Square(square_index)
            
            # Check if square has a piece and belongs to current player
            piece = self._current_game.board.get_piece_at(square_index)
            if not piece:
                return {
                    "success": False,
                    "error": "No piece at square",
                    "message": "No piece at selected square"
                }
            
            if piece.color != self._current_game.current_player:
                return {
                    "success": False,
                    "error": "Wrong player",
                    "message": "Not your turn"
                }
            
            # Get legal moves for the selected piece
            legal_moves = await self._game_service.get_legal_moves(
                game_id=self._current_game.game_id,
                square=square_index
            )
            
            self._selected_square = square
            self._legal_moves = [Square(move) for move in legal_moves.legal_moves]
            
            return {
                "success": True,
                "selected_square": square_index,
                "legal_moves": legal_moves.legal_moves,
                "piece": piece.type.value,
                "message": f"Selected {piece.type.value} at square {square_index}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to select square"
            }
    
    async def make_move(self, from_square: int, to_square: int, promotion_piece: Optional[str] = None) -> Dict[str, Any]:
        """
        Make a move on the board.
        
        Args:
            from_square: Source square index
            to_square: Destination square index
            promotion_piece: Piece type for pawn promotion (optional)
            
        Returns:
            Move result
        """
        if not self._is_game_active or not self._current_game:
            return {
                "success": False,
                "error": "No active game",
                "message": "Please start or load a game first"
            }
        
        try:
            # Make move using application service
            move_result = await self._game_service.make_move(
                game_id=self._current_game.game_id,
                from_square=from_square,
                to_square=to_square,
                promotion_piece=promotion_piece
            )
            
            # Update local state
            self._current_game = move_result.game
            self._selected_square = None
            self._legal_moves = []
            
            # Check if game is over
            if move_result.game.is_ended:
                self._is_game_active = False
            
            return {
                "success": True,
                "move_notation": move_result.notation,
                "current_player": move_result.current_player,
                "board_state": move_result.board_state,
                "is_check": move_result.is_check,
                "is_checkmate": move_result.is_checkmate,
                "is_stalemate": move_result.is_stalemate,
                "game_ended": move_result.game.is_ended,
                "message": f"Move made: {move_result.notation}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to make move"
            }
    
    async def undo_move(self) -> Dict[str, Any]:
        """
        Undo the last move.
        
        Returns:
            Undo result
        """
        if not self._current_game:
            return {
                "success": False,
                "error": "No game loaded",
                "message": "Please load a game first"
            }
        
        try:
            undo_result = await self._game_service.undo_move(game_id=self._current_game.game_id)
            
            self._current_game = undo_result.game
            self._selected_square = None
            self._legal_moves = []
            self._is_game_active = not undo_result.game.is_ended
            
            return {
                "success": True,
                "current_player": undo_result.current_player,
                "board_state": undo_result.board_state,
                "message": "Move undone successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to undo move"
            }
    
    async def redo_move(self) -> Dict[str, Any]:
        """
        Redo the last undone move.
        
        Returns:
            Redo result
        """
        if not self._current_game:
            return {
                "success": False,
                "error": "No game loaded",
                "message": "Please load a game first"
            }
        
        try:
            redo_result = await self._game_service.redo_move(game_id=self._current_game.game_id)
            
            self._current_game = redo_result.game
            self._selected_square = None
            self._legal_moves = []
            self._is_game_active = not redo_result.game.is_ended
            
            return {
                "success": True,
                "current_player": redo_result.current_player,
                "board_state": redo_result.board_state,
                "message": "Move redone successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to redo move"
            }
    
    def get_current_game_state(self) -> Optional[Dict[str, Any]]:
        """
        Get current game state.
        
        Returns:
            Current game state or None if no game
        """
        if not self._current_game:
            return None
        
        return {
            "game_id": self._current_game.game_id,
            "current_player": self._current_game.current_player,
            "board_state": self._current_game.board.to_fen(),
            "is_ended": self._current_game.is_ended,
            "winner": self._current_game.winner.value if self._current_game.winner else None,
            "selected_square": self._selected_square.index if self._selected_square else None,
            "legal_moves": [move.index for move in self._legal_moves],
            "move_count": self._current_game.move_history.get_move_count(),
        }
    
    def get_selected_square(self) -> Optional[int]:
        """Get currently selected square index."""
        return self._selected_square.index if self._selected_square else None
    
    def get_legal_moves(self) -> List[int]:
        """Get legal moves for currently selected piece."""
        return [move.index for move in self._legal_moves]
    
    def clear_selection(self) -> None:
        """Clear current square selection."""
        self._selected_square = None
        self._legal_moves = []
    
    def is_game_active(self) -> bool:
        """Check if game is currently active."""
        return self._is_game_active
    
    def get_current_player(self) -> Optional[Player]:
        """Get current player."""
        return self._current_game.current_player if self._current_game else None 