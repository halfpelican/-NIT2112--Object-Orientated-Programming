"""
OzZoo Animals Package.

Exports all concrete animal implementations.
"""

from .birds import Kookaburra, Emu, WedgeTailedEagle
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
    "Kookaburra",
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
