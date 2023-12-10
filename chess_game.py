import pygame
import chess
from ui import draw_board, draw_status, draw_selected_square, draw_valid_moves
from config import SQUARE_SIZE, FPS
import sys

class ChessGame:
    def __init__(self, screen):
        self.screen = screen
        self.board = chess.Board()
        self.selected_square = None
        self.valid_moves = []

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                position = pygame.mouse.get_pos()
                col, row = position[0] // SQUARE_SIZE, position[1] // SQUARE_SIZE
                square = row * 8 + col

                if self.selected_square is None:
                    piece = self.board.piece_at(square)
                    if piece and (piece.color == self.board.turn):
                        self.selected_square = square
                        self.valid_moves = [move for move in self.board.legal_moves if move.from_square == square]
                else:
                    move = chess.Move(self.selected_square, square)
                    if move in self.valid_moves:
                        self.board.push(move)
                    self.selected_square = None
                    self.valid_moves = []

    def main_loop(self):
        CLOCK = pygame.time.Clock()

        while not self.board.is_game_over():
            self.handle_events()
            draw_board(self.screen, self.board)
            draw_status(self.screen, self.board)
            if self.selected_square is not None:
                draw_selected_square(self.screen, self.selected_square)
                draw_valid_moves(self.screen, self.valid_moves)
            pygame.display.flip()
            CLOCK.tick(FPS)
