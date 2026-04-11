"""
Mission Display Widget
Shows current mission progress in the UI.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..app import OzZooApp


class MissionWidget(tk.Frame):
    """Widget displaying current mission status."""
    
    def __init__(self, parent: tk.Frame, app: OzZooApp):
        super().__init__(parent, bg=app.COLOURS["card_bg"], relief="raised", bd=2)
        self._app = app
        self._zoo = app.zoo
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the mission display UI."""
        # Title
        title_frame = tk.Frame(self, bg=self._app.COLOURS["primary"])
        title_frame.pack(fill="x")
        
        tk.Label(
            title_frame,
            text="🎯 Current Mission",
            bg=self._app.COLOURS["primary"],
            fg=self._app.COLOURS["text_light"],
            font=("Segoe UI", 12, "bold"),
            pady=5
        ).pack()
        
        # Mission content
        self._content_frame = tk.Frame(self, bg=self._app.COLOURS["card_bg"])
        self._content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self._refresh()
    
    def _refresh(self) -> None:
        """Refresh mission display."""
        # Clear existing widgets
        for widget in self._content_frame.winfo_children():
            widget.destroy()
        
        if not self._zoo or not self._zoo.current_mission:
            tk.Label(
                self._content_frame,
                text="No active mission",
                bg=self._app.COLOURS["card_bg"],
                fg=self._app.COLOURS["secondary"],
                font=("Segoe UI", 10, "italic")
            ).pack(pady=20)
            return
        
        mission = self._zoo.current_mission
        
        # Mission title
        tk.Label(
            self._content_frame,
            text=mission.title,
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", pady=(0, 5))
        
        # Mission description
        tk.Label(
            self._content_frame,
            text=mission.description,
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 9),
            wraplength=250,
            justify="left"
        ).pack(anchor="w", pady=(0, 10))
        
        # Progress bar
        progress_pct = mission.get_progress_percentage()
        
        tk.Label(
            self._content_frame,
            text=f"Progress: {mission.get_status_text()}",
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(0, 3))
        
        # Progress bar visual
        progress_frame = tk.Frame(
            self._content_frame,
            bg=self._app.COLOURS["border"],
            height=20,
            relief="sunken",
            bd=1
        )
        progress_frame.pack(fill="x", pady=(0, 10))
        progress_frame.pack_propagate(False)
        
        fill_frame = tk.Frame(
            progress_frame,
            bg=self._app.COLOURS["success"] if not mission.is_failed else self._app.COLOURS["danger"],
            width=int(progress_pct * 2.5)  # Scale to widget width
        )
        fill_frame.pack(side="left", fill="y")
        
        # Show individual animal progress for KEEP_HAPPY missions
        from ...models.mission import MissionType
        if mission.mission_type == MissionType.KEEP_HAPPY:
            # Get required info
            required_days = getattr(mission, 'required_days', 5)
            required_count = mission.target_value
            
            # Show which animals are currently happy
            happy_animals = [
                a for a in self._zoo.animals.values()
                if a.is_alive and a.species == mission.target_animal and a.happiness >= 70
            ]
            
            animal_progress = tk.Frame(self._content_frame, bg=self._app.COLOURS["card_bg"])
            animal_progress.pack(fill="x", pady=(0, 10))
            
            # Show requirement status
            requirements_met = len(happy_animals) >= required_count
            status_color = self._app.COLOURS["success"] if requirements_met else self._app.COLOURS["danger"]
            status_text = f"✓ {len(happy_animals)}/{required_count} animals happy today" if requirements_met else f"✗ {len(happy_animals)}/{required_count} animals happy (need {required_count})"
            
            tk.Label(
                animal_progress,
                text=status_text,
                bg=self._app.COLOURS["card_bg"],
                fg=status_color,
                font=("Segoe UI", 9, "bold")
            ).pack(anchor="w", pady=(0, 5))
            
            if happy_animals:
                # Convert species name to display name
                species_display_map = {
                    "Koala": "Koalas",
                    "Kangaroo": "Kangaroos",
                    "Wombat": "Wombats",
                    "Platypus": "Platypuses",
                    "Emu": "Emus",
                    "WedgeTailedEagle": "Wedge-Tailed Eagles",
                    "SaltwaterCroc": "Saltwater Crocodiles",
                    "FrilledLizard": "Frilled Lizards"
                }
                species_display = species_display_map.get(mission.target_animal, f"{mission.target_animal}s")
                
                tk.Label(
                    animal_progress,
                    text=f"🐾 Currently happy {species_display}:",
                    bg=self._app.COLOURS["card_bg"],
                    fg=self._app.COLOURS["text"],
                    font=("Segoe UI", 9, "bold")
                ).pack(anchor="w")
                
                for animal in happy_animals[:5]:  # Show max 5
                    days_happy = self._zoo._consecutive_happy_days.get(animal.name, 0)
                    tk.Label(
                        animal_progress,
                        text=f"  • {animal.name}: 😊 {animal.happiness}% happiness ({days_happy} days streak)",
                        bg=self._app.COLOURS["card_bg"],
                        fg=self._app.COLOURS["success"],
                        font=("Segoe UI", 8)
                    ).pack(anchor="w")
                
                if len(happy_animals) > 5:
                    tk.Label(
                        animal_progress,
                        text=f"  ... and {len(happy_animals) - 5} more",
                        bg=self._app.COLOURS["card_bg"],
                        fg=self._app.COLOURS["secondary"],
                        font=("Segoe UI", 8, "italic")
                    ).pack(anchor="w")
            else:
                # Convert species name to display name
                species_display_map = {
                    "Koala": "koalas",
                    "Kangaroo": "kangaroos",
                    "Wombat": "wombats",
                    "Platypus": "platypuses",
                    "Emu": "emus",
                    "WedgeTailedEagle": "wedge-tailed eagles",
                    "SaltwaterCroc": "saltwater crocodiles",
                    "FrilledLizard": "frilled lizards"
                }
                species_display = species_display_map.get(mission.target_animal, mission.target_animal.lower())
                
                tk.Label(
                    animal_progress,
                    text=f"⚠ No happy {species_display} found (need happiness ≥ 70%)",
                    bg=self._app.COLOURS["card_bg"],
                    fg=self._app.COLOURS["danger"],
                    font=("Segoe UI", 8, "italic")
                ).pack(anchor="w")
        
        # Reward info
        tk.Label(
            self._content_frame,
            text=f"💰 Reward: {mission.reward.description}",
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["success"],
            font=("Segoe UI", 9, "italic")
        ).pack(anchor="w")
        
        # Status indicator
        if mission.is_complete:
            status_text = "✓ Complete! Collect reward on next day."
            status_color = self._app.COLOURS["success"]
        elif mission.is_failed:
            status_text = "✗ Mission Failed"
            status_color = self._app.COLOURS["danger"]
        elif mission.days_remaining <= 2:
            status_text = f"⚠ Only {mission.days_remaining} days left!"
            status_color = self._app.COLOURS["accent"]
        else:
            status_text = f"⏰ {mission.days_remaining} days remaining"
            status_color = self._app.COLOURS["text"]
        
        tk.Label(
            self._content_frame,
            text=status_text,
            bg=self._app.COLOURS["card_bg"],
            fg=status_color,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(10, 0))
    
    def update_display(self) -> None:
        """Public method to update the display."""
        self._refresh()
