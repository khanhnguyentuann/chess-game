"""
Dummy Notification Service for testing
"""

from typing import Any, Dict

from ...domain.entities.game import Game
from ...domain.interfaces.services import INotificationService
from ...shared.types.enums import GameResult, Player


class DummyNotificationService(INotificationService):
    """Dummy implementation of notification service for testing."""

    async def notify_move_made(self, game: Game, move_data: Dict[str, Any]) -> None:
        """Notify that a move was made."""
        print(f"📢 Move made: {move_data.get('notation', 'Unknown move')}")

    async def notify_game_over(self, game: Game, result: GameResult) -> None:
        """Notify that game ended."""
        print(f"🏁 Game over! Result: {result.value}")

    async def notify_check(self, game: Game, player: Player) -> None:
        """Notify that a player is in check."""
        print(f"⚠️ Check! {player.value} is in check")

    async def notify_error(self, error_message: str, context: Dict[str, Any]) -> None:
        """Notify about errors."""
        print(f"❌ Error: {error_message}")
        if context:
            print(f"   Context: {context}")
