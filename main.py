import pygame
from chess_game import ChessGame
from ui import show_start_screen
from config import WINDOW_WIDTH, WINDOW_HEIGHT

def main():
    pygame.init()
    SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Chess Game")
    show_start_screen(SCREEN)
    game = ChessGame(SCREEN)
    game.main_loop()

if __name__ == "__main__":
    main()
