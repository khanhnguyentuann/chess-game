"""
Domain Repository Interfaces
Defines contracts for data persistence without implementation details.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID

from ..entities.game import Game
from ..entities.board import Board
from ..entities.move_history import MoveHistory
from ...shared.types.type_definitions import GameState


class IGameRepository(ABC):
    """Interface for game persistence operations."""
    
    @abstractmethod
    async def save_game(self, game: Game) -> str:
        """
        Save a game and return its ID.
        
        Args:
            game: Game instance to save
            
        Returns:
            Unique game ID
        """
        pass
    
    @abstractmethod
    async def load_game(self, game_id: str) -> Optional[Game]:
        """
        Load a game by ID.
        
        Args:
            game_id: Unique game identifier
            
        Returns:
            Game instance or None if not found
        """
        pass
    
    @abstractmethod
    async def delete_game(self, game_id: str) -> bool:
        """
        Delete a game by ID.
        
        Args:
            game_id: Game to delete
            
        Returns:
            True if deleted successfully
        """
        pass
    
    @abstractmethod
    async def list_games(self, player_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List saved games.
        
        Args:
            player_id: Optional filter by player
            
        Returns:
            List of game metadata
        """
        pass
    
    @abstractmethod
    async def save_game_state(self, game_id: str, state: GameState) -> bool:
        """Save current game state."""
        pass
    
    @abstractmethod
    async def load_game_state(self, game_id: str) -> Optional[GameState]:
        """Load game state by ID."""
        pass


class IMoveHistoryRepository(ABC):
    """Interface for move history persistence."""
    
    @abstractmethod
    async def save_move_history(self, game_id: str, history: MoveHistory) -> bool:
        """Save move history for a game."""
        pass
    
    @abstractmethod
    async def load_move_history(self, game_id: str) -> Optional[MoveHistory]:
        """Load move history for a game."""
        pass
    
    @abstractmethod
    async def append_move(self, game_id: str, move_data: Dict[str, Any]) -> bool:
        """Append a single move to history."""
        pass


class ISettingsRepository(ABC):
    """Interface for user settings persistence."""
    
    @abstractmethod
    async def save_settings(self, user_id: str, settings: Dict[str, Any]) -> bool:
        """Save user settings."""
        pass
    
    @abstractmethod
    async def load_settings(self, user_id: str) -> Dict[str, Any]:
        """Load user settings."""
        pass
    
    @abstractmethod
    async def update_setting(self, user_id: str, key: str, value: Any) -> bool:
        """Update a specific setting."""
        pass
