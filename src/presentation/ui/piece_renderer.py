"""
Chess Piece Renderer - Draws chess pieces using Pygame shapes and text
Provides vector-based rendering of chess pieces instead of using images.
"""

import math
from typing import Dict, Tuple

import pygame

from ...shared.types.enums import Player


class PieceRenderer:
    """Renders chess pieces using Pygame drawing functions."""

    def __init__(self, square_size: int):
        """Initialize the piece renderer.

        Args:
            square_size: Size of each chess square in pixels
        """
        self.square_size = square_size
        self.piece_size = int(square_size * 0.85)  # Piece takes 85% of square
        self.center_offset = (square_size - self.piece_size) // 2

        # Enhanced colors for pieces with gradients
        self.WHITE_PIECE = (255, 255, 255)
        self.WHITE_PIECE_SHADOW = (240, 240, 240)
        self.WHITE_PIECE_HIGHLIGHT = (255, 255, 255)
        self.BLACK_PIECE = (40, 40, 40)
        self.BLACK_PIECE_SHADOW = (20, 20, 20)
        self.BLACK_PIECE_HIGHLIGHT = (80, 80, 80)

        # Outline colors
        self.WHITE_OUTLINE = (180, 180, 180)
        self.BLACK_OUTLINE = (10, 10, 10)

        # Detail colors
        self.WHITE_DETAIL = (160, 160, 160)
        self.BLACK_DETAIL = (60, 60, 60)

        # Gold accents for crowns and special details
        self.GOLD = (255, 215, 0)
        self.GOLD_SHADOW = (218, 165, 32)

        # Font for piece symbols
        self.font = pygame.font.Font(None, self.piece_size // 2)

        # Cache for rendered pieces
        self.piece_cache: Dict[str, pygame.Surface] = {}

    def get_piece_surface(self, piece_code: str) -> pygame.Surface:
        """Get a surface with the rendered piece.

        Args:
            piece_code: Piece code (e.g., 'wp', 'br', 'wk', etc.)

        Returns:
            pygame.Surface with the rendered piece
        """
        if piece_code in self.piece_cache:
            return self.piece_cache[piece_code]

        # Create new surface
        surface = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)

        # Determine piece type and color
        color = piece_code[0]  # 'w' or 'b'
        piece_type = piece_code[1]  # 'p', 'r', 'n', 'b', 'q', 'k'

        # Draw the piece
        if piece_type == "p":
            self._draw_pawn(surface, color)
        elif piece_type == "r":
            self._draw_rook(surface, color)
        elif piece_type == "n":
            self._draw_knight(surface, color)
        elif piece_type == "b":
            self._draw_bishop(surface, color)
        elif piece_type == "q":
            self._draw_queen(surface, color)
        elif piece_type == "k":
            self._draw_king(surface, color)

        # Cache the result
        self.piece_cache[piece_code] = surface
        return surface

    def _draw_pawn(self, surface: pygame.Surface, color: str):
        """Draw a pawn piece with enhanced details."""
        x, y = self.center_offset, self.center_offset
        size = self.piece_size

        # Colors
        fill_color = self.WHITE_PIECE if color == "w" else self.BLACK_PIECE
        shadow_color = (
            self.WHITE_PIECE_SHADOW if color == "w" else self.BLACK_PIECE_SHADOW
        )
        highlight_color = (
            self.WHITE_PIECE_HIGHLIGHT if color == "w" else self.BLACK_PIECE_HIGHLIGHT
        )
        outline_color = self.WHITE_OUTLINE if color == "w" else self.BLACK_OUTLINE
        detail_color = self.WHITE_DETAIL if color == "w" else self.BLACK_DETAIL

        # Base (bottom part) with shadow
        base_width = int(size * 0.65)
        base_height = int(size * 0.18)
        base_x = x + (size - base_width) // 2
        base_y = y + size - base_height - int(size * 0.08)

        # Shadow
        pygame.draw.rect(
            surface, shadow_color, (base_x + 2, base_y + 2, base_width, base_height)
        )
        # Main base
        pygame.draw.rect(surface, fill_color, (base_x, base_y, base_width, base_height))
        # Highlight
        pygame.draw.rect(
            surface, highlight_color, (base_x, base_y, base_width, base_height // 3)
        )
        pygame.draw.rect(
            surface, outline_color, (base_x, base_y, base_width, base_height), 2
        )

        # Body (middle part) with gradient effect
        body_width = int(size * 0.45)
        body_height = int(size * 0.32)
        body_x = x + (size - body_width) // 2
        body_y = base_y - body_height

        # Shadow
        pygame.draw.rect(
            surface, shadow_color, (body_x + 2, body_y + 2, body_width, body_height)
        )
        # Main body
        pygame.draw.rect(surface, fill_color, (body_x, body_y, body_width, body_height))
        # Highlight
        pygame.draw.rect(
            surface, highlight_color, (body_x, body_y, body_width, body_height // 3)
        )
        pygame.draw.rect(
            surface, outline_color, (body_x, body_y, body_width, body_height), 2
        )

        # Head (top part) with 3D effect
        head_radius = int(size * 0.22)
        head_x = x + size // 2
        head_y = body_y - head_radius

        # Shadow
        pygame.draw.circle(surface, shadow_color, (head_x + 2, head_y + 2), head_radius)
        # Main head
        pygame.draw.circle(surface, fill_color, (head_x, head_y), head_radius)
        # Highlight
        pygame.draw.circle(
            surface,
            highlight_color,
            (head_x - head_radius // 3, head_y - head_radius // 3),
            head_radius // 2,
        )
        pygame.draw.circle(surface, outline_color, (head_x, head_y), head_radius, 2)

        # Crown detail with gold accent
        crown_width = int(size * 0.25)
        crown_height = int(size * 0.12)
        crown_x = head_x - crown_width // 2
        crown_y = head_y - head_radius // 2

        # Crown base
        pygame.draw.rect(
            surface, self.GOLD, (crown_x, crown_y, crown_width, crown_height)
        )
        pygame.draw.rect(
            surface, self.GOLD_SHADOW, (crown_x, crown_y, crown_width, crown_height), 1
        )

        # Crown jewels
        jewel_radius = int(size * 0.02)
        jewel_positions = [
            (crown_x + crown_width // 4, crown_y + crown_height // 2),
            (crown_x + crown_width // 2, crown_y + crown_height // 3),
            (crown_x + 3 * crown_width // 4, crown_y + crown_height // 2),
        ]

        for jewel_x, jewel_y in jewel_positions:
            pygame.draw.circle(surface, detail_color, (jewel_x, jewel_y), jewel_radius)
            pygame.draw.circle(
                surface, outline_color, (jewel_x, jewel_y), jewel_radius, 1
            )

    def _draw_rook(self, surface: pygame.Surface, color: str):
        """Draw a rook piece with enhanced details."""
        x, y = self.center_offset, self.center_offset
        size = self.piece_size

        fill_color = self.WHITE_PIECE if color == "w" else self.BLACK_PIECE
        shadow_color = (
            self.WHITE_PIECE_SHADOW if color == "w" else self.BLACK_PIECE_SHADOW
        )
        highlight_color = (
            self.WHITE_PIECE_HIGHLIGHT if color == "w" else self.BLACK_PIECE_HIGHLIGHT
        )
        outline_color = self.WHITE_OUTLINE if color == "w" else self.BLACK_OUTLINE
        detail_color = self.WHITE_DETAIL if color == "w" else self.BLACK_DETAIL

        # Base with shadow
        base_width = int(size * 0.75)
        base_height = int(size * 0.16)
        base_x = x + (size - base_width) // 2
        base_y = y + size - base_height - int(size * 0.04)

        # Shadow
        pygame.draw.rect(
            surface, shadow_color, (base_x + 2, base_y + 2, base_width, base_height)
        )
        # Main base
        pygame.draw.rect(surface, fill_color, (base_x, base_y, base_width, base_height))
        # Highlight
        pygame.draw.rect(
            surface, highlight_color, (base_x, base_y, base_width, base_height // 3)
        )
        pygame.draw.rect(
            surface, outline_color, (base_x, base_y, base_width, base_height), 2
        )

        # Body with gradient
        body_width = int(size * 0.55)
        body_height = int(size * 0.42)
        body_x = x + (size - body_width) // 2
        body_y = base_y - body_height

        # Shadow
        pygame.draw.rect(
            surface, shadow_color, (body_x + 2, body_y + 2, body_width, body_height)
        )
        # Main body
        pygame.draw.rect(surface, fill_color, (body_x, body_y, body_width, body_height))
        # Highlight
        pygame.draw.rect(
            surface, highlight_color, (body_x, body_y, body_width, body_height // 3)
        )
        pygame.draw.rect(
            surface, outline_color, (body_x, body_y, body_width, body_height), 2
        )

        # Top battlements with 3D effect
        battlement_width = int(size * 0.12)
        battlement_height = int(size * 0.18)
        battlement_spacing = int(size * 0.16)

        for i in range(3):
            battlement_x = body_x + i * battlement_spacing
            # Shadow
            pygame.draw.rect(
                surface,
                shadow_color,
                (
                    battlement_x + 1,
                    body_y - battlement_height + 1,
                    battlement_width,
                    battlement_height,
                ),
            )
            # Main battlement
            pygame.draw.rect(
                surface,
                fill_color,
                (
                    battlement_x,
                    body_y - battlement_height,
                    battlement_width,
                    battlement_height,
                ),
            )
            # Highlight
            pygame.draw.rect(
                surface,
                highlight_color,
                (
                    battlement_x,
                    body_y - battlement_height,
                    battlement_width,
                    battlement_height // 3,
                ),
            )
            pygame.draw.rect(
                surface,
                outline_color,
                (
                    battlement_x,
                    body_y - battlement_height,
                    battlement_width,
                    battlement_height,
                ),
                1,
            )

        # Cross detail with gold accent
        cross_x = body_x + body_width // 2
        cross_y = body_y + body_height // 2
        cross_size = int(size * 0.16)
        cross_thickness = 4

        # Cross shadow
        pygame.draw.line(
            surface,
            shadow_color,
            (cross_x - cross_size + 1, cross_y + 1),
            (cross_x + cross_size + 1, cross_y + 1),
            cross_thickness,
        )
        pygame.draw.line(
            surface,
            shadow_color,
            (cross_x + 1, cross_y - cross_size + 1),
            (cross_x + 1, cross_y + cross_size + 1),
            cross_thickness,
        )

        # Main cross
        pygame.draw.line(
            surface,
            self.GOLD,
            (cross_x - cross_size, cross_y),
            (cross_x + cross_size, cross_y),
            cross_thickness,
        )
        pygame.draw.line(
            surface,
            self.GOLD,
            (cross_x, cross_y - cross_size),
            (cross_x, cross_y + cross_size),
            cross_thickness,
        )

        # Cross outline
        pygame.draw.line(
            surface,
            self.GOLD_SHADOW,
            (cross_x - cross_size, cross_y),
            (cross_x + cross_size, cross_y),
            1,
        )
        pygame.draw.line(
            surface,
            self.GOLD_SHADOW,
            (cross_x, cross_y - cross_size),
            (cross_x, cross_y + cross_size),
            1,
        )

    def _draw_knight(self, surface: pygame.Surface, color: str):
        """Draw a knight piece with enhanced details."""
        x, y = self.center_offset, self.center_offset
        size = self.piece_size

        fill_color = self.WHITE_PIECE if color == "w" else self.BLACK_PIECE
        shadow_color = (
            self.WHITE_PIECE_SHADOW if color == "w" else self.BLACK_PIECE_SHADOW
        )
        highlight_color = (
            self.WHITE_PIECE_HIGHLIGHT if color == "w" else self.BLACK_PIECE_HIGHLIGHT
        )
        outline_color = self.WHITE_OUTLINE if color == "w" else self.BLACK_OUTLINE
        detail_color = self.WHITE_DETAIL if color == "w" else self.BLACK_DETAIL

        # Base with shadow
        base_width = int(size * 0.65)
        base_height = int(size * 0.16)
        base_x = x + (size - base_width) // 2
        base_y = y + size - base_height - int(size * 0.04)

        # Shadow
        pygame.draw.rect(
            surface, shadow_color, (base_x + 2, base_y + 2, base_width, base_height)
        )
        # Main base
        pygame.draw.rect(surface, fill_color, (base_x, base_y, base_width, base_height))
        # Highlight
        pygame.draw.rect(
            surface, highlight_color, (base_x, base_y, base_width, base_height // 3)
        )
        pygame.draw.rect(
            surface, outline_color, (base_x, base_y, base_width, base_height), 2
        )

        # Body (horse shape) with 3D effect
        body_points = [
            (base_x + base_width // 2, base_y - int(size * 0.42)),  # Top
            (
                base_x + base_width // 2 - int(size * 0.16),
                base_y - int(size * 0.22),
            ),  # Left curve
            (base_x + int(size * 0.12), base_y - int(size * 0.12)),  # Left bottom
            (
                base_x + base_width - int(size * 0.12),
                base_y - int(size * 0.12),
            ),  # Right bottom
            (
                base_x + base_width // 2 + int(size * 0.16),
                base_y - int(size * 0.22),
            ),  # Right curve
        ]

        # Shadow
        shadow_points = [(px + 2, py + 2) for px, py in body_points]
        pygame.draw.polygon(surface, shadow_color, shadow_points)
        # Main body
        pygame.draw.polygon(surface, fill_color, body_points)
        # Highlight
        highlight_points = [(px - 2, py - 2) for px, py in body_points]
        pygame.draw.polygon(surface, highlight_color, highlight_points)
        pygame.draw.polygon(surface, outline_color, body_points, 2)

        # Head with 3D effect
        head_radius = int(size * 0.18)
        head_x = base_x + base_width // 2
        head_y = base_y - int(size * 0.48)

        # Shadow
        pygame.draw.circle(surface, shadow_color, (head_x + 2, head_y + 2), head_radius)
        # Main head
        pygame.draw.circle(surface, fill_color, (head_x, head_y), head_radius)
        # Highlight
        pygame.draw.circle(
            surface,
            highlight_color,
            (head_x - head_radius // 3, head_y - head_radius // 3),
            head_radius // 2,
        )
        pygame.draw.circle(surface, outline_color, (head_x, head_y), head_radius, 2)

        # Eye with detail
        eye_radius = int(size * 0.04)
        eye_x = head_x + int(size * 0.06)
        eye_y = head_y - int(size * 0.04)

        # Eye shadow
        pygame.draw.circle(surface, shadow_color, (eye_x + 1, eye_y + 1), eye_radius)
        # Main eye
        pygame.draw.circle(surface, detail_color, (eye_x, eye_y), eye_radius)
        # Eye highlight
        pygame.draw.circle(
            surface,
            highlight_color,
            (eye_x - eye_radius // 3, eye_y - eye_radius // 3),
            eye_radius // 3,
        )
        pygame.draw.circle(surface, outline_color, (eye_x, eye_y), eye_radius, 1)

        # Mane detail
        mane_points = [
            (head_x - head_radius // 2, head_y - head_radius // 2),
            (head_x - head_radius // 3, head_y - head_radius),
            (head_x + head_radius // 3, head_y - head_radius),
            (head_x + head_radius // 2, head_y - head_radius // 2),
        ]
        pygame.draw.polygon(surface, detail_color, mane_points)
        pygame.draw.polygon(surface, outline_color, mane_points, 1)

    def _draw_bishop(self, surface: pygame.Surface, color: str):
        """Draw a bishop piece with enhanced details."""
        x, y = self.center_offset, self.center_offset
        size = self.piece_size

        fill_color = self.WHITE_PIECE if color == "w" else self.BLACK_PIECE
        shadow_color = (
            self.WHITE_PIECE_SHADOW if color == "w" else self.BLACK_PIECE_SHADOW
        )
        highlight_color = (
            self.WHITE_PIECE_HIGHLIGHT if color == "w" else self.BLACK_PIECE_HIGHLIGHT
        )
        outline_color = self.WHITE_OUTLINE if color == "w" else self.BLACK_OUTLINE
        detail_color = self.WHITE_DETAIL if color == "w" else self.BLACK_DETAIL

        # Base with shadow
        base_width = int(size * 0.65)
        base_height = int(size * 0.16)
        base_x = x + (size - base_width) // 2
        base_y = y + size - base_height - int(size * 0.04)

        # Shadow
        pygame.draw.rect(
            surface, shadow_color, (base_x + 2, base_y + 2, base_width, base_height)
        )
        # Main base
        pygame.draw.rect(surface, fill_color, (base_x, base_y, base_width, base_height))
        # Highlight
        pygame.draw.rect(
            surface, highlight_color, (base_x, base_y, base_width, base_height // 3)
        )
        pygame.draw.rect(
            surface, outline_color, (base_x, base_y, base_width, base_height), 2
        )

        # Body (triangular) with 3D effect
        body_width = int(size * 0.45)
        body_height = int(size * 0.38)
        body_x = x + (size - body_width) // 2
        body_y = base_y - body_height

        body_points = [
            (body_x + body_width // 2, body_y),  # Top point
            (body_x, body_y + body_height),  # Bottom left
            (body_x + body_width, body_y + body_height),  # Bottom right
        ]

        # Shadow
        shadow_points = [(px + 2, py + 2) for px, py in body_points]
        pygame.draw.polygon(surface, shadow_color, shadow_points)
        # Main body
        pygame.draw.polygon(surface, fill_color, body_points)
        # Highlight
        highlight_points = [(px - 2, py - 2) for px, py in body_points]
        pygame.draw.polygon(surface, highlight_color, highlight_points)
        pygame.draw.polygon(surface, outline_color, body_points, 2)

        # Cross detail with gold accent
        cross_x = body_x + body_width // 2
        cross_y = body_y + body_height // 2
        cross_size = int(size * 0.14)
        cross_thickness = 4

        # Cross shadow
        pygame.draw.line(
            surface,
            shadow_color,
            (cross_x - cross_size + 1, cross_y + 1),
            (cross_x + cross_size + 1, cross_y + 1),
            cross_thickness,
        )
        pygame.draw.line(
            surface,
            shadow_color,
            (cross_x + 1, cross_y - cross_size + 1),
            (cross_x + 1, cross_y + cross_size + 1),
            cross_thickness,
        )

        # Main cross
        pygame.draw.line(
            surface,
            self.GOLD,
            (cross_x - cross_size, cross_y),
            (cross_x + cross_size, cross_y),
            cross_thickness,
        )
        pygame.draw.line(
            surface,
            self.GOLD,
            (cross_x, cross_y - cross_size),
            (cross_x, cross_y + cross_size),
            cross_thickness,
        )

        # Cross outline
        pygame.draw.line(
            surface,
            self.GOLD_SHADOW,
            (cross_x - cross_size, cross_y),
            (cross_x + cross_size, cross_y),
            1,
        )
        pygame.draw.line(
            surface,
            self.GOLD_SHADOW,
            (cross_x, cross_y - cross_size),
            (cross_x, cross_y + cross_size),
            1,
        )

        # Slit detail
        slit_width = int(size * 0.025)
        slit_height = int(size * 0.18)
        slit_x = cross_x - slit_width // 2
        slit_y = cross_y - slit_height // 2

        # Slit shadow
        pygame.draw.rect(
            surface, shadow_color, (slit_x + 1, slit_y + 1, slit_width, slit_height)
        )
        # Main slit
        pygame.draw.rect(
            surface, detail_color, (slit_x, slit_y, slit_width, slit_height)
        )
        pygame.draw.rect(
            surface, outline_color, (slit_x, slit_y, slit_width, slit_height), 1
        )

    def _draw_queen(self, surface: pygame.Surface, color: str):
        """Draw a queen piece with enhanced details."""
        x, y = self.center_offset, self.center_offset
        size = self.piece_size

        fill_color = self.WHITE_PIECE if color == "w" else self.BLACK_PIECE
        shadow_color = (
            self.WHITE_PIECE_SHADOW if color == "w" else self.BLACK_PIECE_SHADOW
        )
        highlight_color = (
            self.WHITE_PIECE_HIGHLIGHT if color == "w" else self.BLACK_PIECE_HIGHLIGHT
        )
        outline_color = self.WHITE_OUTLINE if color == "w" else self.BLACK_OUTLINE
        detail_color = self.WHITE_DETAIL if color == "w" else self.BLACK_DETAIL

        # Base with shadow
        base_width = int(size * 0.75)
        base_height = int(size * 0.16)
        base_x = x + (size - base_width) // 2
        base_y = y + size - base_height - int(size * 0.04)

        # Shadow
        pygame.draw.rect(
            surface, shadow_color, (base_x + 2, base_y + 2, base_width, base_height)
        )
        # Main base
        pygame.draw.rect(surface, fill_color, (base_x, base_y, base_width, base_height))
        # Highlight
        pygame.draw.rect(
            surface, highlight_color, (base_x, base_y, base_width, base_height // 3)
        )
        pygame.draw.rect(
            surface, outline_color, (base_x, base_y, base_width, base_height), 2
        )

        # Body with gradient
        body_width = int(size * 0.55)
        body_height = int(size * 0.38)
        body_x = x + (size - body_width) // 2
        body_y = base_y - body_height

        # Shadow
        pygame.draw.rect(
            surface, shadow_color, (body_x + 2, body_y + 2, body_width, body_height)
        )
        # Main body
        pygame.draw.rect(surface, fill_color, (body_x, body_y, body_width, body_height))
        # Highlight
        pygame.draw.rect(
            surface, highlight_color, (body_x, body_y, body_width, body_height // 3)
        )
        pygame.draw.rect(
            surface, outline_color, (body_x, body_y, body_width, body_height), 2
        )

        # Crown with 3D effect
        crown_width = int(size * 0.45)
        crown_height = int(size * 0.22)
        crown_x = x + (size - crown_width) // 2
        crown_y = body_y - crown_height

        # Crown shadow
        pygame.draw.rect(
            surface, shadow_color, (crown_x + 2, crown_y + 2, crown_width, crown_height)
        )
        # Crown base
        pygame.draw.rect(
            surface, fill_color, (crown_x, crown_y, crown_width, crown_height)
        )
        # Crown highlight
        pygame.draw.rect(
            surface, highlight_color, (crown_x, crown_y, crown_width, crown_height // 3)
        )
        pygame.draw.rect(
            surface, outline_color, (crown_x, crown_y, crown_width, crown_height), 2
        )

        # Crown jewels with gold accents
        jewel_radius = int(size * 0.035)
        jewel_positions = [
            (crown_x + crown_width // 4, crown_y + crown_height // 2),
            (crown_x + crown_width // 2, crown_y + crown_height // 3),
            (crown_x + 3 * crown_width // 4, crown_y + crown_height // 2),
        ]

        for jewel_x, jewel_y in jewel_positions:
            # Jewel shadow
            pygame.draw.circle(
                surface, shadow_color, (jewel_x + 1, jewel_y + 1), jewel_radius
            )
            # Main jewel
            pygame.draw.circle(surface, self.GOLD, (jewel_x, jewel_y), jewel_radius)
            # Jewel highlight
            pygame.draw.circle(
                surface,
                highlight_color,
                (jewel_x - jewel_radius // 3, jewel_y - jewel_radius // 3),
                jewel_radius // 3,
            )
            pygame.draw.circle(
                surface, self.GOLD_SHADOW, (jewel_x, jewel_y), jewel_radius, 1
            )

        # Crown spikes
        spike_width = int(size * 0.08)
        spike_height = int(size * 0.12)
        spike_positions = [
            (crown_x + crown_width // 6, crown_y - spike_height // 2),
            (crown_x + crown_width // 2, crown_y - spike_height),
            (crown_x + 5 * crown_width // 6, crown_y - spike_height // 2),
        ]

        for spike_x, spike_y in spike_positions:
            spike_points = [
                (spike_x, spike_y + spike_height),
                (spike_x - spike_width // 2, spike_y),
                (spike_x + spike_width // 2, spike_y),
            ]
            # Spike shadow
            shadow_points = [(px + 1, py + 1) for px, py in spike_points]
            pygame.draw.polygon(surface, shadow_color, shadow_points)
            # Main spike
            pygame.draw.polygon(surface, fill_color, spike_points)
            pygame.draw.polygon(surface, outline_color, spike_points, 1)

    def _draw_king(self, surface: pygame.Surface, color: str):
        """Draw a king piece with enhanced details."""
        x, y = self.center_offset, self.center_offset
        size = self.piece_size

        fill_color = self.WHITE_PIECE if color == "w" else self.BLACK_PIECE
        shadow_color = (
            self.WHITE_PIECE_SHADOW if color == "w" else self.BLACK_PIECE_SHADOW
        )
        highlight_color = (
            self.WHITE_PIECE_HIGHLIGHT if color == "w" else self.BLACK_PIECE_HIGHLIGHT
        )
        outline_color = self.WHITE_OUTLINE if color == "w" else self.BLACK_OUTLINE
        detail_color = self.WHITE_DETAIL if color == "w" else self.BLACK_DETAIL

        # Base with shadow
        base_width = int(size * 0.75)
        base_height = int(size * 0.16)
        base_x = x + (size - base_width) // 2
        base_y = y + size - base_height - int(size * 0.04)

        # Shadow
        pygame.draw.rect(
            surface, shadow_color, (base_x + 2, base_y + 2, base_width, base_height)
        )
        # Main base
        pygame.draw.rect(surface, fill_color, (base_x, base_y, base_width, base_height))
        # Highlight
        pygame.draw.rect(
            surface, highlight_color, (base_x, base_y, base_width, base_height // 3)
        )
        pygame.draw.rect(
            surface, outline_color, (base_x, base_y, base_width, base_height), 2
        )

        # Body with gradient
        body_width = int(size * 0.55)
        body_height = int(size * 0.38)
        body_x = x + (size - body_width) // 2
        body_y = base_y - body_height

        # Shadow
        pygame.draw.rect(
            surface, shadow_color, (body_x + 2, body_y + 2, body_width, body_height)
        )
        # Main body
        pygame.draw.rect(surface, fill_color, (body_x, body_y, body_width, body_height))
        # Highlight
        pygame.draw.rect(
            surface, highlight_color, (body_x, body_y, body_width, body_height // 3)
        )
        pygame.draw.rect(
            surface, outline_color, (body_x, body_y, body_width, body_height), 2
        )

        # Crown with 3D effect
        crown_width = int(size * 0.45)
        crown_height = int(size * 0.22)
        crown_x = x + (size - crown_width) // 2
        crown_y = body_y - crown_height

        # Crown shadow
        pygame.draw.rect(
            surface, shadow_color, (crown_x + 2, crown_y + 2, crown_width, crown_height)
        )
        # Crown base
        pygame.draw.rect(
            surface, fill_color, (crown_x, crown_y, crown_width, crown_height)
        )
        # Crown highlight
        pygame.draw.rect(
            surface, highlight_color, (crown_x, crown_y, crown_width, crown_height // 3)
        )
        pygame.draw.rect(
            surface, outline_color, (crown_x, crown_y, crown_width, crown_height), 2
        )

        # Cross on crown with gold accent
        cross_x = crown_x + crown_width // 2
        cross_y = crown_y + crown_height // 2
        cross_size = int(size * 0.1)
        cross_thickness = 4

        # Cross shadow
        pygame.draw.line(
            surface,
            shadow_color,
            (cross_x - cross_size + 1, cross_y + 1),
            (cross_x + cross_size + 1, cross_y + 1),
            cross_thickness,
        )
        pygame.draw.line(
            surface,
            shadow_color,
            (cross_x + 1, cross_y - cross_size + 1),
            (cross_x + 1, cross_y + cross_size + 1),
            cross_thickness,
        )

        # Main cross
        pygame.draw.line(
            surface,
            self.GOLD,
            (cross_x - cross_size, cross_y),
            (cross_x + cross_size, cross_y),
            cross_thickness,
        )
        pygame.draw.line(
            surface,
            self.GOLD,
            (cross_x, cross_y - cross_size),
            (cross_x, cross_y + cross_size),
            cross_thickness,
        )

        # Cross outline
        pygame.draw.line(
            surface,
            self.GOLD_SHADOW,
            (cross_x - cross_size, cross_y),
            (cross_x + cross_size, cross_y),
            1,
        )
        pygame.draw.line(
            surface,
            self.GOLD_SHADOW,
            (cross_x, cross_y - cross_size),
            (cross_x, cross_y + cross_size),
            1,
        )

        # Crown jewels with gold accents
        jewel_radius = int(size * 0.025)
        jewel_positions = [
            (crown_x + crown_width // 4, crown_y + crown_height // 2),
            (crown_x + 3 * crown_width // 4, crown_y + crown_height // 2),
        ]

        for jewel_x, jewel_y in jewel_positions:
            # Jewel shadow
            pygame.draw.circle(
                surface, shadow_color, (jewel_x + 1, jewel_y + 1), jewel_radius
            )
            # Main jewel
            pygame.draw.circle(surface, self.GOLD, (jewel_x, jewel_y), jewel_radius)
            # Jewel highlight
            pygame.draw.circle(
                surface,
                highlight_color,
                (jewel_x - jewel_radius // 3, jewel_y - jewel_radius // 3),
                jewel_radius // 3,
            )
            pygame.draw.circle(
                surface, self.GOLD_SHADOW, (jewel_x, jewel_y), jewel_radius, 1
            )

        # Crown spikes
        spike_width = int(size * 0.06)
        spike_height = int(size * 0.15)
        spike_positions = [
            (crown_x + crown_width // 4, crown_y - spike_height // 2),
            (crown_x + crown_width // 2, crown_y - spike_height),
            (crown_x + 3 * crown_width // 4, crown_y - spike_height // 2),
        ]

        for spike_x, spike_y in spike_positions:
            spike_points = [
                (spike_x, spike_y + spike_height),
                (spike_x - spike_width // 2, spike_y),
                (spike_x + spike_width // 2, spike_y),
            ]
            # Spike shadow
            shadow_points = [(px + 1, py + 1) for px, py in spike_points]
            pygame.draw.polygon(surface, shadow_color, shadow_points)
            # Main spike
            pygame.draw.polygon(surface, fill_color, spike_points)
            pygame.draw.polygon(surface, outline_color, spike_points, 1)
