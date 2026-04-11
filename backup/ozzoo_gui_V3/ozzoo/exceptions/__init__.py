"""
OzZoo Exceptions Package.

This package provides a structured exception hierarchy for the OzZoo
application, enabling precise error handling across the system.
"""

from ozzoo.exceptions.zoo_exceptions import (
    ZooError,
    AnimalError,
    IncompatibleSpeciesError,
    AnimalSickError,
    ResourceError,
    InsufficientFoodError,
    InsufficientFundsError,
    EnclosureError,
    HabitatCapacityExceededError,
    InvalidHabitatError,
)

__all__ = [
    # Base exception
    "ZooError",
    # Animal exceptions
    "AnimalError",
    "IncompatibleSpeciesError",
    "AnimalSickError",
    # Resource exceptions
    "ResourceError",
    "InsufficientFoodError",
    "InsufficientFundsError",
    # Enclosure exceptions
    "EnclosureError",
    "HabitatCapacityExceededError",
    "InvalidHabitatError",
]
