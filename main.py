"""
Chess Game - Main Entry Point
A clean MVC-architected chess game using Pygame and python-chess.

This is the entry point that initializes Pygame and starts the game controller.
"""

import pygame
import sys
from controllers.game_controller import GameController
from config import WINDOW_WIDTH, WINDOW_HEIGHT


def main():
    """
    Main function that initializes Pygame and starts the chess game.
    """
    try:
        # Initialize Pygame
        pygame.init()
        
        # Create the main game window
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Chess Game - MVC Architecture")
        
        # Create and start the game controller
        game_controller = GameController(screen)
        game_controller.start_game()
        
    except Exception as e:
        print(f"Error starting game: {e}")
        pygame.quit()
        sys.exit(1)


if __name__ == "__main__":
    main()
