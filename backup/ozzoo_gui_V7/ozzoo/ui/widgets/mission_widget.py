"""
Mission Display Widget
Shows active mission progress in the UI.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..app import OzZooApp

from ...models.mission import Mission, MissionType


class MissionWidget(tk.Frame):
    """Widget displaying all active mission statuses."""

    def __init__(self, parent: tk.Frame, app: OzZooApp):
        super().__init__(parent, bg=app.COLOURS["card_bg"], relief="raised", bd=2)
        self._app = app
        self._zoo = app.zoo
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the mission display UI."""
        title_frame = tk.Frame(self, bg=self._app.COLOURS["primary"])
        title_frame.pack(fill="x")
        self._title_label = tk.Label(
            title_frame,
            text="🎯 Active Missions",
            bg=self._app.COLOURS["primary"],
            fg=self._app.COLOURS["text_light"],
            font=("Segoe UI", 12, "bold"),
            pady=5,
        )
        self._title_label.pack()

        self._content_frame = tk.Frame(self, bg=self._app.COLOURS["card_bg"])
        self._content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self._refresh()

    def _mission_type_label(self, mission: Mission) -> str:
        """Return friendly mission type label."""
        type_labels = {
            MissionType.KEEP_HAPPY: "Keep Happy",
            MissionType.BREED_ANIMALS: "Breeding",
            MissionType.VISITOR_COUNT: "Visitors",
            MissionType.PROFIT_TARGET: "Profit",
            MissionType.BUILD_ENCLOSURES: "Expansion",
        }
        return type_labels.get(mission.mission_type, mission.mission_type.value)

    def _status_line(self, mission: Mission) -> tuple[str, str]:
        """Return (status_text, status_color) for mission card footer."""
        if mission.is_complete:
            return "✓ Complete", self._app.COLOURS["success"]
        if mission.is_failed:
            return "✗ Failed", self._app.COLOURS["danger"]
        if mission.duration_days > 0 and mission.days_remaining <= 2:
            return f"⚠ Only {mission.days_remaining} day(s) left", self._app.COLOURS["accent"]
        if mission.duration_days > 0:
            return f"⏰ {mission.days_remaining} day(s) remaining", self._app.COLOURS["text"]
        return "⏰ No time limit", self._app.COLOURS["text"]

    def _add_keep_happy_context(self, parent: tk.Frame, mission: Mission) -> None:
        """Add contextual details for KEEP_HAPPY missions."""
        target_species = mission.target_animal
        if not target_species:
            return

        happy_animals = [
            animal
            for animal in self._zoo.animals.values()
            if (
                animal.is_alive
                and not animal.is_sick
                and animal.species == target_species
                and animal.happiness >= 70
            )
        ]
        required_count = mission.target_value
        requirements_met = len(happy_animals) >= required_count
        status_color = (
            self._app.COLOURS["success"] if requirements_met else self._app.COLOURS["danger"]
        )
        status_text = (
            f"✓ {len(happy_animals)}/{required_count} happy today"
            if requirements_met
            else f"✗ {len(happy_animals)}/{required_count} happy today"
        )

        tk.Label(
            parent,
            text=status_text,
            bg=self._app.COLOURS["card_bg"],
            fg=status_color,
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", pady=(2, 0))

    def _add_mission_card(self, mission: Mission) -> None:
        """Render one mission card."""
        card = tk.Frame(
            self._content_frame,
            bg=self._app.COLOURS["card_bg"],
            relief="groove",
            borderwidth=1,
            padx=8,
            pady=8,
        )
        card.pack(fill="x", pady=(0, 8))

        header = tk.Frame(card, bg=self._app.COLOURS["card_bg"])
        header.pack(fill="x")
        tk.Label(
            header,
            text=mission.title,
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left", anchor="w")
        tk.Label(
            header,
            text=self._mission_type_label(mission),
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["secondary"],
            font=("Segoe UI", 8, "bold"),
        ).pack(side="right", anchor="e")

        tk.Label(
            card,
            text=mission.description,
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 8),
            wraplength=760,
            justify="left",
        ).pack(anchor="w", pady=(4, 6))

        progress_text = mission.get_status_text()
        tk.Label(
            card,
            text=f"Progress: {progress_text}",
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 8),
        ).pack(anchor="w")

        progress_pct = mission.get_progress_percentage()
        bar = ttk.Progressbar(
            card,
            orient="horizontal",
            mode="determinate",
            maximum=100,
            value=progress_pct,
        )
        bar.pack(fill="x", pady=(3, 5))

        if mission.mission_type == MissionType.KEEP_HAPPY:
            self._add_keep_happy_context(card, mission)

        tk.Label(
            card,
            text=f"💰 Reward: {mission.reward.description}",
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["success"],
            font=("Segoe UI", 8, "italic"),
        ).pack(anchor="w", pady=(2, 0))

        status_text, status_color = self._status_line(mission)
        tk.Label(
            card,
            text=status_text,
            bg=self._app.COLOURS["card_bg"],
            fg=status_color,
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", pady=(2, 0))

    def _refresh(self) -> None:
        """Refresh mission display."""
        for widget in self._content_frame.winfo_children():
            widget.destroy()

        active_missions = self._zoo.active_missions if self._zoo else []
        self._title_label.config(text=f"🎯 Active Missions ({len(active_missions)})")

        if not active_missions:
            tk.Label(
                self._content_frame,
                text="No active missions.\nA new mission arrives every 3 days.",
                bg=self._app.COLOURS["card_bg"],
                fg=self._app.COLOURS["secondary"],
                font=("Segoe UI", 10, "italic"),
                justify="center",
            ).pack(pady=20)
            return

        for mission in active_missions:
            self._add_mission_card(mission)

    def update_display(self) -> None:
        """Public method to update the display."""
        self._refresh()

