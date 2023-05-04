import pygame

# Khai báo một số màu sắc cho các quân cờ và bàn cờ
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 128, 0)
BLUE = (0, 0, 128)

# Khởi tạo bàn cờ với các quân cờ ban đầu
board = [
    ["r", "n", "b", "q", "k", "b", "n", "r"],
    ["p", "p", "p", "p", "p", "p", "p", "p"],
    [" ", ".", " ", ".", " ", ".", " ", "."],
    [".", " ", ".", " ", ".", " ", ".", " "],
    [" ", ".", " ", ".", " ", ".", " ", "."],
    [".", " ", ".", " ", ".", " ", ".", " "],
    ["c", "c", "c", "c", "c", "c", "c", "c"],
    ["x", "m", "t", "h", "v", "t", "m", "x"]
]

# Khởi tạo Pygame
pygame.init()

# Thiết lập kích thước cửa sổ và tên của trò chơi
size = (640, 640)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Cờ vua")

# Thiết lập font chữ
font = pygame.font.Font(None, 32)

# Vòng lặp chính của trò chơi
done = False
clock = pygame.time.Clock()

# Lấy tọa độ của ô cờ khi người dùng click vào
def get_coord(pos):
    x, y = pos
    row = y // 80
    col = x // 80
    return row, col

# Thêm biến để lưu trữ quân cờ được chọn và vị trí của nó
selected_piece = None
selected_row, selected_col = None, None

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            row, col = get_coord(pos)

            if selected_piece:
                # Di chuyển quân cờ đã chọn đến vị trí mới
                board[row][col] = selected_piece
                board[selected_row][selected_col] = " " if (selected_row + selected_col) % 2 == 0 else "."
                selected_piece = None
                selected_row, selected_col = None, None
            elif board[row][col] != " " and board[row][col] != ".":
                # Chọn quân cờ và lưu lại vị trí của nó
                selected_piece = board[row][col]
                selected_row, selected_col = row, col
                print("Đã click vào quân cờ ở hàng", row, "cột", col)

    # Vẽ bàn cờ và các quân cờ
    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else BLACK
            pygame.draw.rect(screen, color, [col * 80, row * 80, 80, 80])
            piece = board[row][col]
            if piece != " " and piece != ".":
                img_path = f"images/{piece.lower()}.png"  # Thay "images" bằng thư mục chứa ảnh của bạn
                img = pygame.image.load(img_path)
                if piece.isupper():
                    img = pygame.transform.scale(img, (70, 70))
                else:
                    img = pygame.transform.scale(img, (70, 70))
                screen.blit(img, (col * 80 + 6, row * 80 + 6))

    # Vẽ các ô vuông hỗ trợ chọn quân cờ
    pygame.draw.rect(screen, GREEN, [0, 0, 640, 640], 5)
    for row in range(8):
        for col in range(8):
            if board[row][col] != " " and board[row][col] != ".":
                pygame.draw.rect(screen, BLUE, [col * 80, row * 80, 80, 80], 5)

    # Hiển thị lượt chơi
    text = font.render("Đến lượt của người chơi 1", True, BLACK)
    screen.blit(text, [10, 640])

    # Cập nhật màn hình
    pygame.display.flip()
    clock.tick(60)

# Đóng cửa sổ Pygame
pygame.quit()
