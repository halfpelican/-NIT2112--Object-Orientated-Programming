"""
OzZoo Custom Widgets - Status Bar
Reusable progress bar widget for health/hunger/happiness display.
"""

from __future__ import annotations
import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..app import OzZooApp


class StatusBar(tk.Frame):
    """
    A custom progress bar widget with label and colour coding.
    
    Usage:
        bar = StatusBar(parent, "Health", 75, "#4CAF50")
        bar.set_value(50)  # Update the value
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        label: str,
        value: int = 0,
        colour: str = "#4CAF50",
        width: int = 200,
        height: int = 20,
        bg_colour: str = "#E0E0E0",
        show_percentage: bool = True
    ):
        """
        Initialise a labelled progress bar widget.

        Args:
            parent: Parent widget container.
            label: Prefix text shown next to the bar.
            value: Initial value from 0-100.
            colour: Primary fill colour for healthy values.
            width: Pixel width of the bar body.
            height: Pixel height of the bar body.
            bg_colour: Background colour for the bar track.
            show_percentage: Whether to append percentage text to the label.
        """
        super().__init__(parent, bg=parent.cget("bg") if hasattr(parent, "cget") else "#FFFFFF")
        
        self._label = label
        self._value = max(0, min(100, value))
        self._colour = colour
        self._width = width
        self._height = height
        self._bg_colour = bg_colour
        self._show_percentage = show_percentage
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Build the status bar UI."""
        # Label
        self._label_widget = tk.Label(
            self,
            text=self._format_label(),
            bg=self.cget("bg"),
            font=("Segoe UI", 10),
            width=15,
            anchor="w"
        )
        self._label_widget.pack(side="left", padx=(0, 10))
        
        # Bar container
        self._bar_container = tk.Frame(
            self,
            bg=self._bg_colour,
            width=self._width,
            height=self._height,
            relief="sunken",
            bd=1
        )
        self._bar_container.pack(side="left", fill="x", expand=True)
        self._bar_container.pack_propagate(False)
        
        # Fill bar
        self._bar_fill = tk.Frame(
            self._bar_container,
            bg=self._colour,
            height=self._height - 2
        )
        self._bar_fill.place(relwidth=self._value / 100, relheight=1)
    
    def _format_label(self) -> str:
        """Format the label with percentage if enabled."""
        if self._show_percentage:
            return f"{self._label}: {self._value}%"
        return self._label
    
    def set_value(self, value: int) -> None:
        """Update the bar value."""
        self._value = max(0, min(100, value))
        self._bar_fill.place(relwidth=self._value / 100, relheight=1)
        self._label_widget.config(text=self._format_label())
        
        # Update colour based on value thresholds
        if self._value < 25:
            self._bar_fill.config(bg="#D32F2F")  # Red
        elif self._value < 50:
            self._bar_fill.config(bg="#FF8F00")  # Orange
        else:
            self._bar_fill.config(bg=self._colour)
    
    def set_colour(self, colour: str) -> None:
        """Update the bar colour."""
        self._colour = colour
        self._bar_fill.config(bg=colour)
    
    @property
    def value(self) -> int:
        """Return the current bar value (0-100)."""
        return self._value


class AnimalCard(tk.Frame):
    """
    A card widget displaying animal information.
    
    Shows:
    - Name and species
    - Health/hunger/happiness bars
    - Status indicator (emoji)
    - Click callback support
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        name: str,
        species: str,
        health: int,
        hunger: int,
        happiness: int,
        on_click: callable = None,
        bg_colour: str = "#FFFFFF"
    ):
        """
        Initialise a compact animal summary card.

        Args:
            parent: Parent widget container.
            name: Animal display name.
            species: Animal species label.
            health: Health score (0-100).
            hunger: Hunger score (0-100).
            happiness: Happiness score (0-100).
            on_click: Optional callback fired when the card is clicked.
            bg_colour: Background colour for card and child widgets.
        """
        super().__init__(parent, bg=bg_colour, relief="raised", bd=1, cursor="hand2")
        
        self._name = name
        self._species = species
        self._health = health
        self._hunger = hunger
        self._happiness = happiness
        self._on_click = on_click
        self._bg_colour = bg_colour
        
        self._setup_ui()
        
        if on_click:
            self.bind("<Button-1>", lambda e: on_click())
            for child in self.winfo_children():
                child.bind("<Button-1>", lambda e: on_click())
    
    def _setup_ui(self) -> None:
        """Build the card UI."""
        # Status indicator
        if self._health < 20:
            status = "🔴"
        elif self._hunger > 70:
            status = "🟡"
        else:
            status = "🟢"
        
        # Header with name
        header = tk.Frame(self, bg=self._bg_colour)
        header.pack(fill="x", padx=10, pady=(10, 5))
        
        name_label = tk.Label(
            header,
            text=f"{status} {self._name}",
            bg=self._bg_colour,
            font=("Segoe UI", 12, "bold")
        )
        name_label.pack(side="left")
        
        species_label = tk.Label(
            header,
            text=self._species,
            bg=self._bg_colour,
            fg="#757575",
            font=("Segoe UI", 10)
        )
        species_label.pack(side="right")
        
        # Stats
        stats_frame = tk.Frame(self, bg=self._bg_colour)
        stats_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Mini bars
        for label, value, colour in [
            ("❤️", self._health, "#D32F2F"),
            ("🍽️", 100 - self._hunger, "#FF8F00"),  # Invert hunger (lower is better displayed)
            ("😊", self._happiness, "#388E3C")
        ]:
            bar_frame = tk.Frame(stats_frame, bg=self._bg_colour)
            bar_frame.pack(fill="x", pady=1)
            
            tk.Label(
                bar_frame,
                text=label,
                bg=self._bg_colour,
                font=("Segoe UI", 8)
            ).pack(side="left")
            
            bar_bg = tk.Frame(bar_frame, bg="#E0E0E0", height=6)
            bar_bg.pack(side="left", fill="x", expand=True, padx=5)
            
            bar_fill = tk.Frame(bar_bg, bg=colour, height=6)
            bar_fill.place(relwidth=value/100, relheight=1)
    
    def update_stats(self, health: int, hunger: int, happiness: int) -> None:
        """Update the animal stats and redraw."""
        self._health = health
        self._hunger = hunger
        self._happiness = happiness
        
        # Clear and rebuild
        for widget in self.winfo_children():
            widget.destroy()
        self._setup_ui()
