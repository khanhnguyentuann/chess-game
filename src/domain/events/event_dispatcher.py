"""
Enhanced Event Dispatcher with async support and event filtering.
Supports both sync and async event handlers.
"""

from typing import Dict, List, Callable, Any, Optional, Union
import asyncio
from abc import ABC, abstractmethod
from enum import Enum
import logging
from dataclasses import dataclass
from datetime import datetime

from .game_events import GameEvent, EventType


class EventPriority(Enum):
    """Event handler priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class EventHandler:
    """Wrapper for event handlers with metadata."""
    handler: Union[Callable, Callable[..., Any]]
    priority: EventPriority = EventPriority.NORMAL
    is_async: bool = False
    event_filter: Optional[Callable[[GameEvent], bool]] = None
    name: Optional[str] = None


class IEventMiddleware(ABC):
    """Interface for event middleware."""
    
    @abstractmethod
    async def process_event(self, event: GameEvent, next_handler: Callable) -> Any:
        """Process event with middleware logic."""
        pass


class EventDispatcher:
    """
    Advanced event dispatcher with middleware support, 
    async handling, and event filtering.
    """
    
    def __init__(self):
        self._handlers: Dict[EventType, List[EventHandler]] = {}
        self._middleware: List[IEventMiddleware] = []
        self._logger = logging.getLogger(__name__)
        self._event_history: List[GameEvent] = []
        self._max_history = 1000
    
    def subscribe(self, 
                 event_type: EventType, 
                 handler: Union[Callable, Callable[..., Any]],
                 priority: EventPriority = EventPriority.NORMAL,
                 event_filter: Optional[Callable[[GameEvent], bool]] = None,
                 name: Optional[str] = None) -> str:
        """
        Subscribe to events with advanced options.
        
        Args:
            event_type: Type of event to subscribe to
            handler: Event handler function (sync or async)
            priority: Handler priority level
            event_filter: Optional filter function
            name: Optional handler name for debugging
            
        Returns:
            Handler ID for unsubscription
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        
        # Detect if handler is async
        is_async = asyncio.iscoroutinefunction(handler)
        
        event_handler = EventHandler(
            handler=handler,
            priority=priority,
            is_async=is_async,
            event_filter=event_filter,
            name=name or f"{handler.__name__}_{len(self._handlers[event_type])}"
        )
        
        self._handlers[event_type].append(event_handler)
        
        # Sort by priority (highest first)
        self._handlers[event_type].sort(
            key=lambda h: h.priority.value, 
            reverse=True
        )
        
        handler_id = f"{event_type.value}_{event_handler.name}"
        self._logger.debug(f"Subscribed handler {handler_id} to {event_type.value}")
        
        return handler_id
    
    def unsubscribe(self, event_type: EventType, handler_id: str) -> bool:
        """Unsubscribe a handler by ID."""
        if event_type not in self._handlers:
            return False
        
        for i, handler in enumerate(self._handlers[event_type]):
            if f"{event_type.value}_{handler.name}" == handler_id:
                del self._handlers[event_type][i]
                self._logger.debug(f"Unsubscribed handler {handler_id}")
                return True
        
        return False
    
    def unsubscribe_all(self, event_type: EventType) -> None:
        """Remove all handlers for an event type."""
        if event_type in self._handlers:
            count = len(self._handlers[event_type])
            self._handlers[event_type].clear()
            self._logger.debug(f"Unsubscribed {count} handlers from {event_type.value}")
    
    def add_middleware(self, middleware: IEventMiddleware) -> None:
        """Add event middleware."""
        self._middleware.append(middleware)
        self._logger.debug(f"Added middleware: {middleware.__class__.__name__}")
    
    async def dispatch(self, event: GameEvent) -> Dict[str, Any]:
        """
        Dispatch event to all registered handlers with middleware support.
        
        Args:
            event: Event to dispatch
            
        Returns:
            Dictionary with dispatch results
        """
        try:
            # Add to history
            self._add_to_history(event)
            
            # Apply middleware
            processed_event = event
            for middleware in self._middleware:
                processed_event = await middleware.process_event(
                    processed_event, 
                    lambda e: e  # Identity function as next handler
                )
            
            # Get handlers for this event type
            handlers = self._handlers.get(event.event_type, [])
            
            results = {
                'event_id': event.event_id,
                'handlers_called': 0,
                'handlers_failed': 0,
                'errors': []
            }
            
            for handler in handlers:
                # Apply event filter if present
                if handler.event_filter and not handler.event_filter(processed_event):
                    continue
                
                try:
                    if handler.is_async:
                        await handler.handler(processed_event)
                    else:
                        handler.handler(processed_event)
                    
                    results['handlers_called'] += 1
                    
                except Exception as e:
                    results['handlers_failed'] += 1
                    results['errors'].append({
                        'handler': handler.name,
                        'error': str(e)
                    })
                    self._logger.error(
                        f"Handler {handler.name} failed: {e}", 
                        exc_info=True
                    )
            
            self._logger.debug(
                f"Dispatched {event.event_type.value}: "
                f"{results['handlers_called']} called, "
                f"{results['handlers_failed']} failed"
            )
            
            return results
            
        except Exception as e:
            self._logger.error(f"Event dispatch failed: {e}", exc_info=True)
            return {
                'event_id': event.event_id,
                'handlers_called': 0,
                'handlers_failed': 1,
                'errors': [{'handler': 'dispatcher', 'error': str(e)}]
            }
    
    def dispatch_sync(self, event: GameEvent) -> Dict[str, Any]:
        """Synchronous event dispatch wrapper."""
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.dispatch(event))
        except RuntimeError:
            # No event loop running, create new one
            return asyncio.run(self.dispatch(event))
    
    def get_event_history(self, 
                         event_type: Optional[EventType] = None,
                         limit: Optional[int] = None) -> List[GameEvent]:
        """Get event history with optional filtering."""
        history = self._event_history
        
        if event_type:
            history = [e for e in history if e.event_type == event_type]
        
        if limit:
            history = history[-limit:]
        
        return history
    
    def clear_history(self) -> None:
        """Clear event history."""
        self._event_history.clear()
    
    def get_handler_info(self) -> Dict[str, Any]:
        """Get information about registered handlers."""
        info = {}
        for event_type, handlers in self._handlers.items():
            info[event_type.value] = [
                {
                    'name': h.name,
                    'priority': h.priority.name,
                    'is_async': h.is_async,
                    'has_filter': h.event_filter is not None
                }
                for h in handlers
            ]
        return info
    
    def _add_to_history(self, event: GameEvent) -> None:
        """Add event to history with size limit."""
        self._event_history.append(event)
        
        # Maintain history size limit
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]


