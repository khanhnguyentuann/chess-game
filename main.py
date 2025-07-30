"""
Chess Game - Main Entry Point
Clean Architecture chess game with dependency injection and event-driven design.

Entry point that configures dependencies and starts the application.
"""

import asyncio
import sys
import logging
from pathlib import Path

# Import composition root
from src.composition_root import get_container, reset_container

# Import application use cases
from src.application.use_cases.make_move import MakeMoveUseCase

# Import domain entities
from src.domain.entities.game import Game
from src.domain.entities.board import Board

# Import shared types
from src.shared.types.enums import Player


def create_sample_game(container) -> Game:
    """Create a sample game for testing the new architecture."""
    # Get services from container
    move_validator = container.get("move_validator")
    
    # Create a new game
    board = Board()
    game = Game(
        white_player="Player 1",
        black_player="Player 2",
        board=board
    )
    
    return game


async def run_sample_game():
    """Run a sample game to test the new architecture."""
    try:
        # Get container
        container = get_container()
        
        # Create sample game
        game = create_sample_game(container)
        
        # Get use case
        make_move_use_case: MakeMoveUseCase = container.get("make_move_use_case")
        
        print("Chess Game - Clean Architecture Demo")
        print("====================================")
        print(f"Game ID: {game.game_id}")
        print(f"White Player: {game.white_player}")
        print(f"Black Player: {game.black_player}")
        print(f"Current Player: {game.current_player.value}")
        print()
        
        # Get legal moves
        legal_moves = await make_move_use_case.get_legal_moves(game)
        print(f"Legal moves available: {len(legal_moves)}")
        
        if legal_moves:
            # Try to make a move (e2-e4)
            from src.shared.types.type_definitions import MoveRequest
            import chess
            
            move_request = MoveRequest(
                from_square=chess.E2,
                to_square=chess.E4,
                promotion=None
            )
            
            print(f"\nAttempting move: e2-e4")
            result = await make_move_use_case.execute(game, move_request)
            
            if result["success"]:
                print(f"✓ Move successful: {result['message']}")
                print(f"Current player: {game.current_player.value}")
                print(f"Can undo: {result['can_undo']}")
                print(f"Game status: {result['game_status']}")
            else:
                print(f"✗ Move failed: {result['message']}")
        
        print("\n✓ Architecture test completed successfully!")
        
    except Exception as e:
        logging.error(f"Error in sample game: {e}", exc_info=True)
        print(f"✗ Error: {e}")


def main():
    """
    Main function that initializes the application and starts the game.
    """
    try:
        print("Chess Game - Clean Architecture")
        print("==============================")
        print("Choose an option:")
        print("1. Run demo (console)")
        print("2. Start game with UI")
        print("3. Exit")
        
        while True:
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == "1":
                print("\nStarting demo...")
                asyncio.run(run_sample_game())
                break
            elif choice == "2":
                print("\nStarting game with UI...")
                # Import and run the menu system
                from src.presentation.ui.menu_system import MenuSystem
                menu = MenuSystem()
                menu.run()
                break
            elif choice == "3":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
        
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        print(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        reset_container()
        print("Game shutdown complete")


if __name__ == "__main__":
    main()
