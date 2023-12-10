import pygame
from config import WINDOW_WIDTH, WINDOW_HEIGHT, BOARD_SIZE, SQUARE_SIZE, STATUS_HEIGHT, load_images
# from config import SQUARE_SIZE, FPS, load_images
IMAGES = load_images()

import sys

def draw_board(screen, board):
    colors = [pygame.Color("white"), pygame.Color("gray")]

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            color = colors[((row + col) % 2)]
            pygame.draw.rect(screen, color, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

            piece = board.piece_at(row * BOARD_SIZE + col)
            if piece:
                piece_name = piece.color and piece.symbol().lower() or piece.symbol()
                piece_name = ('w' if piece.color else 'b') + piece_name.lower()
                screen.blit(IMAGES[piece_name], pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_status(screen, board):
    status_rect = pygame.Rect(0, WINDOW_WIDTH, WINDOW_WIDTH, STATUS_HEIGHT)
    pygame.draw.rect(screen, pygame.Color("white"), status_rect)

    status_font = pygame.font.Font(None, 36)
    if board.turn:
        status_text = "Turn: White"
    else:
        status_text = "Turn: Black"
    status_surface = status_font.render(status_text, True, pygame.Color("black"))
    status_position = status_rect.center
    screen.blit(status_surface, status_surface.get_rect(center=status_position))

def draw_selected_square(screen, square):
    row, col = square // BOARD_SIZE, square % BOARD_SIZE
    pygame.draw.rect(screen, pygame.Color("blue"), pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

def draw_valid_moves(screen, valid_moves):
    for move in valid_moves:
        row, col = move.to_square // BOARD_SIZE, move.to_square % BOARD_SIZE
        pygame.draw.circle(screen, pygame.Color("green"), (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), 10)

def show_start_screen(screen):
    screen.fill(pygame.Color("white"))
    font = pygame.font.Font(None, 48)
    text = font.render("New Game", True, pygame.Color("black"))
    text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

    button_rect = pygame.Rect(text_rect.left - 10, text_rect.top - 10, text_rect.width + 20, text_rect.height + 20)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        if button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, pygame.Color("lightgray"), button_rect)  # Nút sẽ thay đổi màu khi chuột di chuyển qua
        else:
            pygame.draw.rect(screen, pygame.Color("darkgray"), button_rect)

        screen.blit(text, text_rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(mouse_pos):
                    return  # Bắt đầu trò chơi
