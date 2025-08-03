"""
Event Publisher Service
Infrastructure service for publishing domain events.
"""

import asyncio
from typing import Any, Callable, Dict, List, Optional

from ...domain.events import DomainEvent


class EventPublisher:
    """Service for publishing domain events to registered handlers."""
    
    def __init__(self):
        """Initialize event publisher."""
        self._handlers: Dict[str, List[Callable]] = {}
        self._event_history: List[DomainEvent] = []
        self._is_enabled = True
    
    def subscribe(self, event_type: str, handler: Callable) -> None:
        """
        Subscribe to an event type.
        
        Args:
            event_type: Type of event to subscribe to
            handler: Function to call when event occurs
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def unsubscribe(self, event_type: str, handler: Callable) -> bool:
        """
        Unsubscribe from an event type.
        
        Args:
            event_type: Type of event to unsubscribe from
            handler: Function to remove from handlers
            
        Returns:
            True if handler was removed, False if not found
        """
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
                return True
            except ValueError:
                pass
        return False
    
    async def publish(self, event: DomainEvent) -> None:
        """
        Publish a domain event to all registered handlers.
        
        Args:
            event: Domain event to publish
        """
        if not self._is_enabled:
            return
        
        # Store event in history
        self._event_history.append(event)
        
        # Get handlers for this event type
        event_type = event.event_type()
        handlers = self._handlers.get(event_type, [])
        
        # Call all handlers asynchronously
        tasks = []
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    task = asyncio.create_task(handler(event))
                    tasks.append(task)
                else:
                    # For synchronous handlers, run in thread pool
                    loop = asyncio.get_event_loop()
                    task = loop.run_in_executor(None, handler, event)
                    tasks.append(task)
            except Exception as e:
                print(f"Error in event handler for {event_type}: {e}")
        
        # Wait for all handlers to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def publish_sync(self, event: DomainEvent) -> None:
        """
        Publish a domain event synchronously.
        
        Args:
            event: Domain event to publish
        """
        if not self._is_enabled:
            return
        
        # Store event in history
        self._event_history.append(event)
        
        # Get handlers for this event type
        event_type = event.event_type()
        handlers = self._handlers.get(event_type, [])
        
        # Call all handlers synchronously
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"Error in event handler for {event_type}: {e}")
    
    def get_event_history(self) -> List[DomainEvent]:
        """Get all published events."""
        return self._event_history.copy()
    
    def get_events_by_type(self, event_type: str) -> List[DomainEvent]:
        """Get events of a specific type."""
        return [event for event in self._event_history if event.event_type() == event_type]
    
    def clear_history(self) -> None:
        """Clear event history."""
        self._event_history.clear()
    
    def enable(self) -> None:
        """Enable event publishing."""
        self._is_enabled = True
    
    def disable(self) -> None:
        """Disable event publishing."""
        self._is_enabled = False
    
    def is_enabled(self) -> bool:
        """Check if event publishing is enabled."""
        return self._is_enabled
    
    def get_subscriber_count(self, event_type: str) -> int:
        """Get number of subscribers for an event type."""
        return len(self._handlers.get(event_type, []))
    
    def get_all_event_types(self) -> List[str]:
        """Get all registered event types."""
        return list(self._handlers.keys()) 