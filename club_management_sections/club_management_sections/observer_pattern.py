"""Observer and observable abstractions for event-driven notifications."""

from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
# =============================================================================
# OBSERVER PATTERN
# =============================================================================


class Observer(ABC):
    """Observer interface for the Observer pattern."""
    
    @abstractmethod
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """Receive notification of an event."""
        pass


class Observable(ABC):
    """Interface for observable objects."""
    
    @abstractmethod
    def add_observer(self, observer: Observer) -> None:
        """Add an observer."""
        pass
    
    @abstractmethod
    def remove_observer(self, observer: Observer) -> None:
        """Remove an observer."""
        pass
    
    @abstractmethod
    def notify_observers(self, event_type: str, data: Dict[str, Any]) -> None:
        """Notify all observers of an event."""
        pass

