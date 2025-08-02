"""
Modern Chess Game UI - Enhanced version with beautiful design
Clean architecture with component-based system and animations.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple

import pygame

from ...composition_root import get_container, reset_container
from ...domain.entities.board import Board
from ...domain.entities.game import Game
from ...shared.types.enums import GameResult, GameState, Player, UIColors
from ...shared.types.type_definitions import MoveRequest
from ...shared.utils.save_manager import save_manager
from .animations import animation_system, animate, animate_to, EasingType
from .components.button import Button, IconButton, ToggleButton
from .components.panel import InfoPanel, Panel
from .piece_renderer import PieceRenderer
from .themes import theme_manager


class ModernChessUI:
    """Modern chess game UI with beautiful design and smooth animations."""

    def __init__(self):
        if not pygame.get_init():
            pygame.init()

        # Get current theme
        self.theme = theme_manager.get_current_theme()
        
        # Layout constants
        self.SIDEBAR_WIDTH = 300
        self.BOARD_SIZE = 640
        self.WINDOW_WIDTH = self.BOARD_SIZE + self.SIDEBAR_WIDTH + 40
        self.WINDOW_HEIGHT = max(self.BOARD_SIZE + 100, 700)
        
        # Board layout
        self.SQUARE_SIZE = self.BOARD_SIZE // 8
        self.BOARD_OFFSET_X = 20
        self.BOARD_OFFSET_Y = (self.WINDOW_HEIGHT - self.BOARD_SIZE) // 2
        
        # Setup display
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Chess Game - Modern UI")
        
        self.clock = pygame.time.Clock()
        
        # Initialize piece renderer
        self.piece_renderer = PieceRenderer(self.SQUARE_SIZE)
        
        # Game state
        self.game = None
        self.selected_square = None
        self.valid_moves = []
        self.last_move = None
        self.game_over = False
        
        # Animation properties
        self.board_animation_offset = 0.0
        self.piece_animations = {}
        
        # UI Components
        self._create_ui_components()
        
        # Fonts
        self.title_font = pygame.font.Font(None, 32)
        self.info_font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 16)
        
        # Modal state
        self.show_quit_dialog = False
        self.show_settings = False
        
    def _create_ui_components(self) -> None:
        """Create all UI components."""
        sidebar_x = self.BOARD_OFFSET_X + self.BOARD_SIZE + 20
        
        # Info Panel
        self.info_panel = InfoPanel(
            sidebar_x, 20, self.SIDEBAR_WIDTH - 20, 200
        )
        
        # Control Panel
        self.control_panel = Panel(
            sidebar_x, 240, self.SIDEBAR_WIDTH - 20, 180, "Game Controls"
        )
        
        # Buttons
        button_width = (self.SIDEBAR_WIDTH - 60) // 2
        button_height = 40
        
        self.new_game_btn = Button(
            sidebar_x + 15, 280, button_width, button_height,
            "New Game", self._on_new_game
        )
        
        self.undo_btn = Button(
            sidebar_x + 15 + button_width + 10, 280, button_width, button_height,
            "Undo", self._on_undo
        )
        
        self.save_btn = Button(
            sidebar_x + 15, 330, button_width, button_height,
            "Save", self._on_save_game
        )
        
        self.settings_btn = Button(
            sidebar_x + 15 + button_width + 10, 330, button_width, button_height,
            "Settings", self._on_settings
        )
        
        self.quit_btn = Button(
            sidebar_x + 15, 380, self.SIDEBAR_WIDTH - 50, button_height,
            "Quit to Menu", self._on_quit
        )
        
        # Theme selector
        self.theme_panel = Panel(
            sidebar_x, 440, self.SIDEBAR_WIDTH - 20, 120, "Theme"
        )
        
        theme_btn_width = (self.SIDEBAR_WIDTH - 80) // 3
        themes = theme_manager.list_themes()
        
        self.theme_buttons = []
        for i, theme_name in enumerate(themes):
            btn = ToggleButton(
                sidebar_x + 15 + i * (theme_btn_width + 10), 480,
                theme_btn_width, 30, theme_name.title(),
                callback=lambda t=theme_name: self._on_theme_change(t)
            )
            if theme_name == theme_manager.get_current_theme().name:
                btn.toggled = True
            self.theme_buttons.append(btn)
        
        # Add buttons to panels
        self.control_panel.add_child(self.new_game_btn)
        self.control_panel.add_child(self.undo_btn)
        self.control_panel.add_child(self.save_btn)
        self.control_panel.add_child(self.settings_btn)
        self.control_panel.add_child(self.quit_btn)
        
        for btn in self.theme_buttons:
            self.theme_panel.add_child(btn)
        
        # All panels
        self.panels = [self.info_panel, self.control_panel, self.theme_panel]
        
        # Animate panels in
        for i, panel in enumerate(self.panels):
            panel.rect.x += 300  # Start off-screen
            animate(panel.rect, 'x', sidebar_x, 0.8 + i * 0.1, easing=EasingType.EASE_OUT, delay=i * 0.1)
    
    def _on_new_game(self) -> None:
        """Handle new game button."""
        if self.game:
            self.game.reset_game()
            self.selected_square = None
            self.valid_moves = []
            self.last_move = None
            self._animate_board_reset()
    
    def _on_undo(self) -> None:
        """Handle undo button."""
        if self.game and self.game.undo_last_move():
            self.selected_square = None
            self.valid_moves = []
            self._animate_piece_return()
    
    def _on_save_game(self) -> None:
        """Handle save game button."""
        if self.game:
            data = self.game.to_dict()
            if save_manager.save_game(data):
                self._show_notification("Game saved successfully!", (40, 167, 69))
            else:
                self._show_notification("Failed to save game!", (220, 53, 69))
    
    def _on_settings(self) -> None:
        """Handle settings button."""
        self.show_settings = not self.show_settings
    
    def _on_quit(self) -> None:
        """Handle quit button."""
        self.show_quit_dialog = True
    
    def _on_theme_change(self, theme_name: str) -> None:
        """Handle theme change."""
        if theme_manager.set_theme(theme_name):
            self.theme = theme_manager.get_current_theme()
            
            # Update button states
            for btn in self.theme_buttons:
                btn.toggled = (btn.text.lower() == theme_name)
            
            # Animate theme change
            self._animate_theme_change()
    
    def _animate_board_reset(self) -> None:
        """Animate board reset."""
        animate(self, 'board_animation_offset', 20.0, 0.3, easing=EasingType.BOUNCE)
        animate(self, 'board_animation_offset', 0.0, 0.3, delay=0.3, easing=EasingType.EASE_OUT)
    
    def _animate_piece_return(self) -> None:
        """Animate piece returning after undo."""
        # Simple shake animation
        animate(self, 'board_animation_offset', -10.0, 0.1, easing=EasingType.EASE_OUT)
        animate(self, 'board_animation_offset', 10.0, 0.1, delay=0.1, easing=EasingType.EASE_OUT)
        animate(self, 'board_animation_offset', 0.0, 0.1, delay=0.2, easing=EasingType.EASE_OUT)
    
    def _animate_theme_change(self) -> None:
        """Animate theme change."""
        # Animate all panels
        for panel in self.panels:
            original_y = panel.rect.y
            animate(panel.rect, 'y', original_y - 20, 0.2, easing=EasingType.EASE_OUT)
            animate(panel.rect, 'y', original_y, 0.2, delay=0.2, easing=EasingType.BOUNCE)
    
    def _show_notification(self, message: str, color: Tuple[int, int, int]) -> None:
        """Show a notification message."""
        # This would be implemented with a notification system
        print(f"Notification: {message}")
    
    def _get_square_from_mouse(self, mouse_pos: Tuple[int, int]) -> Optional[int]:
        """Convert mouse position to chess square index."""
        x, y = mouse_pos
        
        board_x = self.BOARD_OFFSET_X + self.board_animation_offset
        board_y = self.BOARD_OFFSET_Y
        
        if (board_x <= x <= board_x + self.BOARD_SIZE and 
            board_y <= y <= board_y + self.BOARD_SIZE):
            
            col = int((x - board_x) // self.SQUARE_SIZE)
            row = int((y - board_y) // self.SQUARE_SIZE)
            
            if 0 <= col < 8 and 0 <= row < 8:
                return row * 8 + col
        
        return None
    
    def _handle_board_click(self, square: int) -> None:
        """Handle click on chess board."""
        if not self.game or self.game.is_game_over:
            return
        
        if self.selected_square is None:
            # Select piece
            if self.game.select_square(square):
                self.selected_square = square
                self.valid_moves = self.game.valid_moves_from_selected
                self._animate_square_selection(square)
        else:
            # Try to make move
            if square in [move.to_square for move in self.valid_moves]:
                # Find the matching move
                move = next((m for m in self.valid_moves if m.to_square == square), None)
                if move and self.game.make_move(square, move.promotion):
                    self.last_move = (self.selected_square, square)
                    self._animate_piece_move(self.selected_square, square)
                    self.selected_square = None
                    self.valid_moves = []
                    
                    # Check for game over
                    if self.game.is_game_over:
                        self._animate_game_over()
            else:
                # Try to select different piece
                if self.game.select_square(square):
                    self.selected_square = square
                    self.valid_moves = self.game.valid_moves_from_selected
                    self._animate_square_selection(square)
                else:
                    self.selected_square = None
                    self.valid_moves = []
    
    def _animate_square_selection(self, square: int) -> None:
        """Animate square selection."""
        # Add a subtle pulse animation to the selected square
        pass
    
    def _animate_piece_move(self, from_square: int, to_square: int) -> None:
        """Animate piece movement."""
        # This would implement smooth piece movement animation
        pass
    
    def _animate_game_over(self) -> None:
        """Animate game over state."""
        # Animate board slightly to indicate game over
        animate(self, 'board_animation_offset', 5.0, 0.5, easing=EasingType.EASE_IN_OUT)
        animate(self, 'board_animation_offset', -5.0, 0.5, delay=0.5, easing=EasingType.EASE_IN_OUT)
        animate(self, 'board_animation_offset', 0.0, 0.5, delay=1.0, easing=EasingType.EASE_OUT)
    
    def _draw_board(self) -> None:
        """Draw the chess board with modern styling."""
        board_x = self.BOARD_OFFSET_X + self.board_animation_offset
        board_y = self.BOARD_OFFSET_Y
        
        # Draw board shadow
        shadow_offset = 8
        shadow_rect = pygame.Rect(
            board_x + shadow_offset, 
            board_y + shadow_offset, 
            self.BOARD_SIZE, 
            self.BOARD_SIZE
        )
        shadow_surface = pygame.Surface((self.BOARD_SIZE, self.BOARD_SIZE), pygame.SRCALPHA)
        shadow_surface.fill(self.theme.get_color('shadow'))
        self.screen.blit(shadow_surface, shadow_rect.topleft)
        
        # Draw board border
        border_rect = pygame.Rect(board_x - 4, board_y - 4, self.BOARD_SIZE + 8, self.BOARD_SIZE + 8)
        pygame.draw.rect(self.screen, self.theme.get_color('border'), border_rect)
        pygame.draw.rect(self.screen, self.theme.get_color('surface'), border_rect, 2)
        
        # Draw squares
        for row in range(8):
            for col in range(8):
                x = board_x + col * self.SQUARE_SIZE
                y = board_y + row * self.SQUARE_SIZE
                square = row * 8 + col
                
                # Determine square color
                is_light = (row + col) % 2 == 0
                base_color = (self.theme.get_color('light_square') if is_light 
                             else self.theme.get_color('dark_square'))
                
                # Apply overlays
                color = base_color
                overlay_alpha = 0
                
                # Last move highlight
                if self.last_move and square in self.last_move:
                    overlay_color = self.theme.get_color('last_move')
                    overlay_alpha = 100
                
                # Selected square
                elif square == self.selected_square:
                    overlay_color = self.theme.get_color('selected')
                    overlay_alpha = 180
                
                # Valid move squares
                elif square in [move.to_square for move in self.valid_moves]:
                    overlay_color = self.theme.get_color('valid_move')
                    overlay_alpha = 120
                
                # Draw base square
                pygame.draw.rect(self.screen, color, (x, y, self.SQUARE_SIZE, self.SQUARE_SIZE))
                
                # Draw overlay if needed
                if overlay_alpha > 0:
                    overlay_surface = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)
                    overlay_surface.fill((*overlay_color[:3], overlay_alpha))
                    self.screen.blit(overlay_surface, (x, y))
                
                # Draw piece
                if self.game:
                    piece = self.game.board.get_piece_at(square)
                    if piece:
                        piece_symbol = self._get_piece_symbol(piece)
                        if piece_symbol:
                            piece_surface = self.piece_renderer.get_piece_surface(piece_symbol)
                            self.screen.blit(piece_surface, (x, y))
        
        # Draw coordinates
        self._draw_coordinates(board_x, board_y)
    
    def _draw_coordinates(self, board_x: int, board_y: int) -> None:
        """Draw board coordinates."""
        coord_font = pygame.font.Font(None, 16)
        coord_color = self.theme.get_color('on_surface')
        
        # Files (a-h)
        for col in range(8):
            letter = chr(ord('a') + col)
            text = coord_font.render(letter, True, coord_color)
            x = board_x + col * self.SQUARE_SIZE + self.SQUARE_SIZE - 15
            y = board_y + self.BOARD_SIZE + 5
            self.screen.blit(text, (x, y))
        
        # Ranks (1-8)
        for row in range(8):
            number = str(8 - row)
            text = coord_font.render(number, True, coord_color)
            x = board_x - 20
            y = board_y + row * self.SQUARE_SIZE + 5
            self.screen.blit(text, (x, y))
    
    def _get_piece_symbol(self, piece) -> str:
        """Get piece symbol for rendering."""
        if piece is None:
            return None
        
        color = "w" if piece.color else "b"
        piece_type = piece.piece_type
        
        piece_map = {1: "p", 2: "n", 3: "b", 4: "r", 5: "q", 6: "k"}
        return f"{color}{piece_map[piece_type]}"
    
    def _update_info_panel(self) -> None:
        """Update the information panel."""
        if not self.game:
            return
        
        self.info_panel.set_info("Current Player", self.game.current_player.value.title())
        self.info_panel.set_info("Move Count", str(self.game.move_count))
        
        if self.selected_square is not None:
            col = chr(ord('a') + self.selected_square % 8)
            row = str(8 - self.selected_square // 8)
            self.info_panel.set_info("Selected", f"{col}{row}")
        else:
            self.info_panel.set_info("Selected", "None")
        
        if self.game.board.is_in_check():
            self.info_panel.set_info("Status", "CHECK!")
        elif self.game.is_game_over:
            result = self.game.get_game_result()
            if result == GameResult.WHITE_WINS:
                self.info_panel.set_info("Status", "White Wins!")
            elif result == GameResult.BLACK_WINS:
                self.info_panel.set_info("Status", "Black Wins!")
            else:
                self.info_panel.set_info("Status", "Draw")
        else:
            self.info_panel.set_info("Status", "Playing")
    
    def _draw_quit_dialog(self) -> None:
        """Draw quit confirmation dialog."""
        if not self.show_quit_dialog:
            return
        
        # Semi-transparent overlay
        overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # Dialog box
        dialog_width = 400
        dialog_height = 200
        dialog_x = (self.WINDOW_WIDTH - dialog_width) // 2
        dialog_y = (self.WINDOW_HEIGHT - dialog_height) // 2
        
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        pygame.draw.rect(self.screen, self.theme.get_color('surface'), dialog_rect)
        pygame.draw.rect(self.screen, self.theme.get_color('border'), dialog_rect, 2)
        
        # Dialog text
        title_text = self.title_font.render("Quit Game", True, self.theme.get_color('on_surface'))
        title_rect = title_text.get_rect(center=(dialog_x + dialog_width // 2, dialog_y + 40))
        self.screen.blit(title_text, title_rect)
        
        message_text = self.info_font.render("Save your game before quitting?", True, self.theme.get_color('on_surface'))
        message_rect = message_text.get_rect(center=(dialog_x + dialog_width // 2, dialog_y + 80))
        self.screen.blit(message_text, message_rect)
        
        # Buttons
        button_width = 120
        button_height = 40
        button_y = dialog_y + dialog_height - 60
        
        continue_rect = pygame.Rect(dialog_x + 40, button_y, button_width, button_height)
        save_rect = pygame.Rect(dialog_x + dialog_width - 160, button_y, button_width, button_height)
        
        # Draw buttons
        pygame.draw.rect(self.screen, self.theme.get_color('secondary'), continue_rect)
        pygame.draw.rect(self.screen, self.theme.get_color('primary'), save_rect)
        
        continue_text = self.info_font.render("Continue", True, self.theme.get_color('on_surface'))
        continue_text_rect = continue_text.get_rect(center=continue_rect.center)
        self.screen.blit(continue_text, continue_text_rect)
        
        save_text = self.info_font.render("Save & Quit", True, UIColors.WHITE)
        save_text_rect = save_text.get_rect(center=save_rect.center)
        self.screen.blit(save_text, save_text_rect)
        
        # Store rects for click detection
        self.quit_dialog_continue_rect = continue_rect
        self.quit_dialog_save_rect = save_rect
    
    def _handle_quit_dialog_click(self, pos: Tuple[int, int]) -> Optional[str]:
        """Handle quit dialog clicks."""
        if hasattr(self, 'quit_dialog_continue_rect') and self.quit_dialog_continue_rect.collidepoint(pos):
            self.show_quit_dialog = False
            return None
        elif hasattr(self, 'quit_dialog_save_rect') and self.quit_dialog_save_rect.collidepoint(pos):
            if self.game:
                data = self.game.to_dict()
                save_manager.save_game(data)
            return "menu"
        return None
    
    def update(self, dt: float) -> None:
        """Update UI state."""
        # Update animation system
        animation_system.update(dt)
        
        # Update components
        for panel in self.panels:
            panel.update(dt)
        
        # Update info panel
        self._update_info_panel()
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Handle pygame events."""
        # Handle quit dialog first
        if self.show_quit_dialog:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                result = self._handle_quit_dialog_click(event.pos)
                if result:
                    return result
            return None
        
        # Handle UI components
        for panel in self.panels:
            if panel.handle_event(event):
                return None
        
        # Handle board clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            square = self._get_square_from_mouse(event.pos)
            if square is not None:
                self._handle_board_click(square)
        
        # Handle keyboard
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "menu"
        
        return None
    
    def render(self) -> None:
        """Render the entire UI."""
        # Clear screen with background color
        self.screen.fill(self.theme.get_color('background'))
        
        # Draw chess board
        self._draw_board()
        
        # Draw UI panels
        for panel in self.panels:
            panel.render(self.screen)
        
        # Draw dialogs
        self._draw_quit_dialog()
        
        # Update display
        pygame.display.flip()
    
    def run(self) -> str:
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
            dt = self.clock.tick(60) / 1000.0  # Delta time in seconds
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return "quit"
                
                result = self.handle_event(event)
                if result:
                    return result
            
            # Update
            self.update(dt)
            
            # Render
            self.render()
        
        return "quit"


def main():
    """Main function to run the modern chess UI."""
    try:
        ui = ModernChessUI()
        return ui.run()
    except Exception as e:
        print(f"Error running modern chess UI: {e}")
        import traceback
        traceback.print_exc()
        return "quit"


if __name__ == "__main__":
    main()