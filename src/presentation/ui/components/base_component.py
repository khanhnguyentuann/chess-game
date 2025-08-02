"""
Base Component - Foundation for all UI components
Provides common functionality and consistent interface.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple

import pygame

from ....shared.types.enums import UIColors


class BaseComponent(ABC):
    """Base class for all UI components."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        visible: bool = True,
        enabled: bool = True,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = visible
        self.enabled = enabled
        self.hovered = False
        self.pressed = False
        self.focused = False
        
        # Animation properties
        self.animation_progress = 0.0
        self.target_animation = 0.0
        self.animation_speed = 0.15
        
        # Style properties
        self.style = self._get_default_style()
        
    def _get_default_style(self) -> Dict[str, Any]:
        """Get default style for the component."""
        return {
            'background_color': UIColors.LIGHT_GRAY,
            'border_color': UIColors.GRAY,
            'text_color': UIColors.BLACK,
            'border_width': 1,
            'border_radius': 4,
            'padding': 8,
            'font_size': 16,
        }
    
    def set_style(self, style: Dict[str, Any]) -> None:
        """Update component style."""
        self.style.update(style)
    
    def update(self, dt: float) -> None:
        """Update component state."""
        # Smooth animation
        if abs(self.target_animation - self.animation_progress) > 0.01:
            diff = self.target_animation - self.animation_progress
            self.animation_progress += diff * self.animation_speed
        else:
            self.animation_progress = self.target_animation
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame event.
        
        Returns:
            True if event was handled, False otherwise
        """
        if not self.visible or not self.enabled:
            return False
            
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
            self.target_animation = 1.0 if self.hovered else 0.0
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.pressed = True
                self.focused = True
                return self._on_click(event.pos)
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.pressed = False
                
        return False
    
    @abstractmethod
    def render(self, surface: pygame.Surface) -> None:
        """Render the component."""
        pass
    
    def _on_click(self, pos: Tuple[int, int]) -> bool:
        """Handle click event. Override in subclasses."""
        return False
    
    def _draw_rounded_rect(
        self, 
        surface: pygame.Surface, 
        color: Tuple[int, int, int], 
        rect: pygame.Rect, 
        radius: int
    ) -> None:
        """Draw a rounded rectangle."""
        if radius <= 0:
            pygame.draw.rect(surface, color, rect)
            return
            
        # Draw rounded rectangle using circles and rectangles
        pygame.draw.circle(surface, color, (rect.left + radius, rect.top + radius), radius)
        pygame.draw.circle(surface, color, (rect.right - radius, rect.top + radius), radius)
        pygame.draw.circle(surface, color, (rect.left + radius, rect.bottom - radius), radius)
        pygame.draw.circle(surface, color, (rect.right - radius, rect.bottom - radius), radius)
        
        pygame.draw.rect(surface, color, (rect.left + radius, rect.top, rect.width - 2 * radius, rect.height))
        pygame.draw.rect(surface, color, (rect.left, rect.top + radius, rect.width, rect.height - 2 * radius))
    
    def _interpolate_color(
        self, 
        color1: Tuple[int, int, int], 
        color2: Tuple[int, int, int], 
        t: float
    ) -> Tuple[int, int, int]:
        """Interpolate between two colors."""
        t = max(0.0, min(1.0, t))
        return (
            int(color1[0] + (color2[0] - color1[0]) * t),
            int(color1[1] + (color2[1] - color1[1]) * t),
            int(color1[2] + (color2[2] - color1[2]) * t),
        )