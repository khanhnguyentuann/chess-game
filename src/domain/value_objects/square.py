"""
Square Value Object
Represents a chess square with validation and utility methods.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Square:
    """Immutable value object representing a chess square."""
    
    index: int
    
    def __post_init__(self):
        """Validate square index."""
        if not (0 <= self.index <= 63):
            raise ValueError(f"Square index must be between 0 and 63, got {self.index}")
    
    @property
    def file(self) -> int:
        """Get file (column) of square (0-7)."""
        return self.index % 8
    
    @property
    def rank(self) -> int:
        """Get rank (row) of square (0-7)."""
        return self.index // 8
    
    @property
    def algebraic_notation(self) -> str:
        """Get algebraic notation (e.g., 'e4')."""
        files = 'abcdefgh'
        ranks = '87654321'
        return f"{files[self.file]}{ranks[self.rank]}"
    
    @classmethod
    def from_algebraic(cls, notation: str) -> "Square":
        """Create square from algebraic notation."""
        if len(notation) != 2:
            raise ValueError(f"Invalid algebraic notation: {notation}")
        
        file_char, rank_char = notation.lower()
        files = 'abcdefgh'
        ranks = '87654321'
        
        try:
            file_idx = files.index(file_char)
            rank_idx = ranks.index(rank_char)
            index = rank_idx * 8 + file_idx
            return cls(index)
        except ValueError:
            raise ValueError(f"Invalid algebraic notation: {notation}")
    
    @classmethod
    def from_file_rank(cls, file: int, rank: int) -> "Square":
        """Create square from file and rank."""
        if not (0 <= file <= 7) or not (0 <= rank <= 7):
            raise ValueError(f"File and rank must be between 0 and 7, got file={file}, rank={rank}")
        
        index = rank * 8 + file
        return cls(index)
    
    def is_valid(self) -> bool:
        """Check if square is valid."""
        return 0 <= self.index <= 63
    
    def __str__(self) -> str:
        return self.algebraic_notation
    
    def __repr__(self) -> str:
        return f"Square({self.algebraic_notation})" 