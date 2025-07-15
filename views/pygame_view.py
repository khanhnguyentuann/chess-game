"""
Pygame View - Handles all rendering and visual presentation of the chess game.
This module is responsible for drawing the board, pieces, UI elements, and game screens.
"""

import pygame
import sys
from typing import List
import chess
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, BOARD_SIZE, SQUARE_SIZE, STATUS_HEIGHT,
    WHITE, GREEN, DARK_GREEN, BLACK, load_images
)


class PygameView:
    """
    View class that handles all visual rendering using Pygame including:
    - Board and piece rendering
    - UI elements (status, buttons)
    - Start screen and instructions
    - Visual feedback for moves and selections
    """
    
    def __init__(self, screen: pygame.Surface):
        """
        Initialize the Pygame view.
        
        Args:
            screen: Pygame surface to render on
        """
        self.screen = screen
        self.images = load_images()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
    
    def draw_board(self, chess_board) -> None:
        """
        Draw the chess board with pieces.
        
        Args:
            chess_board: ChessBoard model instance
        """
        # Draw board squares
        colors = [pygame.Color("white"), pygame.Color("gray")]
        
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                color = colors[((row + col) % 2)]
                square_rect = pygame.Rect(
                    col * SQUARE_SIZE, 
                    row * SQUARE_SIZE, 
                    SQUARE_SIZE, 
                    SQUARE_SIZE
                )
                pygame.draw.rect(self.screen, color, square_rect)
                
                # Draw piece if present
                square_index = row * BOARD_SIZE + col
                piece = chess_board.get_piece_at(square_index)
                if piece:
                    piece_name = self._get_piece_image_name(piece)
                    if piece_name in self.images:
                        self.screen.blit(self.images[piece_name], square_rect)
    
    def draw_selected_square(self, selected_square: int) -> None:
        """
        Highlight the selected square.
        
        Args:
            selected_square: Index of the selected square
        """
        if selected_square is not None:
            row, col = selected_square // BOARD_SIZE, selected_square % BOARD_SIZE
            square_rect = pygame.Rect(
                col * SQUARE_SIZE, 
                row * SQUARE_SIZE, 
                SQUARE_SIZE, 
                SQUARE_SIZE
            )
            pygame.draw.rect(self.screen, pygame.Color("blue"), square_rect, 3)
    
    def draw_valid_moves(self, valid_moves: List[chess.Move]) -> None:
        """
        Draw indicators for valid moves.
        
        Args:
            valid_moves: List of valid moves to highlight
        """
        for move in valid_moves:
            row, col = move.to_square // BOARD_SIZE, move.to_square % BOARD_SIZE
            center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
            center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2
            pygame.draw.circle(self.screen, pygame.Color("green"), (center_x, center_y), 10)
    
    def draw_status(self, chess_board) -> None:
        """
        Draw the game status bar.
        
        Args:
            chess_board: ChessBoard model instance
        """
        status_rect = pygame.Rect(0, WINDOW_WIDTH, WINDOW_WIDTH, STATUS_HEIGHT)
        pygame.draw.rect(self.screen, WHITE, status_rect)
        
        # Current player turn
        current_player = "White" if chess_board.get_current_player() else "Black"
        status_text = f"Turn: {current_player}"
        
        # Check status
        if chess_board.is_in_check():
            status_text += " (Check!)"
        
        # Game over status
        if chess_board.is_game_over():
            game_result = chess_board.get_game_result()
            status_text = game_result if game_result else "Game Over"
        
        status_surface = self.font_medium.render(status_text, True, BLACK)
        status_position = status_rect.center
        text_rect = status_surface.get_rect(center=status_position)
        self.screen.blit(status_surface, text_rect)
    
    def show_start_screen(self) -> None:
        """Display the start screen and wait for user input."""
        running = True
        button_rect = pygame.Rect(
            WINDOW_WIDTH // 2 - 75, 
            WINDOW_HEIGHT // 2 + 20, 
            150, 
            50
        )
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button_rect.collidepoint(event.pos):
                        running = False
            
            self.screen.fill(WHITE)
            
            # Draw title
            title_text = self.font_large.render("Chess Game", True, GREEN)
            title_rect = title_text.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50)
            )
            self.screen.blit(title_text, title_rect)
            
            # Draw start button
            self._draw_button(
                "Start Game", 
                button_rect, 
                GREEN, 
                DARK_GREEN, 
                WHITE, 
                self.font_medium
            )
            
            pygame.display.flip()
    
    def show_instructions(self) -> None:
        """Display the instructions screen."""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        running = False
            
            self.screen.fill(WHITE)
            
            instructions = [
                "Welcome to Chess Game!",
                "Press SPACE to start.",
                "Use mouse to move pieces.",
                "Click on a piece to select it.",
                "Click on a highlighted square to move.",
                "Press SPACE to continue..."
            ]
            
            for i, line in enumerate(instructions):
                text = self.font_medium.render(line, True, BLACK)
                text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, 100 + i * 40))
                self.screen.blit(text, text_rect)
            
            pygame.display.flip()
    
    def show_game_over_screen(self, result: str) -> bool:
        """
        Display game over screen with result.
        
        Args:
            result: Game result string
            
        Returns:
            True if player wants to play again, False to quit
        """
        running = True
        play_again_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 50, 200, 40)
        quit_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 100, 200, 40)
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_again_rect.collidepoint(event.pos):
                        return True
                    if quit_rect.collidepoint(event.pos):
                        return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        return True
                    if event.key == pygame.K_q:
                        return False
            
            self.screen.fill(WHITE)
            
            # Draw game result
            result_text = self.font_large.render(result, True, BLACK)
            result_rect = result_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
            self.screen.blit(result_text, result_rect)
            
            # Draw buttons
            self._draw_button("Play Again (R)", play_again_rect, GREEN, DARK_GREEN, WHITE, self.font_small)
            self._draw_button("Quit (Q)", quit_rect, pygame.Color("red"), pygame.Color("darkred"), WHITE, self.font_small)
            
            pygame.display.flip()
    
    def update_display(self) -> None:
        """Update the display."""
        pygame.display.flip()
    
    def clear_screen(self) -> None:
        """Clear the screen with white background."""
        self.screen.fill(WHITE)
    
    def _get_piece_image_name(self, piece: chess.Piece) -> str:
        """
        Get the image name for a chess piece.
        
        Args:
            piece: Chess piece
            
        Returns:
            Image name string
        """
        color_char = 'w' if piece.color else 'b'
        piece_char = piece.symbol().lower()
        return f"{color_char}{piece_char}"
    
    def _draw_button(self, text: str, rect: pygame.Rect, color: pygame.Color, 
                    hover_color: pygame.Color, text_color: pygame.Color, 
                    font: pygame.font.Font) -> None:
        """
        Draw a button with hover effect.
        
        Args:
            text: Button text
            rect: Button rectangle
            color: Normal button color
            hover_color: Hover button color
            text_color: Text color
            font: Font to use
        """
        mouse_pos = pygame.mouse.get_pos()
        button_color = hover_color if rect.collidepoint(mouse_pos) else color
        
        pygame.draw.rect(self.screen, button_color, rect)
        pygame.draw.rect(self.screen, WHITE, rect, 2)
        
        text_render = font.render(text, True, text_color)
        text_rect = text_render.get_rect(center=rect.center)
        self.screen.blit(text_render, text_rect)
