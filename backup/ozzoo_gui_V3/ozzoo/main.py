#!/usr/bin/env python3
"""
OzZoo - Australian Wildlife Park Simulation
Main entry point for the GUI application.

NIT2112 Object-Oriented Programming Project
Name: Benjamin Morovan
Student ID: s8014554
"""

from __future__ import annotations
import sys
from pathlib import Path

# Ensure the ozzoo package is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from ozzoo.ui.app import OzZooApp
from ozzoo.ui.frames.main_menu import MainMenuFrame
from ozzoo.ui.frames.zoo_status import ZooStatusFrame
from ozzoo.ui.frames.animal_view import AnimalViewFrame
from ozzoo.ui.frames.enclosure_view import EnclosureViewFrame
from ozzoo.ui.frames.shop import ShopFrame
from ozzoo.ui.frames.map_view import MapViewFrame
from ozzoo.ui.frames.settings import SettingsFrame


def main() -> None:
    """
    Main entry point for OzZoo.
    
    Creates the application, registers all frames, and starts the main loop.
    """
    # Create the application
    app = OzZooApp()
    
    # Register all frames for navigation
    app.register_frame("main_menu", MainMenuFrame)
    app.register_frame("zoo_status", ZooStatusFrame)
    app.register_frame("animal_view", AnimalViewFrame)
    app.register_frame("enclosure_view", EnclosureViewFrame)
    app.register_frame("map_view", MapViewFrame)
    app.register_frame("shop", ShopFrame)
    app.register_frame("settings", SettingsFrame)
    
    # Show the main menu on startup
    app.show_frame("main_menu")
    
    # Start the application
    app.mainloop()


if __name__ == "__main__":
    main()
