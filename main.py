import pygame
import sys
import chess

pygame.init()

FPS = 30
WINDOW_WIDTH = 512
WINDOW_HEIGHT = 600
BOARD_SIZE = 8
SQUARE_SIZE = WINDOW_WIDTH // BOARD_SIZE
STATUS_HEIGHT = 88
####
CLOCK = pygame.time.Clock()
SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Chess Game")

def load_images():
    pieces = ["r", "n", "b", "q", "k", "p"]
    colors = ["w", "b"]
    images = {}
    for color in colors:
        for piece in pieces:
            name = f"{color}{piece}"
            images[name] = pygame.transform.scale(pygame.image.load(f"images/{name}.png"), (SQUARE_SIZE, SQUARE_SIZE))
    return images

IMAGES = load_images()

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

# hàm chính để chạy trò chơi
def main():
    board = chess.Board()
    selected_square = None
    valid_moves = []

    while not board.is_game_over():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                position = pygame.mouse.get_pos()
                col, row = position[0] // SQUARE_SIZE, position[1] // SQUARE_SIZE
                square = row * BOARD_SIZE + col



                if selected_square is None:
                    piece = board.piece_at(square)
                    if piece and (piece.color == board.turn):
                        selected_square = square
                        valid_moves = [move for move in board.legal_moves if move.from_square == square]
                else:
                    move = chess.Move(selected_square, square)
                    if move in valid_moves:
                        board.push(move)
                    selected_square = None
                    valid_moves = []

        draw_board(SCREEN, board)
        draw_status(SCREEN, board)
        if selected_square is not None:
            draw_selected_square(SCREEN, selected_square)
            draw_valid_moves(SCREEN, valid_moves)
        pygame.display.flip()
        CLOCK.tick(FPS)

if __name__ == "__main__":
    main()