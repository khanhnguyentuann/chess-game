import pygame
from config import WINDOW_WIDTH, WINDOW_HEIGHT, BOARD_SIZE, SQUARE_SIZE, STATUS_HEIGHT, load_images, WHITE, GREEN, DARK_GREEN, BLACK
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

# Show màn hình hướng dẫn
def show_instructions(screen):
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    running = False

        screen.fill(WHITE)
        font = pygame.font.Font(None, 36)
        instructions = ["Welcome to Chess Game!", "Press SPACE to start.", "Use mouse to move pieces."]
        for i, line in enumerate(instructions):
            text = font.render(line, True, BLACK)
            screen.blit(text, (50, 50 + i * 40))

        pygame.display.flip()


def draw_start_button(screen, text, rect, color, hover_color, text_color, font_size):
    mouse_pos = pygame.mouse.get_pos()
    button_color = hover_color if rect.collidepoint(mouse_pos) else color

    pygame.draw.rect(screen, button_color, rect)
    pygame.draw.rect(screen, WHITE, rect, 2)  # Viền trắng

    font = pygame.font.Font(None, font_size)
    text_render = font.render(text, True, text_color)
    text_rect = text_render.get_rect(center=rect.center)
    screen.blit(text_render, text_rect)


def show_start_screen(screen):
    running = True
    button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 75, WINDOW_HEIGHT // 2 + 20, 150, 50)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    running = False

        screen.fill(WHITE) # Xóa màn hình và vẽ nền trắng

        # Vẽ tiêu đề
        font = pygame.font.Font(None, 48)
        text = font.render("Chess Game", True, GREEN)
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        screen.blit(text, text_rect)

        # Vẽ nút "Bắt đầu"
        draw_start_button(screen, "Start Game", button_rect, GREEN, DARK_GREEN, WHITE, 36)

        # Cập nhật màn hình
        pygame.display.flip()

        # Kiểm tra nút "Bắt đầu" đã được nhấn chưa
        mouse_pos = pygame.mouse.get_pos()
        if button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, DARK_GREEN, button_rect)  # Nút sẽ thay đổi màu khi chuột di chuyển qua
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    return  # Bắt đầu trò chơi