# Built-in middleware implementations
class LoggingMiddleware(IEventMiddleware):
    """Middleware for logging events."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
    
    async def process_event(self, event: GameEvent, next_handler: Callable) -> Any:
        self.logger.info(f"Event: {event.event_type.value} - {event.data}")
        return await next_handler(event)


class TimingMiddleware(IEventMiddleware):
    """Middleware for measuring event processing time."""
    
    def __init__(self):
        self.timing_data = {}
    
    async def process_event(self, event: GameEvent, next_handler: Callable) -> Any:
        start_time = datetime.now()
        result = await next_handler(event)
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        event_type = event.event_type.value
        
        if event_type not in self.timing_data:
            self.timing_data[event_type] = []
        
        self.timing_data[event_type].append(duration)
        return result
    
    def get_average_time(self, event_type: str) -> Optional[float]:
        """Get average processing time for event type."""
        if event_type in self.timing_data:
            times = self.timing_data[event_type]
            return sum(times) / len(times)
        return None


class EventFilterMiddleware(IEventMiddleware):
    """Middleware for global event filtering."""
    
    def __init__(self, filter_func: Callable[[GameEvent], bool]):
        self.filter_func = filter_func
    
    async def process_event(self, event: GameEvent, next_handler: Callable) -> Any:
        if self.filter_func(event):
            return await next_handler(event)
        return event  # Pass through without processing


# Global event dispatcher instance
_global_dispatcher = EventDispatcher()

def get_event_dispatcher() -> EventDispatcher:
    """Get the global event dispatcher instance."""
    return _global_dispatcher
