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
    RingtailPossum,
    TasmanianDevil,
    Wombat,
)
from .reptiles import (
    BlueTonguedSkink,
    CarpetPython,
    EasternBrownSnake,
    FrilledLizard,
    Goanna,
    SaltwaterCroc,
)

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
    "RingtailPossum",
    "TasmanianDevil",
    "Wombat",
    # Reptiles
    "BlueTonguedSkink",
    "CarpetPython",
    "EasternBrownSnake",
    "FrilledLizard",
    "Goanna",
    "SaltwaterCroc",
]
