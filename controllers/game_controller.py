"""
Game Controller - Handles user input, game flow, and coordinates between Model and View.
This module manages the game loop, input processing, and communication between components.
"""

import pygame
import sys
from typing import Tuple, Optional
from models.chess_board import ChessBoard
from views.pygame_view import PygameView
from config import SQUARE_SIZE, FPS


class GameController:
    """
    Controller class that manages:
    - Game loop and timing
    - User input processing
    - Coordination between Model and View
    - Game state transitions
    """
    
    def __init__(self, screen: pygame.Surface):
        """
        Initialize the game controller.
        
        Args:
            screen: Pygame surface for rendering
        """
        self.screen = screen
        self.chess_board = ChessBoard()
        self.view = PygameView(screen)
        self.clock = pygame.time.Clock()
        self.running = True
    
    def start_game(self) -> None:
        """Start the complete game flow including menus and game loop."""
        # Show start screen and instructions
        self.view.show_start_screen()
        self.view.show_instructions()
        
        # Main game loop
        while self.running:
            self._game_loop()
            
            # Handle game over
            if self.chess_board.is_game_over():
                result = self.chess_board.get_game_result()
                if result:
                    play_again = self.view.show_game_over_screen(result)
                    if play_again:
                        self._reset_game()
                    else:
                        self.running = False
                else:
                    self.running = False
        
        pygame.quit()
        sys.exit()
    
    def _game_loop(self) -> None:
        """Main game loop handling events, updates, and rendering."""
        while not self.chess_board.is_game_over() and self.running:
            # Handle events
            self._handle_events()
            
            # Render everything
            self._render()
            
            # Control frame rate
            self.clock.tick(FPS)
    
    def _handle_events(self) -> None:
        """Process all pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self._handle_keyboard_input(event.key)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    self._handle_mouse_click(event.pos)
    
    def _handle_keyboard_input(self, key: int) -> None:
        """
        Handle keyboard input.
        
        Args:
            key: Pygame key constant
        """
        if key == pygame.K_ESCAPE:
            self.running = False
        elif key == pygame.K_r:
            # Reset game
            self._reset_game()
        elif key == pygame.K_u:
            # Undo last move
            self.chess_board.undo_last_move()
        elif key == pygame.K_q:
            # Quit game
            self.running = False
    
    def _handle_mouse_click(self, position: Tuple[int, int]) -> None:
        """
        Handle mouse click events for piece selection and movement.
        
        Args:
            position: Mouse click position (x, y)
        """
        square = self._position_to_square(position)
        if square is None:
            return
        
        # If no square is selected, try to select this square
        if self.chess_board.selected_square is None:
            self.chess_board.select_square(square)
        else:
            # Try to make a move to this square
            move_successful = self.chess_board.make_move(square)
            
            # If move failed and clicked on a different piece of same color, select it
            if not move_successful and self.chess_board.is_valid_selection(square):
                self.chess_board.select_square(square)
            elif not move_successful:
                # Clear selection if move failed and not selecting new piece
                self.chess_board.clear_selection()
    
    def _position_to_square(self, position: Tuple[int, int]) -> Optional[int]:
        """
        Convert mouse position to board square index.
        
        Args:
            position: Mouse position (x, y)
            
        Returns:
            Square index (0-63) or None if outside board
        """
        x, y = position
        
        # Check if click is within the board area
        if x < 0 or x >= SQUARE_SIZE * 8 or y < 0 or y >= SQUARE_SIZE * 8:
            return None
        
        col = x // SQUARE_SIZE
        row = y // SQUARE_SIZE
        
        # Ensure we're within valid board coordinates
        if 0 <= row < 8 and 0 <= col < 8:
            return row * 8 + col
        
        return None
    
    def _render(self) -> None:
        """Render all game elements."""
        # Clear screen
        self.view.clear_screen()
        
        # Draw board and pieces
        self.view.draw_board(self.chess_board)
        
        # Draw selection and valid moves
        if self.chess_board.selected_square is not None:
            self.view.draw_selected_square(self.chess_board.selected_square)
            self.view.draw_valid_moves(self.chess_board.valid_moves)
        
        # Draw status
        self.view.draw_status(self.chess_board)
        
        # Update display
        self.view.update_display()
    
    def _reset_game(self) -> None:
        """Reset the game to initial state."""
        self.chess_board.reset_board()
