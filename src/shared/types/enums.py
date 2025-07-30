"""
Domain Types and Enums
MIGRATED FROM: config.py constants and scattered enum-like values
"""

from enum import Enum, IntEnum
from typing import Tuple


class GameState(Enum):
    """Game state enumeration."""
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    CHECKMATE = "checkmate"
    STALEMATE = "stalemate"
    DRAW = "draw"


class Player(Enum):
    """Player colors."""
    WHITE = "white"
    BLACK = "black"
    
    @property
    def chess_value(self) -> bool:
        """Get boolean value for python-chess compatibility."""
        return self == Player.WHITE
    
    @property
    def name(self) -> str:
        return "White" if self == Player.WHITE else "Black"
    
    def opposite(self) -> 'Player':
        return Player.BLACK if self == Player.WHITE else Player.WHITE


class PieceType(IntEnum):
    """Chess piece types matching python-chess constants."""
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6


class GameResult(Enum):
    """Game result types."""
    WHITE_WINS = "white_wins"
    BLACK_WINS = "black_wins"
    DRAW_STALEMATE = "draw_stalemate"
    DRAW_INSUFFICIENT_MATERIAL = "draw_insufficient_material"
    DRAW_FIFTY_MOVES = "draw_fifty_moves"
    DRAW_REPETITION = "draw_repetition"
    ONGOING = "ongoing"


class UIColors:
    """UI Color constants - MIGRATED FROM config.py"""
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)
    DARK_GREEN = (0, 128, 0)
    BLUE = (0, 0, 255)
    RED = (255, 0, 0)
    DARK_RED = (128, 0, 0)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (200, 200, 200)


class UIConstants:
    """UI Constants - MIGRATED FROM config.py"""
    FPS = 30
    WINDOW_WIDTH = 512
    WINDOW_HEIGHT = 600
    BOARD_SIZE = 8
    SQUARE_SIZE = WINDOW_WIDTH // BOARD_SIZE
    STATUS_HEIGHT = 88


class InputAction(Enum):
    """User input actions."""
    SELECT_SQUARE = "select_square"
    MAKE_MOVE = "make_move"
    UNDO_MOVE = "undo_move"
    RESET_GAME = "reset_game"
    QUIT_GAME = "quit_game"
    SHOW_MENU = "show_menu"


class Square:
    """Chess square representation."""
    def __init__(self, index: int):
        if not 0 <= index <= 63:
            raise ValueError(f"Invalid square index: {index}")
        self.index = index
    
    @property
    def rank(self) -> int:
        """Get rank (row) 0-7."""
        return self.index // 8
    
    @property
    def file(self) -> int:
        """Get file (column) 0-7."""
        return self.index % 8
    
    @property
    def algebraic(self) -> str:
        """Get algebraic notation (e.g., 'e4')."""
        files = 'abcdefgh'
        ranks = '12345678'
        return f"{files[self.file]}{ranks[self.rank]}"
    
    @classmethod
    def from_coords(cls, rank: int, file: int) -> 'Square':
        """Create square from rank/file coordinates."""
        return cls(rank * 8 + file)
    
    @classmethod
    def from_algebraic(cls, notation: str) -> 'Square':
        """Create square from algebraic notation."""
        if len(notation) != 2:
            raise ValueError(f"Invalid algebraic notation: {notation}")
        
        file = ord(notation[0].lower()) - ord('a')
        rank = int(notation[1]) - 1
        
        if not (0 <= file <= 7 and 0 <= rank <= 7):
            raise ValueError(f"Invalid algebraic notation: {notation}")
        
        return cls.from_coords(rank, file)
    
    def __eq__(self, other) -> bool:
        return isinstance(other, Square) and self.index == other.index
    
    def __hash__(self) -> int:
        return hash(self.index)
    
    def __str__(self) -> str:
        return self.algebraic
    
    def __repr__(self) -> str:
        return f"Square({self.algebraic})"


# Type aliases for better readability
Position = Tuple[int, int]  # (x, y) pixel coordinates
Coordinate = Tuple[int, int]  # (rank, file) board coordinates
Color = Tuple[int, int, int]  # RGB color tuple