"""
Abstract Base Classes defining interfaces for the OzZoo project.

This module provides the core interfaces that define contracts for
cleanable objects, feedable entities, and the Observer pattern.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.resources import Food


class ICleanable(ABC):
    """Interface for objects that can be cleaned."""

    @abstractmethod
    def clean(self) -> None:
        """Clean the object, improving its cleanliness level."""
        pass

    @abstractmethod
    def get_cleanliness(self) -> int:
        """Return current cleanliness level (0-100)."""
        pass


class IFeedable(ABC):
    """Interface for entities that can be fed."""

    @abstractmethod
    def feed(self, food: Food) -> bool:
        """
        Feed the entity with the specified food.

        Args:
            food: The food item to feed to the entity.

        Returns:
            True if feeding was successful, False otherwise.
        """
        pass

    @abstractmethod
    def get_diet(self) -> str:
        """Return the required diet type (e.g., 'herbivore', 'carnivore')."""
        pass

    @abstractmethod
    def is_hungry(self) -> bool:
        """Check if the entity is hungry and needs feeding."""
        pass


class IObservable(ABC):
    """Interface for observable subjects in the Observer pattern."""

    @abstractmethod
    def attach(self, observer: IObserver) -> None:
        """
        Attach an observer to receive notifications.

        Args:
            observer: The observer to attach.
        """
        pass

    @abstractmethod
    def detach(self, observer: IObserver) -> None:
        """
        Detach an observer from receiving notifications.

        Args:
            observer: The observer to detach.
        """
        pass

    @abstractmethod
    def notify(self, event: str) -> None:
        """
        Notify all attached observers of an event.

        Args:
            event: A string describing the event that occurred.
        """
        pass


class IObserver(ABC):
    """Interface for observers in the Observer pattern."""

    @abstractmethod
    def update(self, subject: IObservable, event: str) -> None:
        """
        Called when the observed subject changes state.

        Args:
            subject: The observable that triggered the notification.
            event: A string describing the event that occurred.
        """
        pass
