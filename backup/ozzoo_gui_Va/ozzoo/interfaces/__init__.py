"""
OzZoo Interfaces Package.

This package exports all abstract base classes that define
the core interfaces used throughout the OzZoo application.
"""

from .base import ICleanable, IFeedable, IObservable, IObserver

__all__ = [
    "ICleanable",
    "IFeedable",
    "IObservable",
    "IObserver",
]
