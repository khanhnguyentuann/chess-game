"""
Theme Manager - Centralized theme system for consistent styling.
"""

from typing import Any, Dict, Optional, Tuple

from ....shared.types.enums import UIColors


class Theme:
    """Theme definition with colors, fonts, and styling properties."""
    
    def __init__(self, name: str, colors: Dict[str, Any], properties: Dict[str, Any]):
        self.name = name
        self.colors = colors
        self.properties = properties
    
    def get_color(self, key: str, default: Tuple[int, int, int] = UIColors.WHITE) -> Tuple[int, int, int]:
        """Get a color from the theme."""
        return self.colors.get(key, default)
    
    def get_property(self, key: str, default: Any = None) -> Any:
        """Get a property from the theme."""
        return self.properties.get(key, default)


class ThemeManager:
    """Manages application themes and provides theme switching."""
    
    def __init__(self):
        self.themes: Dict[str, Theme] = {}
        self.current_theme: Optional[Theme] = None
        self._load_default_themes()
    
    def _load_default_themes(self) -> None:
        """Load default themes."""
        
        # Modern Dark Theme
        dark_theme = Theme(
            name="dark",
            colors={
                'primary': (70, 130, 180),      # Steel blue
                'primary_hover': (100, 149, 237), # Cornflower blue
                'primary_pressed': (65, 105, 225), # Royal blue
                'secondary': (108, 117, 125),    # Gray
                'success': (40, 167, 69),        # Green
                'danger': (220, 53, 69),         # Red
                'warning': (255, 193, 7),        # Yellow
                'info': (23, 162, 184),          # Cyan
                'light': (248, 249, 250),        # Light gray
                'dark': (33, 37, 41),            # Dark gray
                'background': (18, 18, 18),      # Very dark
                'surface': (28, 28, 28),         # Dark surface
                'surface_variant': (45, 45, 45), # Lighter surface
                'on_background': (255, 255, 255), # White text
                'on_surface': (255, 255, 255),   # White text
                'border': (80, 80, 80),          # Border color
                'shadow': (0, 0, 0, 120),        # Shadow with alpha
                
                # Chess-specific colors
                'light_square': (240, 217, 181),  # Light wood
                'dark_square': (181, 136, 99),    # Dark wood
                'highlight': (255, 255, 0, 150),  # Yellow highlight
                'selected': (124, 252, 0, 180),   # Green selection
                'valid_move': (144, 238, 144, 120), # Light green
                'last_move': (255, 165, 0, 100),  # Orange
                'check': (255, 69, 0, 150),       # Red orange
            },
            properties={
                'border_radius': 8,
                'shadow_offset': 4,
                'animation_speed': 0.15,
                'font_size_small': 14,
                'font_size_normal': 16,
                'font_size_large': 20,
                'font_size_title': 24,
                'padding_small': 4,
                'padding_normal': 8,
                'padding_large': 16,
            }
        )
        
        # Modern Light Theme
        light_theme = Theme(
            name="light",
            colors={
                'primary': (0, 123, 255),        # Blue
                'primary_hover': (0, 86, 179),   # Darker blue
                'primary_pressed': (0, 69, 134), # Even darker blue
                'secondary': (108, 117, 125),    # Gray
                'success': (40, 167, 69),        # Green
                'danger': (220, 53, 69),         # Red
                'warning': (255, 193, 7),        # Yellow
                'info': (23, 162, 184),          # Cyan
                'light': (248, 249, 250),        # Light gray
                'dark': (33, 37, 41),            # Dark gray
                'background': (255, 255, 255),   # White
                'surface': (248, 249, 250),      # Light surface
                'surface_variant': (233, 236, 239), # Darker surface
                'on_background': (33, 37, 41),   # Dark text
                'on_surface': (33, 37, 41),      # Dark text
                'border': (206, 212, 218),       # Light border
                'shadow': (0, 0, 0, 80),         # Lighter shadow
                
                # Chess-specific colors
                'light_square': (240, 217, 181),  # Light wood
                'dark_square': (181, 136, 99),    # Dark wood
                'highlight': (255, 255, 0, 150),  # Yellow highlight
                'selected': (124, 252, 0, 180),   # Green selection
                'valid_move': (144, 238, 144, 120), # Light green
                'last_move': (255, 165, 0, 100),  # Orange
                'check': (255, 69, 0, 150),       # Red orange
            },
            properties={
                'border_radius': 6,
                'shadow_offset': 2,
                'animation_speed': 0.12,
                'font_size_small': 14,
                'font_size_normal': 16,
                'font_size_large': 20,
                'font_size_title': 24,
                'padding_small': 4,
                'padding_normal': 8,
                'padding_large': 16,
            }
        )
        
        # Elegant Theme
        elegant_theme = Theme(
            name="elegant",
            colors={
                'primary': (139, 69, 19),        # Saddle brown
                'primary_hover': (160, 82, 45),  # Lighter brown
                'primary_pressed': (101, 67, 33), # Darker brown
                'secondary': (105, 105, 105),    # Dim gray
                'success': (85, 107, 47),        # Dark olive green
                'danger': (178, 34, 34),         # Fire brick
                'warning': (218, 165, 32),       # Golden rod
                'info': (70, 130, 180),          # Steel blue
                'light': (245, 245, 220),        # Beige
                'dark': (47, 79, 79),            # Dark slate gray
                'background': (25, 25, 25),      # Very dark
                'surface': (40, 40, 40),         # Dark surface
                'surface_variant': (60, 60, 60), # Lighter surface
                'on_background': (245, 245, 220), # Beige text
                'on_surface': (245, 245, 220),   # Beige text
                'border': (139, 69, 19),         # Brown border
                'shadow': (0, 0, 0, 150),        # Strong shadow
                
                # Chess-specific colors
                'light_square': (245, 222, 179),  # Wheat
                'dark_square': (139, 69, 19),     # Saddle brown
                'highlight': (255, 215, 0, 180),  # Gold highlight
                'selected': (218, 165, 32, 200),  # Golden rod selection
                'valid_move': (154, 205, 50, 120), # Yellow green
                'last_move': (255, 140, 0, 120),  # Dark orange
                'check': (220, 20, 60, 180),      # Crimson
            },
            properties={
                'border_radius': 12,
                'shadow_offset': 6,
                'animation_speed': 0.18,
                'font_size_small': 14,
                'font_size_normal': 16,
                'font_size_large': 20,
                'font_size_title': 26,
                'padding_small': 6,
                'padding_normal': 12,
                'padding_large': 20,
            }
        )
        
        self.register_theme(dark_theme)
        self.register_theme(light_theme)
        self.register_theme(elegant_theme)
        
        # Set default theme
        self.set_theme("dark")
    
    def register_theme(self, theme: Theme) -> None:
        """Register a new theme."""
        self.themes[theme.name] = theme
    
    def set_theme(self, theme_name: str) -> bool:
        """Set the current theme."""
        if theme_name in self.themes:
            self.current_theme = self.themes[theme_name]
            return True
        return False
    
    def get_current_theme(self) -> Optional[Theme]:
        """Get the current theme."""
        return self.current_theme
    
    def get_color(self, key: str, default: Tuple[int, int, int] = UIColors.WHITE) -> Tuple[int, int, int]:
        """Get a color from the current theme."""
        if self.current_theme:
            return self.current_theme.get_color(key, default)
        return default
    
    def get_property(self, key: str, default: Any = None) -> Any:
        """Get a property from the current theme."""
        if self.current_theme:
            return self.current_theme.get_property(key, default)
        return default
    
    def list_themes(self) -> list:
        """Get list of available theme names."""
        return list(self.themes.keys())


# Global theme manager instance
theme_manager = ThemeManager()