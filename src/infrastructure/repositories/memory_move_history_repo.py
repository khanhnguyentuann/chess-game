"""
Memory Move History Repository
In-memory implementation of move history repository for development and testing.
"""

from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import uuid

from ...domain.interfaces.repositories import IMoveHistoryRepository
from ...domain.entities.move_history import MoveHistory
from ...shared.exceptions.game_exceptions import PersistenceException


class MemoryMoveHistoryRepository(IMoveHistoryRepository):
    """
    In-memory implementation of move history repository.
    Stores move histories in memory using dictionaries.
    """
    
    def __init__(self):
        self._move_histories: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)
        self.logger.info("Memory move history repository initialized")
    
    async def save_move_history(self, game_id: str, history: MoveHistory) -> bool:
        """
        Save move history for a game.
        
        Args:
            game_id: Game ID
            history: MoveHistory entity to save
            
        Returns:
            True if successful
            
        Raises:
            PersistenceException: If save operation fails
        """
        try:
            # Find existing history for this game
            existing_history_id = None
            for history_id, data in self._move_histories.items():
                if data["game_id"] == game_id:
                    existing_history_id = history_id
                    break
            
            if existing_history_id:
                # Update existing history
                history_id = existing_history_id
            else:
                # Create new history
                history_id = history.history_id or str(uuid.uuid4())
                history.history_id = history_id
            
            # Save to storage
            self._move_histories[history_id] = {
                "history_id": history_id,
                "game_id": game_id,
                "moves": [
                    {
                        "move": str(move.move),
                        "timestamp": move.timestamp.isoformat(),
                        "fen_before": move.fen_before,
                        "fen_after": move.fen_after,
                        "captured_piece": move.captured_piece,
                        "is_check": move.is_check,
                        "is_checkmate": move.is_checkmate,
                        "move_number": move.move_number,
                        "player": move.player.value
                    }
                    for move in history.moves
                ],
                "created_at": history.created_at.isoformat(),
                "updated_at": datetime.now().isoformat(),
                "move_count": history.get_move_count(),
                "current_position": history.current_position
            }
            
            self.logger.debug(f"Move history saved for game: {game_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save move history for game {game_id}: {str(e)}")
            raise PersistenceException(f"Failed to save move history: {str(e)}")
    
    async def load_move_history(self, game_id: str) -> Optional[MoveHistory]:
        """
        Load move history for a game.
        
        Args:
            game_id: Game ID to find move history for
            
        Returns:
            MoveHistory entity or None if not found
        """
        try:
            for history_data in self._move_histories.values():
                if history_data["game_id"] == game_id:
                    # Create MoveHistory from stored data
                    move_history = MoveHistory(
                        game_id=history_data["game_id"],
                        history_id=history_data["history_id"],
                        created_at=datetime.fromisoformat(history_data["created_at"])
                    )
                    
                    # Restore moves (simplified - in real implementation would recreate full move objects)
                    move_history.current_position = history_data.get("current_position", 0)
                    
                    self.logger.debug(f"Move history loaded for game: {game_id}")
                    return move_history
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to load move history for game {game_id}: {str(e)}")
            raise PersistenceException(f"Failed to load move history: {str(e)}")
    
    async def append_move(self, game_id: str, move_data: Dict[str, Any]) -> bool:
        """
        Append a single move to history.
        
        Args:
            game_id: Game ID
            move_data: Move data to append
            
        Returns:
            True if successful
        """
        try:
            # Find existing history or create new one
            history = await self.load_move_history(game_id)
            if not history:
                history = MoveHistory(game_id=game_id)
            
            # Create move record from data (simplified)
            # In real implementation, would properly construct MoveRecord
            
            # Save updated history
            return await self.save_move_history(game_id, history)
            
        except Exception as e:
            self.logger.error(f"Failed to append move for game {game_id}: {str(e)}")
            raise PersistenceException(f"Failed to append move: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get repository statistics."""
        return {
            "total_histories": len(self._move_histories),
            "repository_type": "memory"
        }
    
    def cleanup(self) -> None:
        """Cleanup repository resources."""
        self._move_histories.clear()
        self.logger.info("Memory move history repository cleaned up")
