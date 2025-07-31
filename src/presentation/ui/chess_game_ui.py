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
from .piece_renderer import PieceRenderer


class ChessGameUI:
    """Pygame-based chess game user interface."""
    
    def __init__(self):
        if not pygame.get_init():
            pygame.init()
        
        # --- Layout constants ---
        # Reserve space for a top information panel and a bottom button panel.
        # The central area contains the chess board.
        self.INFO_PANEL_HEIGHT = 90
        self.BUTTON_PANEL_HEIGHT = 60
        self.BOARD_SIZE = 560
        self.WINDOW_WIDTH = 900
        self.WINDOW_HEIGHT = self.INFO_PANEL_HEIGHT + self.BOARD_SIZE + self.BUTTON_PANEL_HEIGHT + 20

        # Size of individual squares
        self.SQUARE_SIZE = self.BOARD_SIZE // 8

        # Offsets for board drawing
        self.BOARD_OFFSET_X = (self.WINDOW_WIDTH - self.BOARD_SIZE) // 2
        self.BOARD_OFFSET_Y = self.INFO_PANEL_HEIGHT
        
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
        
        # Initialize piece renderer
        self.piece_renderer = PieceRenderer(self.SQUARE_SIZE)
        
        # Game state
        self.game = None
        self.selected_square = None
        self.valid_moves = []
        self.game_over = False
        self.message = ""
        self.message_timer = 0
        # For displaying last move and selection in the info panel
        self.last_move_text = ""

        # Quit dialog state
        self.show_quit_dialog = False
        self.quit_dialog_buttons = {
            "save": pygame.Rect(self.WINDOW_WIDTH // 2 - 140, self.WINDOW_HEIGHT // 2 + 30, 120, 40),
            "quit": pygame.Rect(self.WINDOW_WIDTH // 2 + 20,  self.WINDOW_HEIGHT // 2 + 30, 120, 40)
        }
        
        # Font
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Button definitions (reset, undo, quit).  They live in the bottom panel.
        self.BUTTON_WIDTH = 120
        self.BUTTON_HEIGHT = 40
        self.reset_button_rect = pygame.Rect(
            50,
            self.WINDOW_HEIGHT - self.BUTTON_PANEL_HEIGHT + 10,
            self.BUTTON_WIDTH,
            self.BUTTON_HEIGHT,
        )
        self.undo_button_rect = pygame.Rect(
            50 + self.BUTTON_WIDTH + 30,
            self.WINDOW_HEIGHT - self.BUTTON_PANEL_HEIGHT + 10,
            self.BUTTON_WIDTH,
            self.BUTTON_HEIGHT,
        )
        self.quit_button_rect = pygame.Rect(
            50 + 2 * (self.BUTTON_WIDTH + 30),
            self.WINDOW_HEIGHT - self.BUTTON_PANEL_HEIGHT + 10,
            self.BUTTON_WIDTH,
            self.BUTTON_HEIGHT,
        )
        self.buttons = [
            (self.reset_button_rect, "Reset"),
            (self.undo_button_rect, "Undo"),
            (self.quit_button_rect, "Quit"),
        ]
    
    def _get_piece_surface(self, piece_code: str) -> pygame.Surface:
        return self.piece_renderer.get_piece_surface(piece_code)
    
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
        """Draw the chess board inside its allocated region."""
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
                    if piece_symbol:
                        piece_surface = self._get_piece_surface(piece_symbol)
                        self.screen.blit(piece_surface, (x, y))
    
    def _draw_ui(self):
        """Draw UI elements."""
        # Fill the window
        self.screen.fill(self.BACKGROUND)

        # Draw the information panel at the top
        self._draw_info_panel()

        # Draw the board
        self._draw_board()

        # Draw the buttons at the bottom
        self._draw_buttons()

        # Draw message overlay if needed
        if self.message and self.message_timer > 0:
            self._draw_message()

            # Draw quit confirmation dialog if active
        if self.show_quit_dialog:
            self._draw_quit_dialog()

    def _draw_quit_dialog(self):
        """Render the quit confirmation popup."""
        # Semi‑transparent overlay
        overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        # Dialog box
        box_rect = pygame.Rect(self.WINDOW_WIDTH // 2 - 200, self.WINDOW_HEIGHT // 2 - 80, 400, 150)
        pygame.draw.rect(self.screen, (60, 60, 60), box_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), box_rect, 2)
        # Message
        msg = "Do you want to save your current game before quitting?"
        text_surf = self.small_font.render(msg, True, self.TEXT_COLOR)
        text_rect = text_surf.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 - 20))
        self.screen.blit(text_surf, text_rect)
        # Buttons
        for key, rect in self.quit_dialog_buttons.items():
            pygame.draw.rect(self.screen, (80, 80, 80), rect)
            pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)
            label = "Save and Quit" if key == "save" else "Quit"
            surf = self.small_font.render(label, True, self.TEXT_COLOR)
            surf_rect = surf.get_rect(center=rect.center)
            self.screen.blit(surf, surf_rect)
    
    def _draw_info_panel(self):
        """Draw the top information panel (current player, selection, last move)."""
        panel_rect = pygame.Rect(0, 0, self.WINDOW_WIDTH, self.INFO_PANEL_HEIGHT)
        pygame.draw.rect(self.screen, (40, 40, 40), panel_rect)

        # Current player
        cp_text = f"Current player: {self.game.current_player.value.title()}"
        cp_surface = self.font.render(cp_text, True, self.TEXT_COLOR)
        self.screen.blit(cp_surface, (20, 10))

        # Selected square (if any)
        sel_text = "Selected square: "
        if self.selected_square is not None:
            col = chr(ord('a') + self.selected_square % 8)
            row = str(8 - self.selected_square // 8)
            sel_text += f"{col}{row}"
        else:
            sel_text += "–"
        sel_surface = self.small_font.render(sel_text, True, self.TEXT_COLOR)
        self.screen.blit(sel_surface, (20, 50))

        # Last move (if any)
        lm_text = f"Last move: {self.last_move_text or '–'}"
        lm_surface = self.small_font.render(lm_text, True, self.TEXT_COLOR)
        self.screen.blit(lm_surface, (20, 70))

    def _draw_buttons(self):
        """Draw the reset/undo/quit buttons."""
        for rect, label in self.buttons:
            # Draw the button rectangle
            pygame.draw.rect(self.screen, (80, 80, 80), rect)
            pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)

            # Centre the text on the button
            text_surface = self.small_font.render(label, True, self.TEXT_COLOR)
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)
    
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
        # If a quit dialog is shown, handle its buttons separately
        if self.show_quit_dialog:
            # Save and Quit button
            if self.quit_dialog_buttons["save"].collidepoint(mouse_pos):
                self._save_game_and_return_to_menu()
                return
            # Quit without saving
            elif self.quit_dialog_buttons["quit"].collidepoint(mouse_pos):
                self._discard_save_and_return_to_menu()
                return
            # Click elsewhere cancels the dialog
            self.show_quit_dialog = False
            return
        
        # First check if the user clicked on a button (bottom panel)
        if self.reset_button_rect.collidepoint(mouse_pos):
            # Reset game button
            self.game.reset_game()
            self.selected_square = None
            self.valid_moves = []
            self.last_move_text = ""
            self._show_message("Game reset")
            return
        elif self.undo_button_rect.collidepoint(mouse_pos):
            # Undo button
            if self.game.undo_last_move():
                self.selected_square = None
                self.valid_moves = []
                self.last_move_text = ""  # Could derive from move history
                self._show_message("Move undone")
            else:
                self._show_message("No moves to undo")
            return
        elif self.quit_button_rect.collidepoint(mouse_pos):
            # Quit button: return to menu
            self.show_quit_dialog = True
            return

        # Otherwise handle a click on the board
        square = self._get_square_from_mouse(mouse_pos)
        if square is None:
            return
        
        # If no square is selected, try to select this square
        if self.selected_square is None:
            if self.game.select_square(square):
                self.selected_square = square
                self.valid_moves = self.game.valid_moves_from_selected
                # Update the info panel instead of showing a transient message
                self._show_message("")  # Clear any previous message
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
                # Check if this is a pawn promotion move
                promotion = None
                if valid_move.promotion:
                    # Auto-promote to queen (piece type 5)
                    promotion = 5
                
                # Make the move
                if self.game.make_move(square, promotion):
                    # Compose human‑readable move text for info panel
                    move_algebraic = f"{chr(ord('a') + self.selected_square % 8)}{8 - self.selected_square // 8} → {chr(ord('a') + square % 8)}{8 - square // 8}"
                    if promotion:
                        move_algebraic += " (Q)"
                    self.last_move_text = move_algebraic

                    # Clear selection and valid moves
                    self.selected_square = None
                    self.valid_moves = []
                    self._show_message("")  # Clear any previous message
                    
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
        # Keyboard controls are no longer needed; players use on‑screen buttons.
        if key == pygame.K_ESCAPE:
            return "menu"
        
    def _save_game_and_return_to_menu(self):
        """Serialize the current game and exit to the menu."""
        import json, os
        data = self.game.to_dict()
        # File is placed in the project root; adjust path as needed
        with open("saved_game.json", "w", encoding="utf-8") as f:
            json.dump(data, f)
        # Signal the run loop to exit and go back to the menu
        self.game_over = True  # or set a custom flag

    def _discard_save_and_return_to_menu(self):
        """Delete any existing save and exit to the menu."""
        import os
        try:
            os.remove("saved_game.json")
        except FileNotFoundError:
            pass
        self.game_over = True
    
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
