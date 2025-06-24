"""
Event Bus for Decoupled System Communication

Implements publish-subscribe pattern for system communication.
Enables systems to communicate without direct dependencies.
"""

from typing import Dict, List, Callable, Type, Any
from collections import defaultdict
import time
import uuid

class Event:
    """
    Base class for all events in the system.
    
    Events are immutable data objects that represent something that happened.
    """
    
    def __init__(self):
        self.event_id = str(uuid.uuid4())
        self.timestamp = time.time()
        self.handled = False
    
    def mark_handled(self):
        """Mark event as handled (for debugging/logging)"""
        self.handled = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize event to dictionary"""
        return {
            'event_type': self.__class__.__name__,
            'event_id': self.event_id,
            'timestamp': self.timestamp,
            'handled': self.handled
        }

class EventBus:
    """
    Central event bus for publish-subscribe communication.
    
    Allows systems to communicate without knowing about each other.
    Events are processed synchronously to maintain deterministic order.
    """
    
    _instance = None
    
    def __init__(self):
        self._subscribers: Dict[Type[Event], List[Callable]] = defaultdict(list)
        self._event_queue: List[Event] = []
        self._processing = False
        self._stats = EventBusStats()
    
    @classmethod
    def get_instance(cls) -> 'EventBus':
        """Get singleton instance of event bus"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def subscribe(self, event_type: Type[Event], handler: Callable[[Event], None]):
        """
        Subscribe to events of specified type.
        
        Args:
            event_type: Type of event to listen for
            handler: Function to call when event occurs
        """
        self._subscribers[event_type].append(handler)
        self._stats.subscriber_count += 1
    
    def unsubscribe(self, event_type: Type[Event], handler: Callable[[Event], None]):
        """
        Unsubscribe from events of specified type.
        
        Args:
            event_type: Type of event to stop listening for
            handler: Handler function to remove
        """
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(handler)
                self._stats.subscriber_count -= 1
            except ValueError:
                pass  # Handler wasn't subscribed
    
    def publish(self, event: Event):
        """
        Publish event to all subscribers.
        
        Args:
            event: Event to publish
        """
        if self._processing:
            # Queue event if we're already processing events
            self._event_queue.append(event)
        else:
            self._process_event(event)
    
    def publish_immediate(self, event: Event):
        """
        Publish event immediately, bypassing queue.
        
        Use with caution - can cause recursive event processing.
        
        Args:
            event: Event to publish immediately
        """
        self._process_event(event)
    
    def process_events(self):
        """
        Process all queued events.
        
        Call this once per frame to process events in order.
        """
        if self._processing:
            return  # Prevent recursive processing
        
        self._processing = True
        
        try:
            while self._event_queue:
                event = self._event_queue.pop(0)
                self._process_event(event)
        finally:
            self._processing = False
    
    def _process_event(self, event: Event):
        """
        Process single event by notifying all subscribers.
        
        Args:
            event: Event to process
        """
        event_type = type(event)
        
        # Get handlers for this event type
        handlers = self._subscribers.get(event_type, [])
        
        self._stats.events_published += 1
        self._stats.handlers_called += len(handlers)
        
        # Call all handlers
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                # Log error but continue with other handlers
                print(f"Error in event handler: {e}")
                self._stats.handler_errors += 1
    
    def clear_subscribers(self):
        """Clear all subscribers (useful for testing)"""
        self._subscribers.clear()
        self._stats.subscriber_count = 0
    
    def get_subscriber_count(self, event_type: Type[Event] = None) -> int:
        """
        Get number of subscribers for event type.
        
        Args:
            event_type: Event type to count, or None for total
            
        Returns:
            Number of subscribers
        """
        if event_type is None:
            return sum(len(handlers) for handlers in self._subscribers.values())
        else:
            return len(self._subscribers.get(event_type, []))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics"""
        return self._stats.to_dict()
    
    def reset_stats(self):
        """Reset statistics counters"""
        self._stats = EventBusStats()

class EventBusStats:
    """Statistics tracking for event bus performance"""
    
    def __init__(self):
        self.events_published = 0
        self.handlers_called = 0
        self.handler_errors = 0
        self.subscriber_count = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting"""
        return {
            'events_published': self.events_published,
            'handlers_called': self.handlers_called,
            'handler_errors': self.handler_errors,
            'subscriber_count': self.subscriber_count
        }

# Create singleton instance for easy access
_event_bus_singleton = None

def get_event_bus():
    """Get singleton EventBus instance"""
    global _event_bus_singleton
    if _event_bus_singleton is None:
        _event_bus_singleton = EventBus()
    return _event_bus_singleton