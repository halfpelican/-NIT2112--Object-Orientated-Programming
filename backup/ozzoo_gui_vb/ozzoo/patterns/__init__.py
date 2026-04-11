"""
OzZoo Design Patterns Package
Contains implementations of design patterns used in the application.
"""

from .observer import (
    EventManager,
    IObserver,
    ZooEvent,
    EventTypes,
    LoggingObserver,
    CallbackObserver,
)
from .factory import AnimalFactory, create_animal

__all__ = [
    # Observer pattern
    "EventManager",
    "IObserver",
    "ZooEvent",
    "EventTypes",
    "LoggingObserver",
    "CallbackObserver",
    # Factory pattern
    "AnimalFactory",
    "create_animal",
]
