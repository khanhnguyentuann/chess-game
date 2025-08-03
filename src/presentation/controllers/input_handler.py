"""
Input Handler
Handles user input events and converts them to game actions.
"""

import pygame
from typing import Any, Callable, Dict, List, Optional, Tuple

from ...domain.value_objects.square import Square


class InputHandler:
    """Handles user input events and converts them to game actions."""
    
    def __init__(self):
        """Initialize input handler."""
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._key_bindings: Dict[int, str] = {}
        self._mouse_bindings: Dict[int, str] = {}
        self._setup_default_bindings()
    
    def _setup_default_bindings(self) -> None:
        """Setup default key and mouse bindings."""
        # Key bindings
        self._key_bindings = {
            pygame.K_ESCAPE: "escape",
            pygame.K_RETURN: "enter",
            pygame.K_SPACE: "space",
            pygame.K_BACKSPACE: "backspace",
            pygame.K_DELETE: "delete",
            pygame.K_UP: "up",
            pygame.K_DOWN: "down",
            pygame.K_LEFT: "left",
            pygame.K_RIGHT: "right",
            pygame.K_z: "undo",
            pygame.K_y: "redo",
            pygame.K_r: "reset",
            pygame.K_s: "save",
            pygame.K_l: "load",
            pygame.K_n: "new_game",
            pygame.K_m: "menu",
            pygame.K_h: "help",
        }
        
        # Mouse bindings
        self._mouse_bindings = {
            1: "left_click",    # Left mouse button
            2: "middle_click",  # Middle mouse button
            3: "right_click",   # Right mouse button
            4: "scroll_up",     # Mouse wheel up
            5: "scroll_down",   # Mouse wheel down
        }
    
    def register_event_handler(self, event_type: str, handler: Callable) -> None:
        """
        Register an event handler.
        
        Args:
            event_type: Type of event to handle
            handler: Function to call when event occurs
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
    
    def unregister_event_handler(self, event_type: str, handler: Callable) -> bool:
        """
        Unregister an event handler.
        
        Args:
            event_type: Type of event
            handler: Function to remove
            
        Returns:
            True if handler was removed, False if not found
        """
        if event_type in self._event_handlers:
            try:
                self._event_handlers[event_type].remove(handler)
                return True
            except ValueError:
                pass
        return False
    
    def handle_events(self, events: List[pygame.event.Event]) -> List[Dict[str, Any]]:
        """
        Handle a list of pygame events.
        
        Args:
            events: List of pygame events
            
        Returns:
            List of processed event data
        """
        processed_events = []
        
        for event in events:
            event_data = self._process_event(event)
            if event_data:
                processed_events.append(event_data)
                self._notify_handlers(event_data)
        
        return processed_events
    
    def _process_event(self, event: pygame.event.Event) -> Optional[Dict[str, Any]]:
        """
        Process a single pygame event.
        
        Args:
            event: Pygame event
            
        Returns:
            Processed event data or None if not handled
        """
        if event.type == pygame.QUIT:
            return {
                "type": "quit",
                "data": {}
            }
        
        elif event.type == pygame.KEYDOWN:
            return self._process_keydown(event)
        
        elif event.type == pygame.KEYUP:
            return self._process_keyup(event)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            return self._process_mouse_down(event)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            return self._process_mouse_up(event)
        
        elif event.type == pygame.MOUSEMOTION:
            return self._process_mouse_motion(event)
        
        elif event.type == pygame.MOUSEWHEEL:
            return self._process_mouse_wheel(event)
        
        return None
    
    def _process_keydown(self, event: pygame.event.Event) -> Optional[Dict[str, Any]]:
        """Process key down event."""
        key_name = self._key_bindings.get(event.key, f"key_{event.key}")
        
        return {
            "type": "key_down",
            "data": {
                "key": event.key,
                "key_name": key_name,
                "unicode": event.unicode,
                "mod": event.mod
            }
        }
    
    def _process_keyup(self, event: pygame.event.Event) -> Optional[Dict[str, Any]]:
        """Process key up event."""
        key_name = self._key_bindings.get(event.key, f"key_{event.key}")
        
        return {
            "type": "key_up",
            "data": {
                "key": event.key,
                "key_name": key_name,
                "mod": event.mod
            }
        }
    
    def _process_mouse_down(self, event: pygame.event.Event) -> Optional[Dict[str, Any]]:
        """Process mouse button down event."""
        button_name = self._mouse_bindings.get(event.button, f"button_{event.button}")
        
        return {
            "type": "mouse_down",
            "data": {
                "button": event.button,
                "button_name": button_name,
                "pos": event.pos,
                "rel": event.rel
            }
        }
    
    def _process_mouse_up(self, event: pygame.event.Event) -> Optional[Dict[str, Any]]:
        """Process mouse button up event."""
        button_name = self._mouse_bindings.get(event.button, f"button_{event.button}")
        
        return {
            "type": "mouse_up",
            "data": {
                "button": event.button,
                "button_name": button_name,
                "pos": event.pos,
                "rel": event.rel
            }
        }
    
    def _process_mouse_motion(self, event: pygame.event.Event) -> Optional[Dict[str, Any]]:
        """Process mouse motion event."""
        return {
            "type": "mouse_motion",
            "data": {
                "pos": event.pos,
                "rel": event.rel,
                "buttons": event.buttons
            }
        }
    
    def _process_mouse_wheel(self, event: pygame.event.Event) -> Optional[Dict[str, Any]]:
        """Process mouse wheel event."""
        return {
            "type": "mouse_wheel",
            "data": {
                "x": event.x,
                "y": event.y,
                "flipped": event.flipped
            }
        }
    
    def _notify_handlers(self, event_data: Dict[str, Any]) -> None:
        """
        Notify all registered handlers for an event type.
        
        Args:
            event_data: Event data to pass to handlers
        """
        event_type = event_data["type"]
        if event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                try:
                    handler(event_data)
                except Exception as e:
                    print(f"Error in event handler for {event_type}: {e}")
    
    def get_square_from_mouse_pos(self, mouse_pos: Tuple[int, int], board_rect: pygame.Rect, square_size: int) -> Optional[int]:
        """
        Convert mouse position to board square index.
        
        Args:
            mouse_pos: Mouse position (x, y)
            board_rect: Board rectangle
            square_size: Size of each square
            
        Returns:
            Square index or None if outside board
        """
        x, y = mouse_pos
        
        # Check if mouse is within board bounds
        if not board_rect.collidepoint(x, y):
            return None
        
        # Calculate relative position within board
        rel_x = x - board_rect.x
        rel_y = y - board_rect.y
        
        # Calculate file and rank
        file = int(rel_x // square_size)
        rank = 7 - int(rel_y // square_size)  # Invert rank for chess notation
        
        # Validate bounds
        if 0 <= file <= 7 and 0 <= rank <= 7:
            return rank * 8 + file
        
        return None
    
    def get_mouse_pos_from_square(self, square_index: int, board_rect: pygame.Rect, square_size: int) -> Tuple[int, int]:
        """
        Convert board square index to mouse position.
        
        Args:
            square_index: Board square index
            board_rect: Board rectangle
            square_size: Size of each square
            
        Returns:
            Mouse position (x, y) for center of square
        """
        rank = square_index // 8
        file = square_index % 8
        
        # Convert to screen coordinates
        x = board_rect.x + (file + 0.5) * square_size
        y = board_rect.y + ((7 - rank) + 0.5) * square_size
        
        return (int(x), int(y))
    
    def add_key_binding(self, key: int, action: str) -> None:
        """
        Add a custom key binding.
        
        Args:
            key: Pygame key constant
            action: Action name
        """
        self._key_bindings[key] = action
    
    def remove_key_binding(self, key: int) -> bool:
        """
        Remove a key binding.
        
        Args:
            key: Pygame key constant
            
        Returns:
            True if binding was removed, False if not found
        """
        if key in self._key_bindings:
            del self._key_bindings[key]
            return True
        return False
    
    def get_key_bindings(self) -> Dict[int, str]:
        """Get all key bindings."""
        return self._key_bindings.copy()
    
    def clear_event_handlers(self) -> None:
        """Clear all event handlers."""
        self._event_handlers.clear() 