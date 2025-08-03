"""
In-Memory Game Repository Implementation
For development and testing purposes.
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ...domain.entities.game import Game
from ...domain.interfaces.repositories import IGameRepository
from ...shared.exceptions.game_exceptions import (
    GameNotFoundException,
    PersistenceException,
)
from ...shared.types.type_definitions import GameState


class MemoryGameRepository(IGameRepository):
    """In-memory implementation of game repository."""

    def __init__(self):
        self._games: Dict[str, Game] = {}
        self._game_states: Dict[str, GameState] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}

    async def save_game(self, game: Game) -> str:
        """Save a game in memory."""
        try:
            game_id = game.game_id or str(uuid.uuid4())
            game.game_id = game_id

            # Store the game
            self._games[game_id] = game

            # Store metadata
            self._metadata[game_id] = {
                "game_id": game_id,
                "white_player": game.white_player,
                "black_player": game.black_player,
                "created_at": game.created_at.isoformat(),
                "updated_at": datetime.now().isoformat(),
                "is_ended": game.is_ended,
                "winner": game.winner.value if game.winner else None,
                "end_reason": game.end_reason,
                "move_count": game.move_history.get_move_count(),
                "current_player": game.current_player.value,
                "fen": game.board.to_fen(),
            }

            return game_id

        except Exception as e:
            raise PersistenceException(f"Failed to save game: {str(e)}")

    async def load_game(self, game_id: str) -> Optional[Game]:
        """Load a game from memory."""
        try:
            return self._games.get(game_id)
        except Exception as e:
            raise PersistenceException(f"Failed to load game: {str(e)}")

    async def delete_game(self, game_id: str) -> bool:
        """Delete a game from memory."""
        try:
            if game_id in self._games:
                del self._games[game_id]
                if game_id in self._game_states:
                    del self._game_states[game_id]
                if game_id in self._metadata:
                    del self._metadata[game_id]
                return True
            return False
        except Exception as e:
            raise PersistenceException(f"Failed to delete game: {str(e)}")

    async def list_games(self, player_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all games in memory."""
        try:
            games = []
            for game_id, metadata in self._metadata.items():
                # Filter by player if specified
                if player_id and player_id not in [
                    metadata["white_player"],
                    metadata["black_player"],
                ]:
                    continue
                games.append(metadata.copy())

            # Sort by updated_at (most recent first)
            games.sort(key=lambda x: x["updated_at"], reverse=True)
            return games

        except Exception as e:
            raise PersistenceException(f"Failed to list games: {str(e)}")

    async def save_game_state(self, game_id: str, state: GameState) -> bool:
        """Save game state."""
        try:
            self._game_states[game_id] = state
            return True
        except Exception as e:
            raise PersistenceException(f"Failed to save game state: {str(e)}")

    async def load_game_state(self, game_id: str) -> Optional[GameState]:
        """Load game state."""
        try:
            return self._game_states.get(game_id)
        except Exception as e:
            raise PersistenceException(f"Failed to load game state: {str(e)}")

    def clear_all(self) -> None:
        """Clear all stored data (for testing)."""
        self._games.clear()
        self._game_states.clear()
        self._metadata.clear()

    def get_statistics(self) -> Dict[str, Any]:
        """Get repository statistics."""
        return {
            "total_games": len(self._games),
            "active_games": len([g for g in self._games.values() if not g.is_ended]),
            "completed_games": len([g for g in self._games.values() if g.is_ended]),
            "memory_usage": {
                "games": len(self._games),
                "states": len(self._game_states),
                "metadata": len(self._metadata),
            },
        }
