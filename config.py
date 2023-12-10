import pygame

FPS = 30
WINDOW_WIDTH = 512
WINDOW_HEIGHT = 600
BOARD_SIZE = 8
SQUARE_SIZE = WINDOW_WIDTH // BOARD_SIZE
STATUS_HEIGHT = 88

def load_images():
    pieces = ["r", "n", "b", "q", "k", "p"]
    colors = ["w", "b"]
    images = {}
    for color in colors:
        for piece in pieces:
            name = f"{color}{piece}"
            images[name] = pygame.transform.scale(pygame.image.load(f"images/{name}.png"), (SQUARE_SIZE, SQUARE_SIZE))
    return images
