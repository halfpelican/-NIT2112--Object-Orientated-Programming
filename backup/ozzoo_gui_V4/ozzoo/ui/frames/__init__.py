"""
OzZoo UI Frames Package
Contains all frame components for the application.
"""

from .animal_view import AnimalViewFrame
from .enclosure_view import EnclosureViewFrame
from .main_menu import MainMenuFrame
from .settings import SettingsFrame
from .shop import ShopFrame
from .zoo_status import ZooStatusFrame

__all__ = [
    "AnimalViewFrame",
    "EnclosureViewFrame",
    "MainMenuFrame",
    "SettingsFrame",
    "ShopFrame",
    "ZooStatusFrame",
]
