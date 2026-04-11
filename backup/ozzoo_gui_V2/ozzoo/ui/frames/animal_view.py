"""
OzZoo Animal View Frame
List and detail views for animals with feed/heal actions.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..app import OzZooApp
    from ...models.animal import Animal


class AnimalViewFrame(tk.Frame):
    """
    Animal management frame.
    
    Features:
    - List of all animals with status indicators
    - Filter by enclosure, health status, species
    - Detail panel showing selected animal's stats
    - Feed, Heal, and special action buttons
    - Health/Hunger/Happiness progress bars
    """
    
    def __init__(self, parent: tk.Frame, app: OzZooApp):
        super().__init__(parent, bg=app.COLOURS["background"])
        self._app = app
        self._zoo = app.zoo
        self._selected_animal: Optional[Animal] = None
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Build the animal view UI."""
        if not self._zoo:
            self._show_no_zoo_message()
            return
        
        # Header
        header = tk.Label(
            self,
            text="🦘 Animal Management",
            bg=self._app.COLOURS["background"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 24, "bold")
        )
        header.pack(anchor="w", pady=(0, 10))
        
        # Main container (left list, right details)
        main_container = tk.Frame(self, bg=self._app.COLOURS["background"])
        main_container.pack(fill="both", expand=True)
        
        # Left panel - Animal list
        self._create_animal_list(main_container)
        
        # Right panel - Animal details
        self._create_detail_panel(main_container)
    
    def _show_no_zoo_message(self) -> None:
        """Show message when no zoo is loaded."""
        label = tk.Label(
            self,
            text="No zoo loaded.",
            bg=self._app.COLOURS["background"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 14)
        )
        label.pack(expand=True)
    
    def _create_animal_list(self, parent: tk.Frame) -> None:
        """Create the animal list panel."""
        list_frame = tk.Frame(parent, bg=self._app.COLOURS["card_bg"], width=400)
        list_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        list_frame.pack_propagate(False)
        
        # Filter controls
        filter_frame = tk.Frame(list_frame, bg=self._app.COLOURS["card_bg"])
        filter_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(
            filter_frame,
            text="Filter:",
            bg=self._app.COLOURS["card_bg"],
            font=("Segoe UI", 10)
        ).pack(side="left")
        
        self._filter_var = tk.StringVar(value="all")
        filters = ["all", "hungry", "sick", "healthy"]
        for f in filters:
            rb = tk.Radiobutton(
                filter_frame,
                text=f.title(),
                variable=self._filter_var,
                value=f,
                bg=self._app.COLOURS["card_bg"],
                command=self._refresh_animal_list
            )
            rb.pack(side="left", padx=5)
        
        # Scrollable animal list
        list_container = tk.Frame(list_frame, bg=self._app.COLOURS["card_bg"])
        list_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        canvas = tk.Canvas(list_container, bg=self._app.COLOURS["card_bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
        self._animals_frame = tk.Frame(canvas, bg=self._app.COLOURS["card_bg"])
        
        self._animals_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self._animals_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self._refresh_animal_list()
    
    def _refresh_animal_list(self) -> None:
        """Refresh the animal list based on filter."""
        # Clear existing
        for widget in self._animals_frame.winfo_children():
            widget.destroy()
        
        filter_value = self._filter_var.get()
        animals = list(self._zoo.animals.values())
        
        # Apply filter
        if filter_value == "hungry":
            animals = [a for a in animals if a.is_alive and a.is_hungry]
        elif filter_value == "sick":
            animals = [a for a in animals if a.is_alive and a.is_sick]
        elif filter_value == "healthy":
            animals = [a for a in animals if a.is_alive and a.health > 50]
        else:
            animals = [a for a in animals if a.is_alive]
        
        if not animals:
            label = tk.Label(
                self._animals_frame,
                text="No animals match the filter.",
                bg=self._app.COLOURS["card_bg"],
                fg=self._app.COLOURS["text"]
            )
            label.pack(pady=20)
            return
        
        # Create animal cards
        for animal in animals:
            self._create_animal_card(animal)
    
    def _create_animal_card(self, animal: Animal) -> None:
        """Create a clickable card for an animal."""
        # Status icon
        if animal.is_sick:
            icon = "🔴"
        elif animal.is_hungry:
            icon = "🟡"
        else:
            icon = "🟢"
        
        card = tk.Frame(
            self._animals_frame,
            bg=self._app.COLOURS["background"],
            relief="raised",
            borderwidth=1,
            cursor="hand2"
        )
        card.pack(fill="x", pady=2)
        
        # Content
        content = tk.Frame(card, bg=self._app.COLOURS["background"])
        content.pack(fill="x", padx=10, pady=5)
        
        name_label = tk.Label(
            content,
            text=f"{icon} {animal.name}",
            bg=self._app.COLOURS["background"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 12, "bold")
        )
        name_label.pack(anchor="w")
        
        species_label = tk.Label(
            content,
            text=f"{animal.species} | Health: {animal.health}% | Hunger: {animal.hunger}%",
            bg=self._app.COLOURS["background"],
            fg=self._app.COLOURS["secondary"],
            font=("Segoe UI", 9)
        )
        species_label.pack(anchor="w")
        
        # Bind click to show details
        for widget in [card, content, name_label, species_label]:
            widget.bind("<Button-1>", lambda e, a=animal: self._select_animal(a))
    
    def _create_detail_panel(self, parent: tk.Frame) -> None:
        """Create the animal detail panel."""
        self._detail_frame = tk.Frame(parent, bg=self._app.COLOURS["card_bg"], width=400)
        self._detail_frame.pack(side="right", fill="both", expand=True)
        self._detail_frame.pack_propagate(False)
        
        # Placeholder text
        self._detail_placeholder = tk.Label(
            self._detail_frame,
            text="Select an animal to view details",
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["secondary"],
            font=("Segoe UI", 12)
        )
        self._detail_placeholder.pack(expand=True)
    
    def _select_animal(self, animal: Animal) -> None:
        """Select an animal and show its details."""
        self._selected_animal = animal
        self._show_animal_details(animal)
    
    def _show_animal_details(self, animal: Animal) -> None:
        """Display detailed information about an animal."""
        # Clear detail frame
        for widget in self._detail_frame.winfo_children():
            widget.destroy()
        
        # Animal name and species
        header = tk.Frame(self._detail_frame, bg=self._app.COLOURS["primary"])
        header.pack(fill="x")
        
        name_label = tk.Label(
            header,
            text=f"🦘 {animal.name}",
            bg=self._app.COLOURS["primary"],
            fg=self._app.COLOURS["text_light"],
            font=("Segoe UI", 18, "bold")
        )
        name_label.pack(anchor="w", padx=15, pady=10)
        
        species_label = tk.Label(
            header,
            text=f"{animal.species} ({animal.get_animal_type().title()})",
            bg=self._app.COLOURS["primary"],
            fg=self._app.COLOURS["text_light"],
            font=("Segoe UI", 12)
        )
        species_label.pack(anchor="w", padx=15, pady=(0, 10))
        
        # Stats section
        stats_frame = tk.Frame(self._detail_frame, bg=self._app.COLOURS["card_bg"])
        stats_frame.pack(fill="x", padx=15, pady=15)
        
        # Health bar
        self._create_stat_bar(stats_frame, "❤️ Health", animal.health, self._app.COLOURS["danger"])
        # Hunger bar
        self._create_stat_bar(stats_frame, "🍽️ Hunger", animal.hunger, self._app.COLOURS["accent"])
        # Happiness bar
        self._create_stat_bar(stats_frame, "😊 Happiness", animal.happiness, self._app.COLOURS["success"])
        
        # Info section
        info_frame = tk.LabelFrame(
            self._detail_frame,
            text="Info",
            bg=self._app.COLOURS["card_bg"],
            font=("Segoe UI", 10, "bold")
        )
        info_frame.pack(fill="x", padx=15, pady=10)
        
        info_text = f"""Age: {animal.age} years
Gender: {animal.gender.title()}
Diet: {animal.get_diet().title()}
Habitat: {animal.get_habitat_type().replace('_', ' ').title()}
Status: {"Alive" if animal.is_alive else "Deceased"}
Can Breed: {"Yes" if animal.can_breed else "No"}"""
        
        info_label = tk.Label(
            info_frame,
            text=info_text,
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 10),
            justify="left"
        )
        info_label.pack(anchor="w", padx=10, pady=10)
        
        # Actions section
        actions_frame = tk.Frame(self._detail_frame, bg=self._app.COLOURS["card_bg"])
        actions_frame.pack(fill="x", padx=15, pady=10)
        
        # Feed button
        feed_btn = tk.Button(
            actions_frame,
            text="🍖 Feed",
            command=lambda: self._feed_animal(animal),
            bg=self._app.COLOURS["accent"],
            fg=self._app.COLOURS["text_light"],
            font=("Segoe UI", 11),
            relief=tk.FLAT,
            padx=15,
            pady=8
        )
        feed_btn.pack(side="left", padx=5)
        
        # Heal button
        heal_btn = tk.Button(
            actions_frame,
            text="💊 Heal",
            command=lambda: self._heal_animal(animal),
            bg=self._app.COLOURS["success"],
            fg=self._app.COLOURS["text_light"],
            font=("Segoe UI", 11),
            relief=tk.FLAT,
            padx=15,
            pady=8
        )
        heal_btn.pack(side="left", padx=5)
        
        # Make Sound button
        sound_btn = tk.Button(
            actions_frame,
            text="🔊 Make Sound",
            command=lambda: self._make_sound(animal),
            bg=self._app.COLOURS["secondary"],
            fg=self._app.COLOURS["text_light"],
            font=("Segoe UI", 11),
            relief=tk.FLAT,
            padx=15,
            pady=8
        )
        sound_btn.pack(side="left", padx=5)
    
    def _create_stat_bar(self, parent: tk.Frame, label: str, value: int, colour: str) -> None:
        """Create a stat bar with label and progress."""
        frame = tk.Frame(parent, bg=self._app.COLOURS["card_bg"])
        frame.pack(fill="x", pady=5)
        
        lbl = tk.Label(
            frame,
            text=f"{label}: {value}%",
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 10),
            width=20,
            anchor="w"
        )
        lbl.pack(side="left")
        
        # Progress bar
        bar_frame = tk.Frame(frame, bg=self._app.COLOURS["border"], height=15)
        bar_frame.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        fill = tk.Frame(bar_frame, bg=colour, height=15)
        fill.place(relwidth=value/100, relheight=1)
    
    def _feed_animal(self, animal: Animal) -> None:
        """Feed the selected animal."""
        diet = animal.get_diet()
        success, msg = self._zoo.feed_animal(animal.name, diet)
        
        if success:
            self._app.show_info("Feed Animal", msg)
        else:
            self._app.show_warning("Feed Animal", msg)
        
        self._app.update_header_info()
        self._show_animal_details(animal)
        self._refresh_animal_list()
    
    def _heal_animal(self, animal: Animal) -> None:
        """Heal the selected animal."""
        from ...models.resources import MEDICINE_TYPES, Medicine
        
        # Find appropriate medicine
        animal_type = animal.get_animal_type()
        med_key = None
        
        # Try type-specific first
        type_map = {"mammal": "mammal_specialist", "bird": "avian", "reptile": "reptile"}
        if animal_type in type_map and self._zoo.medicine_stock.get(type_map[animal_type], 0) > 0:
            med_key = type_map[animal_type]
        elif self._zoo.medicine_stock.get("general", 0) > 0:
            med_key = "general"
        
        if not med_key:
            self._app.show_warning("Heal Animal", "No suitable medicine in stock! Buy some from the shop.")
            return
        
        # Apply medicine
        med_data = MEDICINE_TYPES[med_key]
        medicine = Medicine(**med_data)
        healing = medicine.apply(animal)
        
        self._zoo._medicine_stock[med_key] -= 1
        
        self._app.show_info("Heal Animal", f"{animal.name} was healed! Health +{healing}")
        self._app.update_header_info()
        self._show_animal_details(animal)
        self._refresh_animal_list()
    
    def _make_sound(self, animal: Animal) -> None:
        """Make the animal produce its sound."""
        sound = animal.make_sound()
        self._app.show_info("Animal Sound", sound)
