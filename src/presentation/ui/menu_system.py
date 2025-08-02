"""
Menu System for Chess Game
Provides menu interface with game options.
"""

import os
import sys
import math
import random
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

    def __init__(self, text: str, action: str, enabled: bool = True, icon: str = ""):
        self.text = text
        self.action = action
        self.enabled = enabled
        self.icon = icon
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
        self.WINDOW_WIDTH = 1000
        self.WINDOW_HEIGHT = 700

        # Setup display
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Chess Game - Menu")

        self.clock = pygame.time.Clock()

        # Fonts - Improved typography hierarchy
        self.title_font = pygame.font.Font(None, 84)  # Larger title
        self.subtitle_font = pygame.font.Font(None, 32)  # New subtitle font
        self.menu_font = pygame.font.Font(None, 36)  # Slightly smaller menu items
        self.menu_font_bold = pygame.font.Font(None, 38)  # Bold for selected items
        self.help_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.version_font = pygame.font.Font(None, 16)

        # Menu state
        self.current_state = MenuState.MAIN_MENU
        self.selected_item = 0
        
        # Animation properties
        self.title_animation = 0.0
        self.menu_item_animations = [0.0] * 10  # Support up to 10 menu items
        self.menu_animation_objects = []  # Store animation objects for menu items
        
        # Background animation properties
        self.background_time = 0.0
        self.chess_pieces_alpha = 0.0
        
        # Particle system for visual effects
        self.particles = []
        self.particle_timer = 0.0

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
        animate(self, 'title_animation', 1.0, 1.2, easing=EasingType.EASE_OUT, delay=0.2)
        
        # Animate background chess pieces
        animate(self, 'chess_pieces_alpha', 0.3, 2.0, easing=EasingType.EASE_OUT, delay=0.5)
        
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
                   easing=EasingType.EASE_OUT, delay=0.8 + i * 0.15)
            
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
        """Get main menu items with icons."""
        return [
            MenuItem("New Game", "new_game", True, ""),
            MenuItem("Continue Game", "continue_game", bool(self.saved_games), ""),
            MenuItem("Help", "help", True, ""),
            MenuItem("Quit", "quit", True, ""),
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

    def _draw_chess_background(self) -> None:
        """Draw animated chess-themed background elements."""
        # Draw subtle chess board pattern
        square_size = 60
        alpha = int(20 * self.chess_pieces_alpha)
        
        for row in range(0, self.WINDOW_HEIGHT // square_size + 2):
            for col in range(0, self.WINDOW_WIDTH // square_size + 2):
                x = col * square_size + (self.background_time * 10) % square_size
                y = row * square_size + (self.background_time * 5) % square_size
                
                if (row + col) % 2 == 0:
                    color = (*self.theme.get_color('surface'), alpha)
                    rect = pygame.Rect(x, y, square_size, square_size)
                    surface = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
                    surface.fill(color)
                    self.screen.blit(surface, rect)
        
        # Draw floating chess pieces
        pieces = ["♔", "♕", "♖", "♗", "♘", "♙"]
        for i in range(6):
            piece = pieces[i]
            x = 50 + i * 150 + math.sin(self.background_time + i) * 20
            y = 100 + i * 80 + math.cos(self.background_time + i) * 15
            
            piece_alpha = int(15 * self.chess_pieces_alpha)
            piece_surface = self.title_font.render(piece, True, (*self.theme.get_color('on_background'), piece_alpha))
            self.screen.blit(piece_surface, (x, y))
        
        # Draw particles
        self._draw_particles()
    
    def _create_particle(self, x: float, y: float) -> dict:
        """Create a new particle."""
        return {
            'x': x,
            'y': y,
            'vx': (random.random() - 0.5) * 20,
            'vy': (random.random() - 0.5) * 20,
            'life': 1.0,
            'max_life': 1.0,
            'size': random.random() * 3 + 1
        }
    
    def _update_particles(self, dt: float) -> None:
        """Update particle system."""
        # Add new particles
        self.particle_timer += dt
        if self.particle_timer > 0.1:  # Create particle every 0.1 seconds
            self.particle_timer = 0.0
            x = random.random() * self.WINDOW_WIDTH
            y = random.random() * self.WINDOW_HEIGHT
            self.particles.append(self._create_particle(x, y))
        
        # Update existing particles
        for particle in self.particles[:]:
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['life'] -= dt * 0.5
            
            # Remove dead particles
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def _draw_particles(self) -> None:
        """Draw particles."""
        for particle in self.particles:
            alpha = int(255 * (particle['life'] / particle['max_life']))
            size = int(particle['size'])
            
            if size > 0:
                color = (*self.theme.get_color('primary'), alpha)
                pygame.draw.circle(
                    self.screen, 
                    color, 
                    (int(particle['x']), int(particle['y'])), 
                    size
                )

    def _draw_title(self):
        """Draw the game title with enhanced styling."""
        # Apply animation transform
        scale = 0.8 + 0.4 * self.title_animation
        alpha = int(255 * self.title_animation)
        
        # Main title
        title_surface = self.title_font.render("CHESS", True, self.theme.get_color('primary'))
        
        # Scale the surface
        if scale != 1.0:
            original_size = title_surface.get_size()
            new_size = (int(original_size[0] * scale), int(original_size[1] * scale))
            title_surface = pygame.transform.scale(title_surface, new_size)
        
        title_surface.set_alpha(alpha)
        title_rect = title_surface.get_rect(center=(self.WINDOW_WIDTH // 2, 120))
        
        # Add shadow effect
        shadow_surface = self.title_font.render("CHESS", True, (0, 0, 0))
        if scale != 1.0:
            shadow_surface = pygame.transform.scale(shadow_surface, new_size)
        shadow_surface.set_alpha(alpha // 3)
        shadow_rect = shadow_surface.get_rect(center=(self.WINDOW_WIDTH // 2 + 3, 123))
        self.screen.blit(shadow_surface, shadow_rect)
        
        self.screen.blit(title_surface, title_rect)
        
        # Subtitle with animation
        if self.title_animation > 0.6:
            subtitle_alpha = int(255 * (self.title_animation - 0.6) / 0.4)
            subtitle_surface = self.subtitle_font.render("Strategic Battle of Minds", True, self.theme.get_color('on_background'))
            subtitle_surface.set_alpha(subtitle_alpha)
            subtitle_rect = subtitle_surface.get_rect(center=(self.WINDOW_WIDTH // 2, 180))
            self.screen.blit(subtitle_surface, subtitle_rect)

    def _draw_menu_items(self, items: List[MenuItem], start_y: int = 280):
        """Draw menu items with enhanced styling."""
        for i, item in enumerate(items):
            # Get animation progress from animation objects
            animation_progress = 0.0
            if i < len(self.menu_animation_objects):
                animation_progress = self.menu_animation_objects[i].value
            
            # Calculate colors and styling based on state
            is_selected = i == self.selected_item and item.enabled
            is_enabled = item.enabled
            
            # Background styling
            item_width = 400
            item_height = 60
            item_x = (self.WINDOW_WIDTH - item_width) // 2
            item_y = start_y + i * 80
            
            # Draw background
            if is_selected:
                # Selected item background with gradient
                bg_rect = pygame.Rect(item_x - 10, item_y - 5, item_width + 20, item_height + 10)
                bg_surface = pygame.Surface((item_width + 20, item_height + 10), pygame.SRCALPHA)
                
                # Gradient background
                for y in range(item_height + 10):
                    t = y / (item_height + 10)
                    color = self._interpolate_color(
                        self.theme.get_color('primary'),
                        self.theme.get_color('surface'),
                        t
                    )
                    pygame.draw.line(bg_surface, (*color, 180), (0, y), (item_width + 20, y))
                
                self.screen.blit(bg_surface, bg_rect.topleft)
                
                # Border
                pygame.draw.rect(self.screen, self.theme.get_color('primary'), bg_rect, 2)
            
            # Text styling
            if is_selected:
                font = self.menu_font_bold
                color = self.theme.get_color('on_primary', (255, 255, 255))
            elif is_enabled:
                font = self.menu_font
                color = self.theme.get_color('on_background')
            else:
                font = self.menu_font
                color = self.theme.get_color('on_background', (128, 128, 128))
            
            # Apply animation
            alpha = int(255 * animation_progress)
            x_offset = int(80 * (1 - animation_progress))
            
            # Render text (centered)
            text_surface = font.render(item.text, True, color)
            text_surface.set_alpha(alpha)
            text_rect = text_surface.get_rect(
                center=(self.WINDOW_WIDTH // 2 + x_offset, item_y + item_height // 2)
            )
            
            # Store rect for click detection (larger click area)
            item.rect = pygame.Rect(item_x - 10, item_y - 5, item_width + 20, item_height + 10)
            
            self.screen.blit(text_surface, text_rect)
            
            # Add subtle hover effect for enabled items
            if is_enabled and not is_selected:
                # Subtle glow effect for text
                glow_surface = font.render(item.text, True, (*self.theme.get_color('primary'), 30))
                glow_surface.set_alpha(alpha // 4)
                glow_rect = glow_surface.get_rect(
                    center=(self.WINDOW_WIDTH // 2 + x_offset + 1, item_y + item_height // 2 + 1)
                )
                self.screen.blit(glow_surface, glow_rect)

    def _draw_help_screen(self):
        """Draw help screen with improved styling."""
        help_text = self._get_help_text()

        y_offset = 80
        for line in help_text:
            if line == "":
                y_offset += 25
                continue

            if line == "CHESS GAME HELP":
                font = self.title_font
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
            y_offset += 35

    def _draw_main_menu(self):
        """Draw main menu with enhanced design."""
        # Draw background
        self.screen.fill(self.theme.get_color('background'))
        
        # Draw animated chess background
        self._draw_chess_background()
        
        # Draw gradient overlay
        self._draw_gradient_background()

        # Draw title
        self._draw_title()

        # Draw menu items
        menu_items = self._get_main_menu_items()
        self._draw_menu_items(menu_items)

        # Draw version info with better styling
        self._draw_version_info()
    
    def _draw_version_info(self):
        """Draw version information with improved styling."""
        version_text = "v1.0"
        subtitle_text = "Clean Architecture Edition"
        
        # Version number
        version_surface = self.version_font.render(version_text, True, self.theme.get_color('on_background', (100, 100, 100)))
        version_rect = version_surface.get_rect(
            center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT - 50)
        )
        self.screen.blit(version_surface, version_rect)
        
        # Subtitle
        subtitle_surface = self.small_font.render(subtitle_text, True, self.theme.get_color('on_background', (80, 80, 80)))
        subtitle_rect = subtitle_surface.get_rect(
            center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT - 30)
        )
        self.screen.blit(subtitle_surface, subtitle_rect)
    

    
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
        # Update background animation time
        self.background_time += dt
        
        # Update particle system
        self._update_particles(dt)
        
        # Update animation system
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
