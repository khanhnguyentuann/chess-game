"""
Menu System for Chess Game
Provides menu interface with game options.
"""

import pygame
import sys
import os
from typing import Optional, List, Tuple
from pathlib import Path
from enum import Enum

# Import domain entities
from ...domain.entities.game import Game
from ...domain.entities.board import Board
from ...shared.types.enums import Player, GameState, GameResult
from ...composition_root import get_container, reset_container
from ...shared.utils.save_manager import save_manager


class MenuState(Enum):
    """Menu states."""
    MAIN_MENU = "main_menu"
    GAME_PLAYING = "game_playing"
    HELP = "help"
    LOAD_GAME = "load_game"


class MenuItem:
    """Represents a menu item."""
    
    def __init__(self, text: str, action: str, enabled: bool = True):
        self.text = text
        self.action = action
        self.enabled = enabled
        self.rect = None  # Will be set when drawing


class MenuSystem:
    """Menu system for the chess game."""
    
    def __init__(self):
        """Initialize the menu system."""
        # Only initialize pygame if not already initialized
        if not pygame.get_init():
            pygame.init()
        
        # Window settings
        self.WINDOW_WIDTH = 800
        self.WINDOW_HEIGHT = 600
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (128, 128, 128)
        self.DARK_GRAY = (64, 64, 64)
        self.BLUE = (0, 100, 200)
        self.LIGHT_BLUE = (100, 150, 255)
        self.RED = (200, 50, 50)
        self.GREEN = (50, 200, 50)
        self.BACKGROUND = (30, 30, 30)
        self.MENU_BG = (50, 50, 50)
        
        # Setup display
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Chess Game - Menu")
        
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.title_font = pygame.font.Font(None, 72)
        self.menu_font = pygame.font.Font(None, 48)
        self.help_font = pygame.font.Font(None, 24)
        
        # Menu state
        self.current_state = MenuState.MAIN_MENU
        self.selected_item = 0
        
        # Game state
        self.game = None
        self.saved_games = []
        
        # Load saved games
        self._load_saved_games()
    
    def _load_saved_games(self):
        """Load saved games from storage."""
        self.saved_games = []
        
        # Use save manager to get save file info
        save_info = save_manager.get_save_info()
        if save_info:
            game_name = f"Game {save_info['game_id'][:8]}"
            moves = save_info['move_count']
            modified_date = save_info['modified_at'][:10]  # Just the date part
            
            self.saved_games.append({
                "name": game_name, 
                "date": modified_date, 
                "moves": moves,
                "filename": save_info['filename']
            })
    
    def _get_main_menu_items(self) -> List[MenuItem]:
        """Get main menu items."""
        return [
            MenuItem("New Game", "new_game"),
            MenuItem("Continue Game", "continue_game", bool(self.saved_games)),
            MenuItem("Help", "help"),
            MenuItem("Quit", "quit")
        ]
    
    def _get_help_text(self) -> List[str]:
        """Get help text."""
        return [
            "CHESS GAME HELP",
            "",
            "HOW TO PLAY:",
            "- Click on a piece to select it",
            "- Click on a valid square to move",
            "- Valid moves are highlighted in green",
            "- Selected piece is highlighted in yellow",
            "",
            "GAME CONTROLS:",
            "- R: Reset the game",
            "- U: Undo last move",
            "- ESC: Return to menu",
            "",
            "GAME RULES:",
            "- White moves first",
            "- Pawns move forward one square",
            "- Knights move in L-shape",
            "- Bishops move diagonally",
            "- Rooks move horizontally and vertically",
            "- Queens move in any direction",
            "- Kings move one square in any direction",
            "",
            "- Checkmate: King is in check with no escape",
            "- Stalemate: No legal moves but not in check",
            "- Draw: Insufficient material, repetition, or 50-move rule",
            "",
            "Press ESC to return to main menu"
        ]
    
    def _draw_title(self):
        """Draw the game title."""
        title_surface = self.title_font.render("CHESS GAME", True, self.WHITE)
        title_rect = title_surface.get_rect(center=(self.WINDOW_WIDTH // 2, 100))
        self.screen.blit(title_surface, title_rect)
    
    def _draw_menu_items(self, items: List[MenuItem], start_y: int = 200):
        """Draw menu items."""
        for i, item in enumerate(items):
            color = self.WHITE if item.enabled else self.GRAY
            if i == self.selected_item and item.enabled:
                color = self.LIGHT_BLUE
            
            text_surface = self.menu_font.render(item.text, True, color)
            text_rect = text_surface.get_rect(center=(self.WINDOW_WIDTH // 2, start_y + i * 60))
            
            # Store rect for click detection
            item.rect = text_rect
            
            self.screen.blit(text_surface, text_rect)
    
    def _draw_help_screen(self):
        """Draw help screen."""
        help_text = self._get_help_text()
        
        y_offset = 50
        for line in help_text:
            if line == "":
                y_offset += 20
                continue
            
            if line == "CHESS GAME HELP":
                font = self.menu_font
                color = self.BLUE
            elif line in ["HOW TO PLAY:", "GAME CONTROLS:", "GAME RULES:"]:
                font = self.menu_font
                color = self.GREEN
            else:
                font = self.help_font
                color = self.WHITE
            
            text_surface = font.render(line, True, color)
            text_rect = text_surface.get_rect(center=(self.WINDOW_WIDTH // 2, y_offset))
            self.screen.blit(text_surface, text_rect)
            y_offset += 30
    
    def _draw_main_menu(self):
        """Draw main menu."""
        # Draw background
        self.screen.fill(self.BACKGROUND)
        
        # Draw title
        self._draw_title()
        
        # Draw menu items
        menu_items = self._get_main_menu_items()
        self._draw_menu_items(menu_items)
        
        # Draw version info
        version_text = "v1.0 - Clean Architecture"
        version_surface = self.help_font.render(version_text, True, self.GRAY)
        version_rect = version_surface.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT - 30))
        self.screen.blit(version_surface, version_rect)
    
    def _draw_help_menu(self):
        """Draw help menu."""
        # Draw background
        self.screen.fill(self.BACKGROUND)
        
        # Draw help content
        self._draw_help_screen()
    
    def _handle_menu_navigation(self, key):
        """Handle menu navigation."""
        if self.current_state == MenuState.MAIN_MENU:
            menu_items = self._get_main_menu_items()
            enabled_items = [i for i, item in enumerate(menu_items) if item.enabled]
            
            if key == pygame.K_UP:
                current_index = enabled_items.index(self.selected_item)
                self.selected_item = enabled_items[(current_index - 1) % len(enabled_items)]
            elif key == pygame.K_DOWN:
                current_index = enabled_items.index(self.selected_item)
                self.selected_item = enabled_items[(current_index + 1) % len(enabled_items)]
            elif key == pygame.K_RETURN:
                self._execute_menu_action(menu_items[self.selected_item].action)
    
    def _execute_menu_action(self, action: str):
        """Execute menu action."""
        if action == "new_game":
            self._start_new_game()
        elif action == "continue_game":
            self._continue_game()
        elif action == "help":
            self.current_state = MenuState.HELP
        elif action == "quit":
            pygame.quit()
            sys.exit(0)
    
    def _start_new_game(self):
        """Start a new game."""
        # Create new game
        board = Board()
        self.game = Game(
            white_player="Player 1",
            black_player="Player 2",
            board=board
        )
        
        # Switch to game state
        self.current_state = MenuState.GAME_PLAYING
        
        # Import and start game UI
        from .chess_game_ui import ChessGameUI
        game_ui = ChessGameUI()
        game_ui.game = self.game
        result = game_ui.run()
        
        # Reset window size to menu size when returning
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Chess Game - Menu")
        
        # Return to menu when game ends
        self.current_state = MenuState.MAIN_MENU
    
    def _continue_game(self):
        """Continue a saved game."""
        # Use save manager to load the game
        data = save_manager.load_game()
        if not data:
            # Fallback: start new game if no save is found
            self._start_new_game()
            return
        
        # Reconstruct the game
        from ...domain.entities.game import Game
        from ...shared.types.enums import Player
        game = Game.from_dict(data)
        
        # Start the UI with the loaded game
        self.game = game
        self.current_state = MenuState.GAME_PLAYING
        from .chess_game_ui import ChessGameUI
        game_ui = ChessGameUI()
        game_ui.game = self.game
        result = game_ui.run()
        
        # Reset window size to menu size when returning
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Chess Game - Menu")
        
        # After returning from UI, reload saved games list (it might have been removed)
        self._load_saved_games()
        self.current_state = MenuState.MAIN_MENU
    
    def _handle_mouse_click(self, pos: Tuple[int, int]):
        """Handle mouse clicks on menu items."""
        if self.current_state == MenuState.MAIN_MENU:
            menu_items = self._get_main_menu_items()
            for i, item in enumerate(menu_items):
                if item.rect and item.rect.collidepoint(pos) and item.enabled:
                    self.selected_item = i
                    self._execute_menu_action(item.action)
                    break
    
    def run(self):
        """Main menu loop."""
        running = True
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.current_state == MenuState.HELP:
                            self.current_state = MenuState.MAIN_MENU
                        else:
                            running = False
                    else:
                        self._handle_menu_navigation(event.key)
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self._handle_mouse_click(event.pos)
            
            # Draw current state
            if self.current_state == MenuState.MAIN_MENU:
                self._draw_main_menu()
            elif self.current_state == MenuState.HELP:
                self._draw_help_menu()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(60)
        
        # Cleanup
        pygame.quit()
        reset_container()


def main():
    """Main function to run the menu system."""
    try:
        menu = MenuSystem()
        menu.run()
    except Exception as e:
        print(f"Error running menu system: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 