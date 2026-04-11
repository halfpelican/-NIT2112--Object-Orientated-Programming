"""
OzZoo Enclosure View Frame
Enclosure management with cleaning and animal assignment.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..app import OzZooApp
    from ...models.enclosure import Enclosure


class EnclosureViewFrame(tk.Frame):
    """
    Enclosure management frame.
    
    Features:
    - Grid of enclosure cards with status
    - Detail view showing animals in enclosure
    - Clean enclosure button
    - Cleanliness progress bar
    - Capacity indicator
    """
    
    def __init__(self, parent: tk.Frame, app: OzZooApp):
        super().__init__(parent, bg=app.COLOURS["background"])
        self._app = app
        self._zoo = app.zoo
        self._selected_enclosure: Optional[Enclosure] = None
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Build the enclosure view UI."""
        if not self._zoo:
            self._show_no_zoo_message()
            return
        
        # Header
        header = tk.Label(
            self,
            text="🏕️ Enclosure Management",
            bg=self._app.COLOURS["background"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 24, "bold")
        )
        header.pack(anchor="w", pady=(0, 10))
        
        # Main container
        main_container = tk.Frame(self, bg=self._app.COLOURS["background"])
        main_container.pack(fill="both", expand=True)
        
        # Left - Enclosure grid
        self._create_enclosure_grid(main_container)
        
        # Right - Detail panel
        self._create_detail_panel(main_container)
    
    def _show_no_zoo_message(self) -> None:
        """Display message when no zoo is loaded."""
        label = tk.Label(
            self,
            text="No zoo loaded.",
            bg=self._app.COLOURS["background"]
        )
        label.pack(expand=True)
    
    def _create_enclosure_grid(self, parent: tk.Frame) -> None:
        """Create the enclosure cards grid."""
        grid_frame = tk.Frame(parent, bg=self._app.COLOURS["card_bg"])
        grid_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Scrollable grid
        canvas = tk.Canvas(
            grid_frame,
            bg=self._app.COLOURS["card_bg"],
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            grid_frame,
            orient="vertical",
            command=canvas.yview
        )
        self._enclosures_frame = tk.Frame(canvas, bg=self._app.COLOURS["card_bg"])
        
        self._enclosures_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self._enclosures_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        self._refresh_enclosure_grid()
    
    def _refresh_enclosure_grid(self) -> None:
        """Refresh the enclosure grid."""
        for widget in self._enclosures_frame.winfo_children():
            widget.destroy()
        
        row, col = 0, 0
        for enclosure in self._zoo.enclosures.values():
            card = self._create_enclosure_card(enclosure)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            col += 1
            if col >= 2:
                col = 0
                row += 1
    
    def _create_enclosure_card(self, enclosure: Enclosure) -> tk.Frame:
        """Create a card for an enclosure."""
        # Status icon based on cleanliness
        if enclosure.is_dirty:
            icon = "⚠️"
            border_colour = self._app.COLOURS["danger"]
        elif enclosure.cleanliness > 70:
            icon = "✨"
            border_colour = self._app.COLOURS["success"]
        else:
            icon = "🧹"
            border_colour = self._app.COLOURS["accent"]

        predation_risk, _ = self._zoo.get_enclosure_predation_status(enclosure.enclosure_id)
        if predation_risk >= self._zoo.PREDATION_HIGH_RISK_THRESHOLD:
            icon = "🚨"
            border_colour = self._app.COLOURS["danger"]
        elif predation_risk >= self._zoo.PREDATION_LOW_RISK_THRESHOLD:
            icon = "⚠️"
            border_colour = self._app.COLOURS["accent"]
        
        card = tk.Frame(
            self._enclosures_frame,
            bg=self._app.COLOURS["card_bg"],
            relief="raised",
            borderwidth=2,
            cursor="hand2"
        )
        
        # Colour strip at top
        strip = tk.Frame(card, bg=border_colour, height=5)
        strip.pack(fill="x")
        
        # Content area
        content = tk.Frame(card, bg=self._app.COLOURS["card_bg"])
        content.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Enclosure name
        name_label = tk.Label(
            content,
            text=f"{icon} {enclosure.name}",
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 12, "bold")
        )
        name_label.pack(anchor="w")
        
        # Habitat type
        type_label = tk.Label(
            content,
            text=enclosure.get_habitat_type().replace("_", " ").title(),
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["secondary"],
            font=("Segoe UI", 9)
        )
        type_label.pack(anchor="w")
        
        # Capacity indicator
        capacity_label = tk.Label(
            content,
            text=f"Animals: {len(enclosure.animals)}/{enclosure.capacity}",
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 10)
        )
        capacity_label.pack(anchor="w", pady=(5, 0))

        if predation_risk > 0:
            risk_colour = (
                self._app.COLOURS["danger"]
                if predation_risk >= self._zoo.PREDATION_HIGH_RISK_THRESHOLD
                else self._app.COLOURS["accent"]
            )
            tk.Label(
                content,
                text=f"Predation Risk: {predation_risk}%",
                bg=self._app.COLOURS["card_bg"],
                fg=risk_colour,
                font=("Segoe UI", 9, "bold"),
            ).pack(anchor="w", pady=(2, 0))
        
        # Cleanliness progress bar
        clean_frame = tk.Frame(content, bg=self._app.COLOURS["card_bg"])
        clean_frame.pack(fill="x", pady=(5, 0))
        
        tk.Label(
            clean_frame,
            text=f"Clean: {enclosure.cleanliness}%",
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 9)
        ).pack(anchor="w")
        
        bar_bg = tk.Frame(
            clean_frame,
            bg=self._app.COLOURS["border"],
            height=8
        )
        bar_bg.pack(fill="x", pady=2)
        
        bar_fill = tk.Frame(bar_bg, bg=border_colour, height=8)
        bar_fill.place(relwidth=enclosure.cleanliness / 100, relheight=1)
        
        # Bind click event to all widgets
        for widget in [card, content, name_label, type_label, capacity_label]:
            widget.bind(
                "<Button-1>",
                lambda e, enc=enclosure: self._select_enclosure(enc)
            )
        
        return card
    
    def _create_detail_panel(self, parent: tk.Frame) -> None:
        """Create the detail panel on the right side."""
        self._detail_frame = tk.Frame(
            parent,
            bg=self._app.COLOURS["card_bg"],
            width=400
        )
        self._detail_frame.pack(side="right", fill="both", expand=True)
        self._detail_frame.pack_propagate(False)
        
        placeholder = tk.Label(
            self._detail_frame,
            text="Select an enclosure to view details",
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["secondary"]
        )
        placeholder.pack(expand=True)
    
    def _select_enclosure(self, enclosure: Enclosure) -> None:
        """Select an enclosure and show its details."""
        self._selected_enclosure = enclosure
        self._show_enclosure_details(enclosure)
    
    def _show_enclosure_details(self, enclosure: Enclosure) -> None:
        """Display detailed information about the enclosure."""
        for widget in self._detail_frame.winfo_children():
            widget.destroy()
        
        # Header section
        header = tk.Frame(self._detail_frame, bg=self._app.COLOURS["primary"])
        header.pack(fill="x")
        
        tk.Label(
            header,
            text=f"🏕️ {enclosure.name}",
            bg=self._app.COLOURS["primary"],
            fg=self._app.COLOURS["text_light"],
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", padx=15, pady=10)
        
        tk.Label(
            header,
            text=enclosure.get_habitat_type().replace("_", " ").title(),
            bg=self._app.COLOURS["primary"],
            fg=self._app.COLOURS["text_light"],
            font=("Segoe UI", 12)
        ).pack(anchor="w", padx=15, pady=(0, 10))
        
        # Statistics section
        stats_frame = tk.Frame(self._detail_frame, bg=self._app.COLOURS["card_bg"])
        stats_frame.pack(fill="x", padx=15, pady=15)
        
        tk.Label(
            stats_frame,
            text=f"Capacity: {len(enclosure.animals)}/{enclosure.capacity}",
            bg=self._app.COLOURS["card_bg"],
            font=("Segoe UI", 11)
        ).pack(anchor="w")
        
        tk.Label(
            stats_frame,
            text=f"Cleanliness: {enclosure.cleanliness}%",
            bg=self._app.COLOURS["card_bg"],
            font=("Segoe UI", 11)
        ).pack(anchor="w")

        tk.Label(
            stats_frame,
            text=(
                f"Barrier Level: {enclosure.barrier_level}/"
                f"{enclosure.MAX_BARRIER_LEVEL}"
            ),
            bg=self._app.COLOURS["card_bg"],
            font=("Segoe UI", 11),
        ).pack(anchor="w")
        
        tk.Label(
            stats_frame,
            text=f"Compatible: {', '.join(enclosure.get_compatible_species())}",
            bg=self._app.COLOURS["card_bg"],
            font=("Segoe UI", 10),
            wraplength=350
        ).pack(anchor="w", pady=(5, 0))

        predation_risk, predation_summary = self._zoo.get_enclosure_predation_status(
            enclosure.enclosure_id
        )
        if predation_summary:
            predation_colour = (
                self._app.COLOURS["danger"]
                if predation_risk >= self._zoo.PREDATION_HIGH_RISK_THRESHOLD
                else self._app.COLOURS["accent"]
            )
            tk.Label(
                stats_frame,
                text=f"Predation Risk: {predation_risk}%\n{predation_summary}",
                bg=self._app.COLOURS["card_bg"],
                fg=predation_colour,
                font=("Segoe UI", 10, "bold"),
                justify="left",
                wraplength=350,
            ).pack(anchor="w", pady=(6, 0))
        
        # Animals in enclosure section
        animals_frame = tk.LabelFrame(
            self._detail_frame,
            text="Animals",
            bg=self._app.COLOURS["card_bg"],
            font=("Segoe UI", 10, "bold")
        )
        animals_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        if enclosure.animals:
            for animal in enclosure.animals:
                # Health status indicator
                if animal.health > 50:
                    status = "🟢"
                elif animal.health > 20:
                    status = "🟡"
                else:
                    status = "🔴"
                
                tk.Label(
                    animals_frame,
                    text=f"{status} {animal.name} ({animal.species})",
                    bg=self._app.COLOURS["card_bg"],
                    font=("Segoe UI", 10)
                ).pack(anchor="w", padx=10, pady=2)
        else:
            tk.Label(
                animals_frame,
                text="No animals in this enclosure",
                bg=self._app.COLOURS["card_bg"],
                fg=self._app.COLOURS["secondary"]
            ).pack(pady=10)
        
        # Action buttons section
        actions_frame = tk.Frame(self._detail_frame, bg=self._app.COLOURS["card_bg"])
        actions_frame.pack(fill="x", padx=15, pady=15)

        relocation_frame = tk.Frame(self._detail_frame, bg=self._app.COLOURS["card_bg"])
        relocation_frame.pack(fill="x", padx=15, pady=15)
        
        clean_btn = tk.Button(
            actions_frame,
            text="🧹 Clean Enclosure",
            command=lambda: self._clean_enclosure(enclosure),
            bg=self._app.COLOURS["secondary"],
            fg=self._app.COLOURS["text_light"],
            font=("Segoe UI", 11),
            relief=tk.FLAT,
            padx=20,
            pady=10
        )
        clean_btn.pack(side="left")

        reinforce_btn = tk.Button(
            actions_frame,
            text=f"🛡️ Reinforce Barrier (${self._zoo.BARRIER_UPGRADE_COST:,.0f})",
            command=lambda: self._on_reinforce_barrier(enclosure),
            bg=self._app.COLOURS["primary"],
            fg=self._app.COLOURS["text_light"],
            font=("Segoe UI", 11),
            relief=tk.FLAT,
            padx=20,
            pady=10,
        )
        reinforce_btn.pack(side="left", padx=(10, 0))

        if enclosure.get_habitat_type() == "billabong":
            relocate_btn = tk.Button(
                relocation_frame,
                text=f"🚚 Emergency Relocate Platypus (${self._zoo.EMERGENCY_RELOCATION_COST:,.0f})",
                command=lambda: self._on_emergency_relocate_platypus(enclosure),
                bg=self._app.COLOURS["accent"],
                fg=self._app.COLOURS["text_light"],
                font=("Segoe UI", 11),
                relief=tk.FLAT,
                padx=20,
                pady=10,
            )
            relocate_btn.pack(side="left", padx=(10, 0))
    
    def _clean_enclosure(self, enclosure: Enclosure) -> None:
        """Clean the selected enclosure."""
        result = enclosure.clean()
        self._app.show_info("Clean Enclosure", result)
        self._refresh_enclosure_grid()
        self._show_enclosure_details(enclosure)

    def _on_reinforce_barrier(self, enclosure: Enclosure) -> None:
        """Upgrade enclosure barriers and refresh UI."""
        success, message = self._zoo.reinforce_enclosure_barrier(enclosure.enclosure_id)
        if success:
            self._app.show_info("Barrier Upgrade", message)
            self._app.update_header_info()
        else:
            self._app.show_warning("Barrier Upgrade", message)
        self._refresh_enclosure_grid()
        self._show_enclosure_details(enclosure)

    def _on_emergency_relocate_platypus(self, enclosure: Enclosure) -> None:
        """Relocate one at-risk platypus to a safer billabong if possible."""
        success, message = self._zoo.emergency_relocate_platypus(enclosure.enclosure_id)
        if success:
            self._app.show_info("Emergency Relocation", message)
            self._app.update_header_info()
        else:
            self._app.show_warning("Emergency Relocation", message)
        self._refresh_enclosure_grid()
        self._show_enclosure_details(enclosure)
