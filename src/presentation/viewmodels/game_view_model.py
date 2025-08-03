"""
Game View Model
Manages UI state and provides data for the presentation layer.
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from ...domain.entities.game import Game
from ...domain.value_objects.square import Square
from ...shared.types.enums import Player, GameResult


@dataclass
class BoardSquareViewModel:
    """View model for a single board square."""
    index: int
    file: str
    rank: int
    piece_type: Optional[str] = None
    piece_color: Optional[str] = None
    is_selected: bool = False
    is_legal_move: bool = False
    is_check: bool = False
    is_last_move: bool = False
    is_hovered: bool = False
    
    @property
    def algebraic_notation(self) -> str:
        """Get algebraic notation for this square."""
        return f"{self.file}{self.rank}"
    
    @property
    def has_piece(self) -> bool:
        """Check if square has a piece."""
        return self.piece_type is not None
    
    @property
    def is_white_piece(self) -> bool:
        """Check if piece is white."""
        return self.piece_color == "white"
    
    @property
    def is_black_piece(self) -> bool:
        """Check if piece is black."""
        return self.piece_color == "black"


@dataclass
class GameStateViewModel:
    """View model for game state."""
    game_id: str
    current_player: str
    board_squares: List[BoardSquareViewModel] = field(default_factory=list)
    selected_square: Optional[int] = None
    legal_moves: List[int] = field(default_factory=list)
    is_game_active: bool = True
    is_check: bool = False
    is_checkmate: bool = False
    is_stalemate: bool = False
    winner: Optional[str] = None
    move_count: int = 0
    last_move_notation: Optional[str] = None
    white_player: str = "White"
    black_player: str = "Black"
    
    @property
    def game_ended(self) -> bool:
        """Check if game has ended."""
        return self.is_checkmate or self.is_stalemate or self.winner is not None
    
    @property
    def current_player_name(self) -> str:
        """Get current player name."""
        return self.white_player if self.current_player == "white" else self.black_player
    
    @property
    def game_result(self) -> Optional[str]:
        """Get game result description."""
        if self.is_checkmate:
            return f"Checkmate - {self.winner} wins!"
        elif self.is_stalemate:
            return "Stalemate - Draw"
        elif self.winner:
            return f"{self.winner} wins!"
        return None


@dataclass
class MenuViewModel:
    """View model for menu state."""
    is_main_menu: bool = True
    is_game_menu: bool = False
    is_settings_menu: bool = False
    is_help_menu: bool = False
    selected_option: int = 0
    menu_options: List[str] = field(default_factory=list)
    
    def get_selected_option_text(self) -> Optional[str]:
        """Get text of currently selected option."""
        if 0 <= self.selected_option < len(self.menu_options):
            return self.menu_options[self.selected_option]
        return None


@dataclass
class UIStateViewModel:
    """View model for overall UI state."""
    game_state: GameStateViewModel = field(default_factory=GameStateViewModel)
    menu_state: MenuViewModel = field(default_factory=MenuViewModel)
    is_fullscreen: bool = False
    window_size: Tuple[int, int] = (800, 600)
    theme_name: str = "classic"
    show_legal_moves: bool = True
    show_coordinates: bool = True
    show_move_history: bool = True
    show_captured_pieces: bool = True
    animation_enabled: bool = True
    sound_enabled: bool = True
    fps: int = 60
    is_paused: bool = False
    show_debug_info: bool = False


class GameViewModel:
    """Main view model for the chess game."""
    
    def __init__(self):
        """Initialize game view model."""
        self._ui_state = UIStateViewModel()
        self._game: Optional[Game] = None
        self._last_move_from: Optional[int] = None
        self._last_move_to: Optional[int] = None
    
    def update_from_game(self, game: Game, selected_square: Optional[int] = None, legal_moves: List[int] = None) -> None:
        """
        Update view model from game state.
        
        Args:
            game: Current game state
            selected_square: Currently selected square
            legal_moves: Legal moves for selected piece
        """
        self._game = game
        
        # Update game state
        self._ui_state.game_state.game_id = game.game_id
        self._ui_state.game_state.current_player = game.current_player.value
        self._ui_state.game_state.is_game_active = not game.is_ended
        self._ui_state.game_state.move_count = game.move_history.get_move_count()
        self._ui_state.game_state.white_player = game.white_player
        self._ui_state.game_state.black_player = game.black_player
        
        # Update game result
        if game.is_ended:
            self._ui_state.game_state.is_checkmate = game.end_reason == "checkmate"
            self._ui_state.game_state.is_stalemate = game.end_reason == "stalemate"
            self._ui_state.game_state.winner = game.winner.value if game.winner else None
        
        # Update board squares
        self._update_board_squares(selected_square, legal_moves or [])
        
        # Update last move
        if game.move_history.get_move_count() > 0:
            last_move = game.move_history.get_last_move()
            if last_move:
                self._last_move_from = last_move.from_square.index
                self._last_move_to = last_move.to_square.index
                self._ui_state.game_state.last_move_notation = last_move.notation
    
    def _update_board_squares(self, selected_square: Optional[int], legal_moves: List[int]) -> None:
        """Update board squares view model."""
        squares = []
        
        for rank in range(8):
            for file in range(8):
                square_index = rank * 8 + file
                square = Square(square_index)
                
                # Get piece at square
                piece = self._game.board.get_piece_at(square_index) if self._game else None
                
                square_vm = BoardSquareViewModel(
                    index=square_index,
                    file=square.file,
                    rank=square.rank,
                    piece_type=piece.type.value if piece else None,
                    piece_color=piece.color.value if piece else None,
                    is_selected=square_index == selected_square,
                    is_legal_move=square_index in legal_moves,
                    is_last_move=square_index in [self._last_move_from, self._last_move_to] if self._last_move_from is not None else False,
                    is_check=self._is_square_check(square_index) if self._game else False
                )
                
                squares.append(square_vm)
        
        self._ui_state.game_state.board_squares = squares
        self._ui_state.game_state.selected_square = selected_square
        self._ui_state.game_state.legal_moves = legal_moves
    
    def _is_square_check(self, square_index: int) -> bool:
        """Check if square is under check."""
        if not self._game:
            return False
        
        # Check if current player's king is in check
        king_square = self._game.board.find_king(self._game.current_player)
        return king_square and king_square.index == square_index
    
    def get_square_at(self, index: int) -> Optional[BoardSquareViewModel]:
        """Get square view model at index."""
        for square in self._ui_state.game_state.board_squares:
            if square.index == index:
                return square
        return None
    
    def get_square_at_position(self, file: str, rank: int) -> Optional[BoardSquareViewModel]:
        """Get square view model at file and rank."""
        for square in self._ui_state.game_state.board_squares:
            if square.file == file and square.rank == rank:
                return square
        return None
    
    def get_pieces_by_color(self, color: str) -> List[BoardSquareViewModel]:
        """Get all pieces of a specific color."""
        return [square for square in self._ui_state.game_state.board_squares 
                if square.piece_color == color]
    
    def get_captured_pieces(self, color: str) -> Dict[str, int]:
        """Get captured pieces for a color."""
        if not self._game:
            return {}
        
        # This would need to be implemented based on move history
        # For now, return empty dict
        return {}
    
    def set_menu_state(self, is_main_menu: bool = True, is_game_menu: bool = False, 
                      is_settings_menu: bool = False, is_help_menu: bool = False) -> None:
        """Set menu state."""
        self._ui_state.menu_state.is_main_menu = is_main_menu
        self._ui_state.menu_state.is_game_menu = is_game_menu
        self._ui_state.menu_state.is_settings_menu = is_settings_menu
        self._ui_state.menu_state.is_help_menu = is_help_menu
    
    def set_menu_options(self, options: List[str]) -> None:
        """Set menu options."""
        self._ui_state.menu_state.menu_options = options
        if self._ui_state.menu_state.selected_option >= len(options):
            self._ui_state.menu_state.selected_option = 0
    
    def select_next_menu_option(self) -> None:
        """Select next menu option."""
        if self._ui_state.menu_state.menu_options:
            self._ui_state.menu_state.selected_option = (
                (self._ui_state.menu_state.selected_option + 1) % 
                len(self._ui_state.menu_state.menu_options)
            )
    
    def select_previous_menu_option(self) -> None:
        """Select previous menu option."""
        if self._ui_state.menu_state.menu_options:
            self._ui_state.menu_state.selected_option = (
                (self._ui_state.menu_state.selected_option - 1) % 
                len(self._ui_state.menu_state.menu_options)
            )
    
    def get_ui_state(self) -> UIStateViewModel:
        """Get current UI state."""
        return self._ui_state
    
    def get_game_state(self) -> GameStateViewModel:
        """Get current game state."""
        return self._ui_state.game_state
    
    def get_menu_state(self) -> MenuViewModel:
        """Get current menu state."""
        return self._ui_state.menu_state
    
    def toggle_fullscreen(self) -> None:
        """Toggle fullscreen mode."""
        self._ui_state.is_fullscreen = not self._ui_state.is_fullscreen
    
    def set_window_size(self, width: int, height: int) -> None:
        """Set window size."""
        self._ui_state.window_size = (width, height)
    
    def set_theme(self, theme_name: str) -> None:
        """Set UI theme."""
        self._ui_state.theme_name = theme_name
    
    def toggle_legal_moves(self) -> None:
        """Toggle legal moves display."""
        self._ui_state.show_legal_moves = not self._ui_state.show_legal_moves
    
    def toggle_coordinates(self) -> None:
        """Toggle coordinates display."""
        self._ui_state.show_coordinates = not self._ui_state.show_coordinates
    
    def toggle_animations(self) -> None:
        """Toggle animations."""
        self._ui_state.animation_enabled = not self._ui_state.animation_enabled
    
    def toggle_sound(self) -> None:
        """Toggle sound."""
        self._ui_state.sound_enabled = not self._ui_state.sound_enabled
    
    def toggle_debug_info(self) -> None:
        """Toggle debug information display."""
        self._ui_state.show_debug_info = not self._ui_state.show_debug_info
    
    def pause_game(self) -> None:
        """Pause the game."""
        self._ui_state.is_paused = True
    
    def resume_game(self) -> None:
        """Resume the game."""
        self._ui_state.is_paused = False 