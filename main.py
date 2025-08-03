"""
Chess Game - Main Entry Point
Clean Architecture chess game with dependency injection and event-driven design.

Entry point that configures dependencies and starts the application.
"""

import logging
import sys

# Import application manager
from src.application_manager import get_application_manager, shutdown_application_manager


def main():
    """
    Main function that initializes the application and starts the game.
    """
    app_manager = None
    try:
        # Initialize application manager
        app_manager = get_application_manager()
        
        # Get application context
        app_context = app_manager.get_context()
        
        # Create presentation layer components
        game_controller = app_context.create_game_controller()
        game_view_model = app_context.create_game_view_model()
        
        # Initialize and run the menu system
        from src.presentation.ui.menu_system import MenuSystem
        menu = MenuSystem()
        menu.run()

    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        print(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        if app_manager:
            shutdown_application_manager()
        # Cleanup pygame
        try:
            import pygame
            if pygame.get_init():
                pygame.quit()
        except ImportError:
            pass
        print("Game shutdown complete")


if __name__ == "__main__":
    main()
