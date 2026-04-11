"""
OzZoo Main Menu Frame
Welcome screen with New Game, Load Game, and Quit options.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk, filedialog
from typing import TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
    from ..app import OzZooApp


class MainMenuFrame(tk.Frame):
    """
    Main menu frame - the first screen shown to users.
    
    Features:
    - Large OzZoo logo/title with Australian wildlife theming
    - New Game button (starts fresh with default zoo)
    - Load Game button (opens file dialog to load saved game)
    - Quit button
    - Decorative Australian animals/imagery (emoji-based)
    """
    
    def __init__(self, parent: tk.Frame, app: OzZooApp):
        """
        Initialise the main menu frame.

        Args:
            parent: Parent container widget.
            app: Shared application controller.
        """
        super().__init__(parent, bg=app.COLOURS["background"])
        self._app = app
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the main menu UI."""
        # Centre container
        centre_frame = tk.Frame(self, bg=self._app.COLOURS["background"])
        centre_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Title with emoji decorations
        title_frame = tk.Frame(centre_frame, bg=self._app.COLOURS["background"])
        title_frame.pack(pady=20)
        
        # Animal decorations
        animals_top = tk.Label(
            title_frame,
            text="🦘  🐨  🦎  🦅  🐊",
            bg=self._app.COLOURS["background"],
            font=("Segoe UI Emoji", 32)
        )
        animals_top.pack()
        
        # Main title
        title = tk.Label(
            title_frame,
            text="OzZoo",
            bg=self._app.COLOURS["background"],
            fg=self._app.COLOURS["primary"],
            font=("Segoe UI", 72, "bold")
        )
        title.pack()
        
        # Subtitle
        subtitle = tk.Label(
            title_frame,
            text="Australian Wildlife Park Simulation",
            bg=self._app.COLOURS["background"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 18)
        )
        subtitle.pack(pady=(0, 10))
        
        # Tagline
        tagline = tk.Label(
            title_frame,
            text="G'day, Manager! Build your dream wildlife sanctuary.",
            bg=self._app.COLOURS["background"],
            fg=self._app.COLOURS["secondary"],
            font=("Segoe UI", 12, "italic")
        )
        tagline.pack(pady=(0, 30))
        
        # Buttons frame
        buttons_frame = tk.Frame(centre_frame, bg=self._app.COLOURS["background"])
        buttons_frame.pack(pady=20)
        
        # New Game button
        new_game_btn = tk.Button(
            buttons_frame,
            text="🌿  New Game",
            command=self._on_new_game,
            bg=self._app.COLOURS["primary"],
            fg=self._app.COLOURS["text_light"],
            font=("Segoe UI", 16, "bold"),
            width=20,
            height=2,
            relief=tk.FLAT,
            activebackground="#1B5E20"
        )
        new_game_btn.pack(pady=10)
        
        # Load Game button
        load_game_btn = tk.Button(
            buttons_frame,
            text="📂  Load Game",
            command=self._on_load_game,
            bg=self._app.COLOURS["secondary"],
            fg=self._app.COLOURS["text_light"],
            font=("Segoe UI", 14),
            width=20,
            height=2,
            relief=tk.FLAT,
            activebackground="#5D4037"
        )
        load_game_btn.pack(pady=10)
        
        # Quit button
        quit_btn = tk.Button(
            buttons_frame,
            text="🚪  Quit",
            command=self._on_quit,
            bg=self._app.COLOURS["danger"],
            fg=self._app.COLOURS["text_light"],
            font=("Segoe UI", 12),
            width=20,
            height=2,
            relief=tk.FLAT,
            activebackground="#B71C1C"
        )
        quit_btn.pack(pady=10)
        
        # Footer with credits
        footer = tk.Label(
            centre_frame,
            text="NIT2112 Object-Oriented Programming Project",
            bg=self._app.COLOURS["background"],
            fg=self._app.COLOURS["border"],
            font=("Segoe UI", 10)
        )
        footer.pack(pady=(40, 0))
    
    def _on_new_game(self) -> None:
        """Start a new game with default zoo setup."""
        from ...models.zoo import create_default_zoo
        
        try:
            zoo = create_default_zoo()
            self._app.zoo = zoo
            self._app.set_status("New game started! Welcome to OzZoo!")
            
            # Set up navigation buttons
            self._setup_game_navigation()
            
            # Show the zoo status dashboard
            self._app.show_frame("zoo_status")
            
        except Exception as e:
            self._app.show_error("Error", f"Failed to create new game: {e}")
    
    def _on_load_game(self) -> None:
        """Load a saved game from file."""
        from ...models.zoo import load_game
        
        # Get saves directory
        saves_dir = Path(__file__).parent.parent.parent / "saves"
        saves_dir.mkdir(exist_ok=True)
        
        filepath = filedialog.askopenfilename(
            title="Load Game",
            initialdir=saves_dir,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filepath:
            try:
                zoo = load_game(Path(filepath))
                self._app.zoo = zoo
                self._app.set_status(f"Loaded game: Day {zoo.day}")
                
                # Set up navigation buttons
                self._setup_game_navigation()
                
                # Show the zoo status dashboard
                self._app.show_frame("zoo_status")
                
            except Exception as e:
                self._app.show_error("Load Error", f"Failed to load game: {e}")
    
    def _on_quit(self) -> None:
        """Quit the application."""
        if self._app.ask_yes_no("Quit", "Are you sure you want to quit OzZoo?"):
            self._app.destroy()
    
    def _setup_game_navigation(self) -> None:
        """Set up navigation buttons for in-game screens."""
        # Clear existing nav buttons
        for widget in self._app._nav_frame.winfo_children():
            widget.destroy()
        
        # Add game navigation buttons
        self._app.add_nav_button("Dashboard", "zoo_status", "📊")
        self._app.add_nav_button("Animals", "animal_view", "🦘")
        self._app.add_nav_button("Enclosures", "enclosure_view", "🏕️")
        self._app.add_nav_button("Map", "map_view", "🗺️")
        self._app.add_nav_button("Shop", "shop", "🛒")
        self._app.add_nav_button("Settings", "settings", "⚙️")
