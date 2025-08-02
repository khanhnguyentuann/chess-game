"""
Chess Game - Main Entry Point
Clean Architecture chess game with dependency injection and event-driven design.

Entry point that configures dependencies and starts the application.
"""

import sys
import logging
import os
from pathlib import Path

# Set pygame window to center on screen before any pygame initialization
os.environ['SDL_VIDEO_CENTERED'] = '1'

# Import composition root
from src.composition_root import get_container, reset_container


def main():
    """
    Main function that initializes the application and starts the game.
    """
    try:
        # Import and run the menu system directly
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
        reset_container()
        print("Game shutdown complete")


if __name__ == "__main__":
    main()
