"""
Clean Architecture Chess Game - Architecture Validation Test
This test validates that the Clean Architecture implementation works correctly.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.composition_root import get_container, reset_container
from src.domain.entities.game import Game
from src.shared.types.type_definitions import MoveRequest
from src.shared.types.enums import Player


async def test_architecture():
    """Test the complete Clean Architecture flow."""
    print("🧪 Testing Clean Architecture Chess Game...")
    print("=" * 50)
    
    try:
        # Get dependencies from container
        container = get_container()
        make_move_use_case = container.get("make_move_use_case")
        game_repository = container.get("game_repository")
        move_history_repository = container.get("move_history_repository")
        
        print("✅ Dependency injection container loaded successfully")
        
        # Create a new game
        game = Game(
            white_player="Test Player 1",
            black_player="Test Player 2"
        )
        
        print(f"✅ Game created: {game.game_id}")
        print(f"   White: {game.white_player}")
        print(f"   Black: {game.black_player}")
        print(f"   Current player: {game.current_player.value}")
        
        # Test multiple moves
        test_moves = [
            MoveRequest(from_square=12, to_square=28),  # e2-e4
            MoveRequest(from_square=52, to_square=36),  # e7-e5
            MoveRequest(from_square=6, to_square=21),   # g1-f3
            MoveRequest(from_square=57, to_square=42),  # b8-c6
        ]
        
        move_names = ["e2-e4", "e7-e5", "g1-f3", "b8-c6"]
        
        for i, (move_request, move_name) in enumerate(zip(test_moves, move_names), 1):
            print(f"\n🎯 Move {i}: {move_name}")
            
            result = await make_move_use_case.execute(game, move_request)
            
            if result.get("success", False):
                print(f"   ✅ {result.get('message', 'Move successful')}")
                print(f"   Current player: {game.current_player.value}")
                print(f"   Move count: {game.move_history.get_move_count()}")
            else:
                print(f"   ❌ {result.get('message', 'Move failed')}")
                return False
        
        # Test game state
        game_status = game.get_status()
        print(f"\n📊 Final Game Status:")
        print(f"   Game ID: {game_status['game_id']}")
        print(f"   Current player: {game_status['current_player']}")
        print(f"   Move count: {game_status['move_count']}")
        print(f"   Game state: {game_status['state']}")
        print(f"   In check: {game_status['in_check']}")
        
        # Test repository persistence
        saved_id = await game_repository.save_game(game)
        print(f"\n💾 Game saved to repository: {saved_id}")
        
        loaded_game = await game_repository.load_game(saved_id)
        if loaded_game:
            print(f"✅ Game loaded from repository successfully")
        else:
            print(f"❌ Failed to load game from repository")
            return False
        
        # Test move history persistence
        saved_history = await move_history_repository.save_move_history(
            game.game_id, game.move_history
        )
        print(f"✅ Move history saved: {saved_history}")
        
        loaded_history = await move_history_repository.load_move_history(game.game_id)
        if loaded_history:
            print(f"✅ Move history loaded successfully")
        else:
            print(f"❌ Failed to load move history")
            return False
        
        # Test undo functionality
        print(f"\n↶ Testing undo functionality...")
        if game.move_history.can_undo():
            undone_move = game.move_history.undo_move()
            print(f"✅ Undone move: {undone_move.move if undone_move else 'None'}")
            print(f"   Move count after undo: {game.move_history.get_move_count()}")
        
        print(f"\n🎉 All tests passed! Clean Architecture is working correctly!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        reset_container()
        print(f"\n🧹 Cleanup completed")


async def main():
    """Main test runner."""
    print("Clean Architecture Chess Game - Validation Test")
    print("=" * 60)
    
    success = await test_architecture()
    
    if success:
        print("\n✅ ALL TESTS PASSED - Clean Architecture is fully functional!")
        print("\n📋 Architecture Summary:")
        print("   🎯 Domain Layer: Entities, Services, Events")
        print("   🔄 Application Layer: Use Cases, Commands")
        print("   🔧 Infrastructure Layer: Repositories, Services")
        print("   🤝 Shared Layer: Types, Config, Utils")
        print("   🎭 Composition Root: Dependency Injection")
        return 0
    else:
        print("\n❌ TESTS FAILED - Please check the implementation")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
