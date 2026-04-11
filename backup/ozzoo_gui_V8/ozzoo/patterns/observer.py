"""
OzZoo Observer Pattern Module
Implements the Observer design pattern for event handling.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable, Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

if TYPE_CHECKING:
    from ..models.animal import Animal


@dataclass
class ZooEvent:
    """Represents an event that occurred in the zoo."""
    event_type: str  # "death", "birth", "sick", "escape", "visitor", etc.
    timestamp: datetime
    subject: Any  # The object that triggered the event (Animal, Enclosure, etc.)
    message: str
    data: Dict[str, Any]  # Additional event data


class IObserver(ABC):
    """Abstract base class for observers."""
    
    @abstractmethod
    def update(self, event: ZooEvent) -> None:
        """Called when an observed event occurs."""
        pass


class EventManager:
    """
    Central event manager using Observer pattern.
    
    Manages subscriptions and broadcasts events to interested observers.
    Supports filtering by event type.
    """
    
    def __init__(self):
        """
        Initialise observer registries and bounded event history storage.
        """
        self._observers: Dict[str, List[IObserver]] = {}  # event_type -> observers
        self._event_history: List[ZooEvent] = []
        self._max_history = 100  # Keep last 100 events
    
    def subscribe(self, event_type: str, observer: IObserver) -> None:
        """
        Subscribe an observer to a specific event type.
        Use "*" to subscribe to all events.
        """
        if event_type not in self._observers:
            self._observers[event_type] = []
        if observer not in self._observers[event_type]:
            self._observers[event_type].append(observer)
    
    def unsubscribe(self, event_type: str, observer: IObserver) -> None:
        """Unsubscribe an observer from an event type."""
        if event_type in self._observers and observer in self._observers[event_type]:
            self._observers[event_type].remove(observer)
    
    def notify(self, event: ZooEvent) -> None:
        """
        Notify all relevant observers of an event.
        Notifies both specific event_type subscribers and "*" subscribers.
        """
        # Add to history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        
        # Notify specific subscribers
        if event.event_type in self._observers:
            for observer in self._observers[event.event_type]:
                observer.update(event)
        
        # Notify wildcard subscribers
        if "*" in self._observers:
            for observer in self._observers["*"]:
                observer.update(event)
    
    def emit(self, event_type: str, subject: Any, message: str, **data) -> None:
        """
        Convenience method to create and emit an event.
        
        Args:
            event_type: Type of event
            subject: The object that triggered the event
            message: Human-readable message
            **data: Additional event data
        """
        event = ZooEvent(
            event_type=event_type,
            timestamp=datetime.now(),
            subject=subject,
            message=message,
            data=data
        )
        self.notify(event)
    
    def get_history(self, event_type: str | None = None, limit: int = 10) -> List[ZooEvent]:
        """
        Get recent events, optionally filtered by type.
        
        Args:
            event_type: Filter by event type (None for all)
            limit: Maximum number of events to return
        """
        if event_type:
            filtered = [e for e in self._event_history if e.event_type == event_type]
        else:
            filtered = self._event_history
        return filtered[-limit:]
    
    def clear_history(self) -> None:
        """Clear all event history."""
        self._event_history.clear()


class LoggingObserver(IObserver):
    """Simple observer that logs events to console (for debugging)."""
    
    def __init__(self, prefix: str = "[ZOO EVENT]"):
        """
        Initialise a console logger observer.

        Args:
            prefix: Prefix text printed before each event line.
        """
        self._prefix = prefix
    
    def update(self, event: ZooEvent) -> None:
        """
        Print an event to stdout.

        Args:
            event: Event payload received from the event manager.
        """
        print(f"{self._prefix} {event.timestamp.strftime('%H:%M:%S')} - {event.event_type.upper()}: {event.message}")


class CallbackObserver(IObserver):
    """Observer that calls a callback function when events occur."""
    
    def __init__(self, callback: Callable[[ZooEvent], None]):
        """
        Initialise a callback-based observer.

        Args:
            callback: Function invoked whenever an event is emitted.
        """
        self._callback = callback
    
    def update(self, event: ZooEvent) -> None:
        """
        Forward the event to the configured callback.

        Args:
            event: Event payload received from the event manager.
        """
        self._callback(event)


# Event type constants
class EventTypes:
    """Constants for common event types."""
    ANIMAL_DEATH = "death"
    ANIMAL_BIRTH = "birth"
    ANIMAL_SICK = "sick"
    ANIMAL_RECOVERED = "recovered"
    ANIMAL_ESCAPE = "escape"
    ANIMAL_FED = "fed"
    ENCLOSURE_CLEANED = "cleaned"
    ENCLOSURE_DIRTY = "dirty"
    VISITOR_ARRIVED = "visitor_arrived"
    VISITOR_LEFT = "visitor_left"
    VISITOR_DONATED = "donated"
    DAY_START = "day_start"
    DAY_END = "day_end"
    RANDOM_EVENT = "random_event"
    PURCHASE = "purchase"
    INSUFFICIENT_FUNDS = "insufficient_funds"
