"""
Chess Game UI - Pygame-based user interface
Provides a graphical interface for playing chess.
"""

import pygame
import sys
import os
from typing import Optional, Tuple, List
from pathlib import Path

# Import domain entities
from ...domain.entities.game import Game
from ...domain.entities.board import Board
from ...shared.types.enums import Player, GameState, GameResult
from ...shared.types.type_definitions import MoveRequest
from ...composition_root import get_container, reset_container


class ChessGameUI:
    """Pygame-based chess game user interface."""
    
    def __init__(self):
        """Initialize the chess game UI."""
        pygame.init()
        
        # Window settings
        self.WINDOW_WIDTH = 800
        self.WINDOW_HEIGHT = 600
        self.BOARD_SIZE = 560
        self.SQUARE_SIZE = self.BOARD_SIZE // 8
        self.BOARD_OFFSET_X = (self.WINDOW_WIDTH - self.BOARD_SIZE) // 2
        self.BOARD_OFFSET_Y = (self.WINDOW_HEIGHT - self.BOARD_SIZE) // 2
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.LIGHT_SQUARE = (240, 217, 181)
        self.DARK_SQUARE = (181, 136, 99)
        self.HIGHLIGHT = (124, 252, 0)
        self.SELECTED = (255, 255, 0)
        self.VALID_MOVE = (144, 238, 144)
        self.BACKGROUND = (50, 50, 50)
        self.TEXT_COLOR = (255, 255, 255)
        
        # Setup display
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Chess Game - Clean Architecture")
        self.clock = pygame.time.Clock()
        
        # Load piece images
        self.piece_images = self._load_piece_images()
        
        # Game state
        self.game = None
        self.selected_square = None
        self.valid_moves = []
        self.game_over = False
        self.message = ""
        self.message_timer = 0
        
        # Font
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
    
    def _load_piece_images(self) -> dict:
        """Load chess piece images."""
        images = {}
        piece_names = ['wp', 'wr', 'wn', 'wb', 'wq', 'wk', 'bp', 'br', 'bn', 'bb', 'bq', 'bk']
        
        # Get assets directory
        assets_dir = Path(__file__).parent.parent.parent.parent / "assets" / "images"
        
        for piece in piece_names:
            image_path = assets_dir / f"{piece}.png"
            if image_path.exists():
                img = pygame.image.load(str(image_path))
                img = pygame.transform.scale(img, (self.SQUARE_SIZE, self.SQUARE_SIZE))
                images[piece] = img
            else:
                # Create a placeholder if image not found
                surf = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE))
                surf.fill(self.WHITE if piece[0] == 'w' else self.BLACK)
                images[piece] = surf
        
        return images
    
    def _get_square_from_mouse(self, mouse_pos: Tuple[int, int]) -> Optional[int]:
        """Convert mouse position to chess square index."""
        x, y = mouse_pos
        
        # Check if click is within board bounds
        if (self.BOARD_OFFSET_X <= x <= self.BOARD_OFFSET_X + self.BOARD_SIZE and
            self.BOARD_OFFSET_Y <= y <= self.BOARD_OFFSET_Y + self.BOARD_SIZE):
            
            # Convert to board coordinates
            board_x = (x - self.BOARD_OFFSET_X) // self.SQUARE_SIZE
            board_y = (y - self.BOARD_OFFSET_Y) // self.SQUARE_SIZE
            
            # Convert to chess square index (0-63)
            square = board_y * 8 + board_x
            return square
        
        return None
    
    def _get_piece_symbol(self, piece) -> str:
        """Get piece symbol for image lookup."""
        if piece is None:
            return None
        
        color = 'w' if piece.color else 'b'
        piece_type = piece.piece_type
        
        piece_map = {
            1: 'p',  # pawn
            2: 'n',  # knight
            3: 'b',  # bishop
            4: 'r',  # rook
            5: 'q',  # queen
            6: 'k'   # king
        }
        
        return f"{color}{piece_map[piece_type]}"
    
    def _draw_board(self):
        """Draw the chess board."""
        for row in range(8):
            for col in range(8):
                x = self.BOARD_OFFSET_X + col * self.SQUARE_SIZE
                y = self.BOARD_OFFSET_Y + row * self.SQUARE_SIZE
                square = row * 8 + col
                
                # Determine square color
                is_light = (row + col) % 2 == 0
                color = self.LIGHT_SQUARE if is_light else self.DARK_SQUARE
                
                # Highlight selected square
                if square == self.selected_square:
                    color = self.SELECTED
                # Highlight valid moves
                elif square in [move.to_square for move in self.valid_moves]:
                    color = self.VALID_MOVE
                
                # Draw square
                pygame.draw.rect(self.screen, color, (x, y, self.SQUARE_SIZE, self.SQUARE_SIZE))
                
                # Draw piece
                piece = self.game.board.get_piece_at(square)
                if piece:
                    piece_symbol = self._get_piece_symbol(piece)
                    if piece_symbol and piece_symbol in self.piece_images:
                        self.screen.blit(self.piece_images[piece_symbol], (x, y))
    
    def _draw_ui(self):
        """Draw UI elements."""
        # Draw background
        self.screen.fill(self.BACKGROUND)
        
        # Draw board
        self._draw_board()
        
        # Draw game info
        self._draw_game_info()
        
        # Draw message
        if self.message and self.message_timer > 0:
            self._draw_message()
    
    def _draw_game_info(self):
        """Draw game information."""
        # Current player
        player_text = f"Current Player: {self.game.current_player.value.title()}"
        player_surface = self.font.render(player_text, True, self.TEXT_COLOR)
        self.screen.blit(player_surface, (10, 10))
        
        # Move count
        move_text = f"Moves: {self.game.move_count}"
        move_surface = self.small_font.render(move_text, True, self.TEXT_COLOR)
        self.screen.blit(move_surface, (10, 50))
        
        # Game state
        state_text = f"State: {self.game.state.value.title()}"
        state_surface = self.small_font.render(state_text, True, self.TEXT_COLOR)
        self.screen.blit(state_surface, (10, 70))
        
        # Instructions
        instructions = [
            "Click to select and move pieces",
            "R - Reset game",
            "U - Undo move",
            "ESC - Quit"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_surface = self.small_font.render(instruction, True, self.TEXT_COLOR)
            self.screen.blit(inst_surface, (10, self.WINDOW_HEIGHT - 100 + i * 20))
    
    def _draw_message(self):
        """Draw temporary message."""
        message_surface = self.font.render(self.message, True, self.TEXT_COLOR)
        message_rect = message_surface.get_rect(center=(self.WINDOW_WIDTH // 2, 50))
        
        # Draw background
        bg_rect = message_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, self.BLACK, bg_rect)
        pygame.draw.rect(self.screen, self.WHITE, bg_rect, 2)
        
        self.screen.blit(message_surface, message_rect)
    
    def _show_message(self, message: str, duration: int = 120):
        """Show a temporary message."""
        self.message = message
        self.message_timer = duration
    
    def _handle_mouse_click(self, mouse_pos: Tuple[int, int]):
        """Handle mouse click events."""
        square = self._get_square_from_mouse(mouse_pos)
        if square is None:
            return
        
        # If no square is selected, try to select this square
        if self.selected_square is None:
            if self.game.select_square(square):
                self.selected_square = square
                self.valid_moves = self.game.valid_moves_from_selected
                self._show_message(f"Selected square {chr(ord('a') + square % 8)}{8 - square // 8}")
            else:
                self._show_message("Invalid selection")
        
        # If a square is selected, try to make a move
        else:
            # Check if this is a valid move
            valid_move = None
            for move in self.valid_moves:
                if move.to_square == square:
                    valid_move = move
                    break
            
            if valid_move:
                # Make the move
                if self.game.make_move(square):
                    self._show_message(f"Move: {chr(ord('a') + self.selected_square % 8)}{8 - self.selected_square // 8} to {chr(ord('a') + square % 8)}{8 - square // 8}")
                    
                    # Check for game over
                    if self.game.is_game_over:
                        result = self.game.get_game_result()
                        if result == GameResult.WHITE_WINS:
                            self._show_message("Checkmate! White wins!", 300)
                        elif result == GameResult.BLACK_WINS:
                            self._show_message("Checkmate! Black wins!", 300)
                        elif result in [GameResult.DRAW_STALEMATE, GameResult.DRAW_INSUFFICIENT_MATERIAL]:
                            self._show_message("Draw!", 300)
                else:
                    self._show_message("Invalid move")
            else:
                # Try to select a different square
                if self.game.select_square(square):
                    self.selected_square = square
                    self.valid_moves = self.game.valid_moves_from_selected
                    self._show_message(f"Selected square {chr(ord('a') + square % 8)}{8 - square // 8}")
                else:
                    self._show_message("Invalid selection")
    
    def _handle_key_press(self, key):
        """Handle keyboard events."""
        if key == pygame.K_r:  # Reset game
            self.game.reset_game()
            self.selected_square = None
            self.valid_moves = []
            self._show_message("Game reset")
        
        elif key == pygame.K_u:  # Undo move
            if self.game.undo_last_move():
                self.selected_square = None
                self.valid_moves = []
                self._show_message("Move undone")
            else:
                self._show_message("No moves to undo")
        
        elif key == pygame.K_ESCAPE:  # Return to menu
            return "menu"  # Signal to return to menu
    
    def run(self):
        """Main game loop."""
        # Initialize game if not provided
        if self.game is None:
            board = Board()
            self.game = Game(
                white_player="Player 1",
                black_player="Player 2",
                board=board
            )
        
        running = True
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self._handle_mouse_click(event.pos)
                
                elif event.type == pygame.KEYDOWN:
                    result = self._handle_key_press(event.key)
                    if result == "menu":
                        running = False
                        return "menu"  # Signal to return to menu
            
            # Update message timer
            if self.message_timer > 0:
                self.message_timer -= 1
            
            # Draw everything
            self._draw_ui()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(60)
        
        # Cleanup
        pygame.quit()
        reset_container()


def main():
    """Main function to run the chess game UI."""
    try:
        ui = ChessGameUI()
        ui.run()
    except Exception as e:
        print(f"Error running chess game UI: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
