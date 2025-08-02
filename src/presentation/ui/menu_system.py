"""
Menu System for Chess Game
Provides menu interface with game options.
"""

import os
import sys
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple

import pygame

from ...composition_root import get_container, reset_container
from ...domain.entities.board import Board

# Import domain entities
from ...domain.entities.game import Game
from ...shared.types.enums import GameResult, GameState, Player
from ...shared.utils.save_manager import save_manager
from .animations import animation_system, animate, EasingType
from .themes import theme_manager


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

        # Get current theme
        self.theme = theme_manager.get_current_theme()

        # Window settings
        self.WINDOW_WIDTH = 800
        self.WINDOW_HEIGHT = 600

        # Setup display
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Chess Game - Menu")

        self.clock = pygame.time.Clock()

        # Fonts
        self.title_font = pygame.font.Font(None, 72)
        self.menu_font = pygame.font.Font(None, 48)
        self.help_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)

        # Menu state
        self.current_state = MenuState.MAIN_MENU
        self.selected_item = 0
        
        # Animation properties
        self.title_animation = 0.0
        self.menu_item_animations = [0.0] * 10  # Support up to 10 menu items
        self.menu_animation_objects = []  # Store animation objects for menu items

        # Game state
        self.game = None
        self.saved_games = []

        # Load saved games
        self._load_saved_games()
        
        # Start entrance animations
        self._start_entrance_animations()
    
    def _start_entrance_animations(self) -> None:
        """Start entrance animations for menu elements."""
        # Animate title
        animate(self, 'title_animation', 1.0, 1.0, easing=EasingType.EASE_OUT, delay=0.2)
        
        # Animate menu items - create individual animation objects
        self.menu_animation_objects = []
        for i in range(len(self.menu_item_animations)):
            # Create a simple object with a property for each animation
            class MenuItemAnimation:
                def __init__(self, value=0.0):
                    self.value = value
            
            # Create animation object and animate it
            anim_obj = MenuItemAnimation(0.0)
            animate(anim_obj, 'value', 1.0, 0.8, 
                   easing=EasingType.EASE_OUT, delay=0.5 + i * 0.1)
            
            # Store the animation object
            self.menu_animation_objects.append(anim_obj)

    def _load_saved_games(self):
        """Load saved games from storage."""
        self.saved_games = []

        # Use save manager to get save file info
        save_info = save_manager.get_save_info()
        if save_info:
            game_name = f"Game {save_info['game_id'][:8]}"
            moves = save_info["move_count"]
            modified_date = save_info["modified_at"][:10]  # Just the date part

            self.saved_games.append(
                {
                    "name": game_name,
                    "date": modified_date,
                    "moves": moves,
                    "filename": save_info["filename"],
                }
            )

    def _get_main_menu_items(self) -> List[MenuItem]:
        """Get main menu items."""
        return [
            MenuItem("New Game", "new_game"),
            MenuItem("Continue Game", "continue_game", bool(self.saved_games)),
            MenuItem("Help", "help"),
            MenuItem("Quit", "quit"),
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
            "Press ESC to return to main menu",
        ]

    def _draw_title(self):
        """Draw the game title."""
        # Apply animation transform
        scale = 0.5 + 0.5 * self.title_animation
        alpha = int(255 * self.title_animation)
        
        title_surface = self.title_font.render("CHESS GAME", True, self.theme.get_color('on_background'))
        
        # Scale the surface
        if scale != 1.0:
            original_size = title_surface.get_size()
            new_size = (int(original_size[0] * scale), int(original_size[1] * scale))
            title_surface = pygame.transform.scale(title_surface, new_size)
        
        title_surface.set_alpha(alpha)
        title_rect = title_surface.get_rect(center=(self.WINDOW_WIDTH // 2, 100))
        self.screen.blit(title_surface, title_rect)
        
        # Draw subtitle with animation
        if self.title_animation > 0.7:
            subtitle_alpha = int(255 * (self.title_animation - 0.7) / 0.3)
            subtitle_surface = self.small_font.render("Clean Architecture Edition", True, self.theme.get_color('on_background'))
            subtitle_surface.set_alpha(subtitle_alpha)
            subtitle_rect = subtitle_surface.get_rect(center=(self.WINDOW_WIDTH // 2, 140))
            self.screen.blit(subtitle_surface, subtitle_rect)

    def _draw_menu_items(self, items: List[MenuItem], start_y: int = 200):
        """Draw menu items."""
        for i, item in enumerate(items):
            # Get animation progress from animation objects
            animation_progress = 0.0
            if i < len(self.menu_animation_objects):
                animation_progress = self.menu_animation_objects[i].value
            
            # Calculate colors based on state and animation
            base_color = self.theme.get_color('on_background') if item.enabled else self.theme.get_color('on_background', (128, 128, 128))
            
            if i == self.selected_item and item.enabled:
                color = self.theme.get_color('primary')
                # Draw selection background
                bg_rect = pygame.Rect(self.WINDOW_WIDTH // 2 - 150, start_y + i * 60 - 10, 300, 50)
                bg_surface = pygame.Surface((300, 50), pygame.SRCALPHA)
                bg_surface.fill((*self.theme.get_color('primary'), 30))
                self.screen.blit(bg_surface, bg_rect.topleft)
            else:
                color = base_color
            
            # Apply animation
            alpha = int(255 * animation_progress)
            x_offset = int(50 * (1 - animation_progress))

            text_surface = self.menu_font.render(item.text, True, color)
            text_surface.set_alpha(alpha)
            text_rect = text_surface.get_rect(
                center=(self.WINDOW_WIDTH // 2 + x_offset, start_y + i * 60)
            )

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
                color = self.theme.get_color('primary')
            elif line in ["HOW TO PLAY:", "GAME CONTROLS:", "GAME RULES:"]:
                font = self.menu_font
                color = self.theme.get_color('success')
            else:
                font = self.help_font
                color = self.theme.get_color('on_background')

            text_surface = font.render(line, True, color)
            text_rect = text_surface.get_rect(center=(self.WINDOW_WIDTH // 2, y_offset))
            self.screen.blit(text_surface, text_rect)
            y_offset += 30

    def _draw_main_menu(self):
        """Draw main menu."""
        # Draw background
        self.screen.fill(self.theme.get_color('background'))
        
        # Draw gradient overlay
        self._draw_gradient_background()

        # Draw title
        self._draw_title()

        # Draw menu items
        menu_items = self._get_main_menu_items()
        self._draw_menu_items(menu_items)

        # Draw version info
        version_text = "v1.0 - Clean Architecture"
        version_surface = self.help_font.render(version_text, True, self.theme.get_color('on_background', (128, 128, 128)))
        version_rect = version_surface.get_rect(
            center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT - 30)
        )
        self.screen.blit(version_surface, version_rect)
    
    def _draw_gradient_background(self) -> None:
        """Draw gradient background."""
        # Create a subtle gradient from top to bottom
        start_color = self.theme.get_color('background')
        end_color = self.theme.get_color('surface')
        
        for y in range(self.WINDOW_HEIGHT):
            t = y / self.WINDOW_HEIGHT
            color = self._interpolate_color(start_color, end_color, t)
            pygame.draw.line(self.screen, color, (0, y), (self.WINDOW_WIDTH, y))
    
    def _interpolate_color(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int], t: float) -> Tuple[int, int, int]:
        """Interpolate between two colors."""
        t = max(0.0, min(1.0, t))
        return (
            int(color1[0] + (color2[0] - color1[0]) * t),
            int(color1[1] + (color2[1] - color1[1]) * t),
            int(color1[2] + (color2[2] - color1[2]) * t),
        )

    def _draw_help_menu(self):
        """Draw help menu."""
        # Draw background
        self.screen.fill(self.theme.get_color('background'))
        self._draw_gradient_background()

        # Draw help content
        self._draw_help_screen()

    def _handle_menu_navigation(self, key):
        """Handle menu navigation."""
        if self.current_state == MenuState.MAIN_MENU:
            menu_items = self._get_main_menu_items()
            enabled_items = [i for i, item in enumerate(menu_items) if item.enabled]

            if key == pygame.K_UP:
                current_index = enabled_items.index(self.selected_item)
                self.selected_item = enabled_items[
                    (current_index - 1) % len(enabled_items)
                ]
            elif key == pygame.K_DOWN:
                current_index = enabled_items.index(self.selected_item)
                self.selected_item = enabled_items[
                    (current_index + 1) % len(enabled_items)
                ]
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
        self.game = Game(white_player="Player 1", black_player="Player 2", board=board)

        # Switch to game state
        self.current_state = MenuState.GAME_PLAYING

        # Import and start modern game UI
        from .modern_chess_ui import ModernChessUI

        game_ui = ModernChessUI()
        game_ui.game = self.game
        result = game_ui.run()

        # Reset window size to menu size when returning
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Chess Game - Menu")

        # Return to menu when game ends
        self.current_state = MenuState.MAIN_MENU
        
        # Restart entrance animations
        self._start_entrance_animations()

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
        from .modern_chess_ui import ModernChessUI

        game_ui = ModernChessUI()
        game_ui.game = self.game
        result = game_ui.run()

        # Reset window size to menu size when returning
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Chess Game - Menu")

        # After returning from UI, reload saved games list (it might have been removed)
        self._load_saved_games()
        self.current_state = MenuState.MAIN_MENU
        
        # Restart entrance animations
        self._start_entrance_animations()

    def _handle_mouse_click(self, pos: Tuple[int, int]):
        """Handle mouse clicks on menu items."""
        if self.current_state == MenuState.MAIN_MENU:
            menu_items = self._get_main_menu_items()
            for i, item in enumerate(menu_items):
                if item.rect and item.rect.collidepoint(pos) and item.enabled:
                    self.selected_item = i
                    self._execute_menu_action(item.action)
                    break
    
    def update(self, dt: float) -> None:
        """Update menu state and animations."""
        animation_system.update(dt)

    def run(self):
        """Main menu loop."""
        running = True

        while running:
            dt = self.clock.tick(60) / 1000.0  # Delta time in seconds
            
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
            
            # Update
            self.update(dt)

            # Draw current state
            if self.current_state == MenuState.MAIN_MENU:
                self._draw_main_menu()
            elif self.current_state == MenuState.HELP:
                self._draw_help_menu()

            # Update display
            pygame.display.flip()

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
