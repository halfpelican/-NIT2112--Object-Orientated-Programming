"""
OzZoo Animals Package.

Exports all concrete animal implementations.
"""

from .birds import Emu, WedgeTailedEagle
from .mammals import (
    Echidna,
    Kangaroo,
    Koala,
    Platypus,
    TasmanianDevil,
    Wombat,
)
from .reptiles import FrilledLizard, SaltwaterCroc

__all__ = [
    # Birds
    "Emu",
    "WedgeTailedEagle",
    # Mammals
    "Echidna",
    "Kangaroo",
    "Koala",
    "Platypus",
    "TasmanianDevil",
    "Wombat",
    # Reptiles
    "FrilledLizard",
    "SaltwaterCroc",
]
