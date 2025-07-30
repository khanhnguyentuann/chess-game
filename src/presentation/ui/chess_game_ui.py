"""
Chess Game UI using Pygame
Clean Architecture presentation layer for chess game with interactive board.
"""

import pygame
import chess
import asyncio
from typing import Optional, Tuple, Dict, Any, List
from pathlib import Path
import logging

from ...application.use_cases.make_move import MakeMoveUseCase
from ...domain.entities.game import Game
from ...shared.types.type_definitions import MoveRequest
from ...shared.types.enums import Player


class ChessGameUI:
    """
    Pygame-based chess game UI following Clean Architecture principles.
    Handles user input and visual representation while delegating game logic to use cases.
    """
    
    # UI Constants
    WINDOW_WIDTH = 512
    WINDOW_HEIGHT = 600
    BOARD_SIZE = 8
    SQUARE_SIZE = WINDOW_WIDTH // BOARD_SIZE
    STATUS_HEIGHT = 88
    
    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    LIGHT_BROWN = (240, 217, 181)
    DARK_BROWN = (181, 136, 99)
    HIGHLIGHT_GREEN = (0, 255, 0, 128)
    HIGHLIGHT_YELLOW = (255, 255, 0, 128)
    HIGHLIGHT_RED = (255, 0, 0, 128)
    
    def __init__(self, 
                 make_move_use_case: MakeMoveUseCase,
                 game: Game,
                 assets_path: str = "assets"):
        self.make_move_use_case = make_move_use_case
        self.game = game
        self.assets_path = Path(assets_path)
        self.logger = logging.getLogger(__name__)
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Chess Game - Clean Architecture")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        
        # Load piece images
        self.piece_images = self._load_piece_images()
        
        # Game state
        self.selected_square: Optional[int] = None
        self.valid_moves: List[chess.Move] = []
        self.running = True
        self.drag_piece = None
        self.drag_pos = (0, 0)
        
        self.logger.info("Chess Game UI initialized")
    
    def _load_piece_images(self) -> Dict[str, pygame.Surface]:
        """Load chess piece images."""
        pieces = {
            'wp': 'wp.png', 'wr': 'wr.png', 'wn': 'wn.png', 'wb': 'wb.png', 'wq': 'wq.png', 'wk': 'wk.png',
            'bp': 'bp.png', 'br': 'br.png', 'bn': 'bn.png', 'bb': 'bb.png', 'bq': 'bq.png', 'bk': 'bk.png'
        }
        
        images = {}
        images_path = self.assets_path / "images"
        
        for piece_key, filename in pieces.items():
            try:
                image_path = images_path / filename
                if image_path.exists():
                    image = pygame.image.load(str(image_path))
                    images[piece_key] = pygame.transform.scale(image, (self.SQUARE_SIZE, self.SQUARE_SIZE))
                else:
                    self.logger.warning(f"Piece image not found: {image_path}")
                    # Create a placeholder
                    surface = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE))
                    surface.fill(self.BLACK if piece_key[0] == 'b' else self.WHITE)
                    images[piece_key] = surface
            except Exception as e:
                self.logger.error(f"Error loading piece image {filename}: {e}")
                # Create a simple colored square as fallback
                surface = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE))
                surface.fill(self.BLACK if piece_key[0] == 'b' else self.WHITE)
                images[piece_key] = surface
        
        return images
    
    def _square_to_coords(self, square: int) -> Tuple[int, int]:
        """Convert chess square number to screen coordinates."""
        file = square % 8
        rank = 7 - (square // 8)  # Flip rank for display
        x = file * self.SQUARE_SIZE
        y = rank * self.SQUARE_SIZE
        return x, y
    
    def _coords_to_square(self, x: int, y: int) -> Optional[int]:
        """Convert screen coordinates to chess square number."""
        if x < 0 or x >= self.WINDOW_WIDTH or y < 0 or y >= self.WINDOW_WIDTH:
            return None
        
        file = x // self.SQUARE_SIZE
        rank = 7 - (y // self.SQUARE_SIZE)  # Flip rank for chess coordinates
        square = rank * 8 + file
        
        return square if 0 <= square <= 63 else None
    
    def _draw_board(self):
        """Draw the chess board."""
        for rank in range(8):
            for file in range(8):
                color = self.LIGHT_BROWN if (rank + file) % 2 == 0 else self.DARK_BROWN
                x = file * self.SQUARE_SIZE
                y = rank * self.SQUARE_SIZE
                pygame.draw.rect(self.screen, color, (x, y, self.SQUARE_SIZE, self.SQUARE_SIZE))
    
    def _draw_highlights(self):
        """Draw square highlights for selected piece and valid moves."""
        if self.selected_square is not None:
            # Highlight selected square
            x, y = self._square_to_coords(self.selected_square)
            highlight_surface = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)
            highlight_surface.fill(self.HIGHLIGHT_YELLOW)
            self.screen.blit(highlight_surface, (x, y))
            
            # Highlight valid moves
            for move in self.valid_moves:
                x, y = self._square_to_coords(move.to_square)
                highlight_surface = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)
                # Different color for capture moves
                if self.game.board.internal_board.piece_at(move.to_square):
                    highlight_surface.fill(self.HIGHLIGHT_RED)
                else:
                    highlight_surface.fill(self.HIGHLIGHT_GREEN)
                self.screen.blit(highlight_surface, (x, y))
    
    def _draw_pieces(self):
        """Draw chess pieces on the board."""
        board = self.game.board.internal_board
        
        for square in range(64):
            piece = board.piece_at(square)
            if piece is not None and square != self.selected_square:
                piece_key = f"{'w' if piece.color else 'b'}{piece.symbol().lower()}"
                if piece_key in self.piece_images:
                    x, y = self._square_to_coords(square)
                    self.screen.blit(self.piece_images[piece_key], (x, y))
        
        # Draw dragged piece at mouse position
        if self.drag_piece:
            piece_key = f"{'w' if self.drag_piece.color else 'b'}{self.drag_piece.symbol().lower()}"
            if piece_key in self.piece_images:
                mouse_x, mouse_y = self.drag_pos
                x = mouse_x - self.SQUARE_SIZE // 2
                y = mouse_y - self.SQUARE_SIZE // 2
                self.screen.blit(self.piece_images[piece_key], (x, y))
    
    def _draw_status(self):
        """Draw game status information."""
        status_y = self.WINDOW_WIDTH
        status_rect = pygame.Rect(0, status_y, self.WINDOW_WIDTH, self.STATUS_HEIGHT)
        pygame.draw.rect(self.screen, self.WHITE, status_rect)
        pygame.draw.line(self.screen, self.BLACK, (0, status_y), (self.WINDOW_WIDTH, status_y), 2)
        
        # Game information
        current_player = "White" if self.game.current_player == Player.WHITE else "Black"
        status_text = f"Current Player: {current_player}"
        
        if self.game.board.is_in_check():
            status_text += " (IN CHECK!)"
        
        if self.game.is_ended:
            if self.game.winner:
                winner = "White" if self.game.winner == Player.WHITE else "Black"
                status_text = f"Game Over - {winner} Wins!"
            else:
                status_text = "Game Over - Draw!"
        
        # Move count
        move_count_text = f"Moves: {self.game.move_history.get_move_count()}"
        
        # Draw text
        text_surface = self.font.render(status_text, True, self.BLACK)
        self.screen.blit(text_surface, (10, status_y + 10))
        
        move_surface = self.font.render(move_count_text, True, self.BLACK)
        self.screen.blit(move_surface, (10, status_y + 35))
        
        # Instructions
        if not self.game.is_ended:
            instruction = "Click to select piece, click again to move"
            inst_surface = self.font.render(instruction, True, self.BLACK)
            self.screen.blit(inst_surface, (10, status_y + 60))
    
    def _get_valid_moves_for_square(self, square: int) -> List[chess.Move]:
        """Get valid moves for a piece on given square."""
        board = self.game.board.internal_board
        piece = board.piece_at(square)
        
        if piece is None:
            return []
        
        # Check if it's the current player's piece
        current_player_white = (self.game.current_player == Player.WHITE)
        if piece.color != current_player_white:
            return []
        
        # Get all legal moves for this piece
        legal_moves = list(board.legal_moves)
        return [move for move in legal_moves if move.from_square == square]
    
    async def _handle_square_click(self, square: int):
        """Handle clicking on a square."""
        if self.game.is_ended:
            return
        
        board = self.game.board.internal_board
        piece = board.piece_at(square)
        
        if self.selected_square is None:
            # First click - select piece
            if piece is not None:
                current_player_white = (self.game.current_player == Player.WHITE)
                if piece.color == current_player_white:
                    self.selected_square = square
                    self.valid_moves = self._get_valid_moves_for_square(square)
                    self.logger.debug(f"Selected square {square}, found {len(self.valid_moves)} valid moves")
        else:
            # Second click - try to move or reselect
            if square == self.selected_square:
                # Clicked same square - deselect
                self.selected_square = None
                self.valid_moves = []
            elif piece is not None:
                current_player_white = (self.game.current_player == Player.WHITE)
                if piece.color == current_player_white:
                    # Clicked own piece - select new piece
                    self.selected_square = square
                    self.valid_moves = self._get_valid_moves_for_square(square)
                else:
                    # Clicked opponent piece - try to capture
                    await self._try_move(self.selected_square, square)
            else:
                # Clicked empty square - try to move
                await self._try_move(self.selected_square, square)
    
    async def _try_move(self, from_square: int, to_square: int):
        """Try to make a move."""
        # Check if this move is valid
        target_move = None
        for move in self.valid_moves:
            if move.from_square == from_square and move.to_square == to_square:
                target_move = move
                break
        
        if target_move is None:
            self.logger.debug(f"Invalid move: {from_square} to {to_square}")
            self.selected_square = None
            self.valid_moves = []
            return
        
        # Create move request
        move_request = MoveRequest(
            from_square=from_square,
            to_square=to_square,
            promotion=target_move.promotion  # Handle pawn promotion
        )
        
        try:
            # Execute move through use case
            result = await self.make_move_use_case.execute(self.game, move_request)
            
            if result.get("success", False):
                self.logger.info(f"Move successful: {result.get('message', 'Move executed')}")
                # Clear selection
                self.selected_square = None
                self.valid_moves = []
            else:
                self.logger.warning(f"Move failed: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            self.logger.error(f"Error executing move: {e}")
        
        # Clear selection regardless
        self.selected_square = None
        self.valid_moves = []
    
    async def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    x, y = event.pos
                    if y < self.WINDOW_WIDTH:  # Click on board
                        square = self._coords_to_square(x, y)
                        if square is not None:
                            await self._handle_square_click(square)
                            
                            # Start drag if piece selected
                            if self.selected_square == square:
                                board = self.game.board.internal_board
                                self.drag_piece = board.piece_at(square)
                                self.drag_pos = event.pos
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.drag_piece:  # End drag
                    x, y = event.pos
                    if y < self.WINDOW_WIDTH:  # Drop on board
                        square = self._coords_to_square(x, y)
                        if square is not None and self.selected_square is not None:
                            await self._try_move(self.selected_square, square)
                    
                    self.drag_piece = None
            
            elif event.type == pygame.MOUSEMOTION:
                if self.drag_piece:
                    self.drag_pos = event.pos
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Reset game (could add this functionality)
                    pass
                elif event.key == pygame.K_u:
                    # Undo move
                    if self.game.move_history.can_undo():
                        self.game.move_history.undo_move()
                        self.logger.info("Move undone")
    
    def draw(self):
        """Draw the entire game."""
        self.screen.fill(self.WHITE)
        self._draw_board()
        self._draw_highlights()
        self._draw_pieces()
        self._draw_status()
        pygame.display.flip()
    
    async def run(self):
        """Main game loop."""
        self.logger.info("Starting chess game UI")
        
        while self.running:
            await self.handle_events()
            self.draw()
            self.clock.tick(60)  # 60 FPS
            
            # Small delay to allow other async operations
            await asyncio.sleep(0.01)
        
        pygame.quit()
        self.logger.info("Chess game UI stopped")
    
    def shutdown(self):
        """Shutdown the UI."""
        self.running = False
