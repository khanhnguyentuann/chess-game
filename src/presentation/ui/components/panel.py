"""
Panel Component - Container for other UI elements.
"""

from typing import Any, Dict, List, Optional, Tuple

import pygame

from ....shared.types.enums import UIColors
from .base_component import BaseComponent


class Panel(BaseComponent):
    """Modern panel container with gradient backgrounds and shadows."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        title: str = "",
        **kwargs
    ):
        super().__init__(x, y, width, height, **kwargs)
        self.title = title
        self.children: List[BaseComponent] = []
        
        # Panel-specific style
        self.style.update({
            'background_color': (45, 45, 45),
            'gradient_end': (35, 35, 35),
            'border_color': (80, 80, 80),
            'title_color': UIColors.WHITE,
            'border_radius': 12,
            'border_width': 1,
            'shadow_offset': 4,
            'shadow_color': (0, 0, 0, 100),
            'title_height': 40,
        })
        
        # Fonts
        self.title_font = pygame.font.Font(None, 24)
        
    def add_child(self, child: BaseComponent) -> None:
        """Add a child component."""
        self.children.append(child)
    
    def remove_child(self, child: BaseComponent) -> None:
        """Remove a child component."""
        if child in self.children:
            self.children.remove(child)
    
    def update(self, dt: float) -> None:
        """Update panel and all children."""
        super().update(dt)
        for child in self.children:
            child.update(dt)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events for panel and children."""
        if not self.visible or not self.enabled:
            return False
        
        # Let children handle events first
        for child in reversed(self.children):  # Reverse for proper z-order
            if child.handle_event(event):
                return True
        
        return super().handle_event(event)
    
    def render(self, surface: pygame.Surface) -> None:
        """Render panel with gradient background and children."""
        if not self.visible:
            return
        
        # Draw shadow
        shadow_rect = self.rect.copy()
        shadow_rect.x += self.style['shadow_offset']
        shadow_rect.y += self.style['shadow_offset']
        
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        self._draw_rounded_rect(
            shadow_surface,
            self.style['shadow_color'],
            pygame.Rect(0, 0, shadow_rect.width, shadow_rect.height),
            self.style['border_radius']
        )
        surface.blit(shadow_surface, shadow_rect.topleft)
        
        # Draw gradient background
        self._draw_gradient_background(surface)
        
        # Draw border
        if self.style['border_width'] > 0:
            pygame.draw.rect(
                surface,
                self.style['border_color'],
                self.rect,
                self.style['border_width']
            )
        
        # Draw title
        if self.title:
            self._draw_title(surface)
        
        # Render children
        for child in self.children:
            child.render(surface)
    
    def _draw_gradient_background(self, surface: pygame.Surface) -> None:
        """Draw gradient background."""
        start_color = self.style['background_color']
        end_color = self.style['gradient_end']
        
        # Create gradient surface
        gradient_surface = pygame.Surface((self.rect.width, self.rect.height))
        
        for y in range(self.rect.height):
            t = y / self.rect.height
            color = self._interpolate_color(start_color, end_color, t)
            pygame.draw.line(gradient_surface, color, (0, y), (self.rect.width, y))
        
        # Apply rounded corners by creating a mask
        mask_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self._draw_rounded_rect(
            mask_surface,
            (255, 255, 255, 255),
            pygame.Rect(0, 0, self.rect.width, self.rect.height),
            self.style['border_radius']
        )
        
        # Apply mask to gradient
        gradient_surface.set_alpha(255)
        gradient_surface = gradient_surface.convert_alpha()
        
        # Blit with mask effect (simplified approach)
        surface.blit(gradient_surface, self.rect.topleft)
    
    def _draw_title(self, surface: pygame.Surface) -> None:
        """Draw panel title."""
        title_surface = self.title_font.render(self.title, True, self.style['title_color'])
        title_rect = title_surface.get_rect()
        title_rect.centerx = self.rect.centerx
        title_rect.y = self.rect.y + 12
        
        surface.blit(title_surface, title_rect)


class InfoPanel(Panel):
    """Specialized panel for displaying game information."""
    
    def __init__(self, x: int, y: int, width: int, height: int, **kwargs):
        super().__init__(x, y, width, height, "Game Info", **kwargs)
        
        self.info_items: Dict[str, str] = {}
        self.info_font = pygame.font.Font(None, 20)
        
        # Info panel specific styling
        self.style.update({
            'background_color': (30, 30, 30),
            'gradient_end': (20, 20, 20),
            'info_color': (200, 200, 200),
            'label_color': (150, 150, 150),
        })
    
    def set_info(self, key: str, value: str) -> None:
        """Set an info item."""
        self.info_items[key] = value
    
    def render(self, surface: pygame.Surface) -> None:
        """Render info panel with information items."""
        super().render(surface)
        
        if not self.visible:
            return
        
        # Draw info items
        y_offset = self.rect.y + self.style['title_height'] + 10
        line_height = 25
        
        for key, value in self.info_items.items():
            # Draw label
            label_surface = self.info_font.render(f"{key}:", True, self.style['label_color'])
            surface.blit(label_surface, (self.rect.x + 15, y_offset))
            
            # Draw value
            value_surface = self.info_font.render(str(value), True, self.style['info_color'])
            surface.blit(value_surface, (self.rect.x + 120, y_offset))
            
            y_offset += line_height