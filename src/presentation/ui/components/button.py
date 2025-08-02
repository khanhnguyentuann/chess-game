"""
Modern Button Component with animations and hover effects.
"""

from typing import Any, Callable, Dict, Optional, Tuple

import pygame

from ....shared.types.enums import UIColors
from .base_component import BaseComponent


class Button(BaseComponent):
    """Modern button with hover animations and customizable styling."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str = "",
        callback: Optional[Callable] = None,
        icon: Optional[pygame.Surface] = None,
        **kwargs
    ):
        super().__init__(x, y, width, height, **kwargs)
        self.text = text
        self.callback = callback
        self.icon = icon
        
        # Button-specific style
        self.style.update({
            'background_color': (70, 130, 180),  # Steel blue
            'hover_color': (100, 149, 237),      # Cornflower blue
            'pressed_color': (65, 105, 225),     # Royal blue
            'text_color': UIColors.WHITE,
            'border_radius': 8,
            'shadow_offset': 2,
            'shadow_color': (0, 0, 0, 50),
        })
        
        # Font
        self.font = pygame.font.Font(None, self.style['font_size'] + 4)
        
    def _get_current_color(self) -> Tuple[int, int, int]:
        """Get current background color based on state."""
        base_color = self.style['background_color']
        hover_color = self.style['hover_color']
        pressed_color = self.style['pressed_color']
        
        if self.pressed:
            return pressed_color
        elif self.hovered:
            return self._interpolate_color(base_color, hover_color, self.animation_progress)
        else:
            return base_color
    
    def render(self, surface: pygame.Surface) -> None:
        """Render the button with modern styling."""
        if not self.visible:
            return
        
        # Draw shadow
        shadow_rect = self.rect.copy()
        shadow_rect.x += self.style['shadow_offset']
        shadow_rect.y += self.style['shadow_offset']
        
        # Create shadow surface with alpha
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        self._draw_rounded_rect(
            shadow_surface, 
            self.style['shadow_color'], 
            pygame.Rect(0, 0, shadow_rect.width, shadow_rect.height),
            self.style['border_radius']
        )
        surface.blit(shadow_surface, shadow_rect.topleft)
        
        # Draw button background
        current_color = self._get_current_color()
        self._draw_rounded_rect(surface, current_color, self.rect, self.style['border_radius'])
        
        # Draw border if specified
        if self.style.get('border_width', 0) > 0:
            pygame.draw.rect(
                surface, 
                self.style['border_color'], 
                self.rect, 
                self.style['border_width']
            )
        
        # Draw icon and text
        content_rect = self.rect.inflate(-self.style['padding'] * 2, -self.style['padding'] * 2)
        
        if self.icon and self.text:
            # Icon + text layout
            icon_rect = self.icon.get_rect()
            icon_rect.centery = content_rect.centery
            icon_rect.left = content_rect.left
            
            text_surface = self.font.render(self.text, True, self.style['text_color'])
            text_rect = text_surface.get_rect()
            text_rect.centery = content_rect.centery
            text_rect.left = icon_rect.right + 8
            
            surface.blit(self.icon, icon_rect)
            surface.blit(text_surface, text_rect)
            
        elif self.icon:
            # Icon only
            icon_rect = self.icon.get_rect(center=content_rect.center)
            surface.blit(self.icon, icon_rect)
            
        elif self.text:
            # Text only
            text_surface = self.font.render(self.text, True, self.style['text_color'])
            text_rect = text_surface.get_rect(center=content_rect.center)
            surface.blit(text_surface, text_rect)
    
    def _on_click(self, pos: Tuple[int, int]) -> bool:
        """Handle button click."""
        if self.callback:
            self.callback()
        return True


class IconButton(Button):
    """Icon-only button with circular design."""
    
    def __init__(self, x: int, y: int, size: int, icon: pygame.Surface, **kwargs):
        super().__init__(x, y, size, size, "", icon=icon, **kwargs)
        
        # Circular button style
        self.style.update({
            'border_radius': size // 2,
            'background_color': (60, 60, 60),
            'hover_color': (80, 80, 80),
            'pressed_color': (40, 40, 40),
        })


class ToggleButton(Button):
    """Toggle button that maintains on/off state."""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str = "", **kwargs):
        super().__init__(x, y, width, height, text, **kwargs)
        self.toggled = False
        
        # Toggle-specific colors
        self.style.update({
            'toggled_color': (34, 139, 34),      # Forest green
            'toggled_hover': (50, 205, 50),     # Lime green
        })
    
    def _get_current_color(self) -> Tuple[int, int, int]:
        """Get current color based on toggle state."""
        if self.toggled:
            base_color = self.style['toggled_color']
            hover_color = self.style['toggled_hover']
        else:
            base_color = self.style['background_color']
            hover_color = self.style['hover_color']
        
        if self.pressed:
            return self.style['pressed_color']
        elif self.hovered:
            return self._interpolate_color(base_color, hover_color, self.animation_progress)
        else:
            return base_color
    
    def _on_click(self, pos: Tuple[int, int]) -> bool:
        """Toggle state on click."""
        self.toggled = not self.toggled
        return super()._on_click(pos)