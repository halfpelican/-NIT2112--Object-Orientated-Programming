"""
OzZoo Animal View Frame
List and detail views for animals with feed/heal actions.
"""

from __future__ import annotations
import random
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
        list_frame = tk.Frame(parent, bg=self._app.COLOURS["card_bg"], width=200)
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
            text=(
                f"{animal.species} | Health: {animal.health}% | Hunger: {animal.hunger}% | "
                f"{'🤒 Sick' if animal.is_sick else '✅ Healthy'}"
            ),
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

        condition_label = tk.Label(
            header,
            text="🤒 Sick - needs treatment" if animal.is_sick else "✅ Healthy",
            bg=self._app.COLOURS["primary"],
            fg=self._app.COLOURS["accent"] if animal.is_sick else self._app.COLOURS["text_light"],
            font=("Segoe UI", 10, "bold")
        )
        condition_label.pack(anchor="w", padx=15, pady=(0, 10))
        
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
Condition: {"Sick" if animal.is_sick else "Healthy"}
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
        care_frame = tk.Frame(self._detail_frame, bg=self._app.COLOURS["card_bg"])
        care_frame.pack(fill="x", padx=15, pady=10)
        interaction_frame = tk.Frame(self._detail_frame, bg=self._app.COLOURS["card_bg"])
        interaction_frame.pack(fill="x", padx=15, pady=10)
        
        # Feed button
        feed_btn = tk.Button(
            care_frame,
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
            care_frame,
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

        treat_btn = tk.Button(
            care_frame,
            text="🤒 Treat",
            command=lambda: self._treat_animal(animal),
            bg=self._app.COLOURS["danger"],
            fg=self._app.COLOURS["text_light"],
            font=("Segoe UI", 11),
            relief=tk.FLAT,
            padx=15,
            pady=8
        )
        treat_btn.pack(side="left", padx=5)
        if not animal.is_sick:
            treat_btn.configure(
                state=tk.DISABLED,
                bg=self._app.COLOURS["border"],
                fg=self._app.COLOURS["secondary"]
            )
        
        # Make Sound button
        sound_btn = tk.Button(
            interaction_frame,
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

        # Feeding Frenzy mini-game button
        frenzy_btn = tk.Button(
            interaction_frame,
            text="🎮 Feeding Frenzy",
            command=lambda: self._play_feeding_frenzy(animal),
            bg=self._app.COLOURS["primary"],
            fg=self._app.COLOURS["text_light"],
            font=("Segoe UI", 11),
            relief=tk.FLAT,
            padx=15,
            pady=8
        )
        frenzy_btn.pack(side="left", padx=5)
    
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
        from ...models.resources import MEDICINE_TYPES

        med_key = self._find_available_medicine(animal)
        if not med_key:
            self._app.show_warning("Heal Animal", "No suitable medicine in stock! Buy some from the shop.")
            return
        
        # Apply medicine (MEDICINE_TYPES contains Medicine objects directly)
        medicine = MEDICINE_TYPES[med_key]
        healing = medicine.apply(animal)
        
        self._zoo._medicine_stock[med_key] -= 1
        
        self._app.show_info("Heal Animal", f"{animal.name} was healed! Health +{healing}")
        self._app.update_header_info()
        self._show_animal_details(animal)
        self._refresh_animal_list()

    def _treat_animal(self, animal: Animal) -> None:
        """Treat sickness using medicine stock."""
        if not animal.is_alive:
            self._app.show_warning("Treat Animal", f"{animal.name} is no longer alive.")
            return
        if not animal.is_sick:
            self._app.show_info("Treat Animal", f"{animal.name} is not sick.")
            return

        med_key = self._find_available_medicine(animal)
        if not med_key:
            self._app.show_warning("Treat Animal", "No suitable medicine in stock! Buy some from the shop.")
            return

        success, msg = self._zoo.treat_sick_animal(animal.name, med_key)
        if success:
            self._app.show_info("Treat Animal", msg)
        else:
            self._app.show_warning("Treat Animal", msg)

        self._app.update_header_info()
        self._show_animal_details(animal)
        self._refresh_animal_list()

    def _find_available_medicine(self, animal: Animal) -> Optional[str]:
        """Find suitable medicine key for an animal based on available stock."""
        animal_type = animal.get_animal_type()
        type_map = {"mammal": "mammal_specialist", "bird": "avian", "reptile": "reptile"}
        specific_key = type_map.get(animal_type)

        if specific_key and self._zoo.medicine_stock.get(specific_key, 0) > 0:
            return specific_key
        if self._zoo.medicine_stock.get("general", 0) > 0:
            return "general"
        return None
    
    def _make_sound(self, animal: Animal) -> None:
        """Make the animal produce its sound."""
        sound = animal.make_sound()
        self._app.show_info("Animal Sound", sound)

    def _play_feeding_frenzy(self, animal: Animal) -> None:
        """Run interactive Feeding Frenzy and boost happiness."""
        if not animal.is_alive:
            self._app.show_warning("Feeding Frenzy", f"{animal.name} is no longer alive.")
            return

        total_attempts = self._zoo.feeding_frenzy_attempts_total
        if total_attempts <= 0:
            self._app.show_warning(
                "Feeding Frenzy",
                "No visitors are currently in the zoo. Advance the day to attract visitors."
            )
            return

        if self._zoo.feeding_frenzy_attempts_remaining <= 0:
            self._app.show_warning(
                "Feeding Frenzy",
                "No toss attempts remain for today. Advance the day for a new visitor pool."
            )
            return

        if sum(self._zoo.food_stock.values()) <= 0:
            self._app.show_warning(
                "Feeding Frenzy",
                "No food is in stock. Buy food before starting Feeding Frenzy."
            )
            return

        dialog = tk.Toplevel(self._app)
        dialog.title(f"🎮 Feeding Frenzy - {animal.name}")
        dialog.geometry("600x500")
        dialog.transient(self._app)
        dialog.grab_set()
        dialog.configure(bg=self._app.COLOURS["card_bg"])

        container = tk.Frame(dialog, bg=self._app.COLOURS["card_bg"])
        container.pack(fill="both", expand=True, padx=15, pady=15)

        tk.Label(
            container,
            text=f"Feed {animal.name} the right food ({animal.get_diet().title()})",
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w")

        tk.Label(
            container,
            text=(
                "Click Toss while the marker is inside the green target zone. "
                "Missing the zone has an injury risk."
            ),
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["secondary"],
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(2, 8))

        attempts_var = tk.StringVar()
        attempts_label = tk.Label(
            container,
            textvariable=attempts_var,
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 10, "bold")
        )
        attempts_label.pack(anchor="w", pady=(0, 8))

        meter_canvas = tk.Canvas(
            container,
            width=460,
            height=70,
            bg=self._app.COLOURS["background"],
            highlightthickness=1,
            highlightbackground=self._app.COLOURS["border"]
        )
        meter_canvas.pack(anchor="w", pady=(0, 8))

        meter_left = 30
        meter_right = 430
        meter_top = 20
        meter_bottom = 50
        initial_target_width = 90

        meter_canvas.create_rectangle(
            meter_left,
            meter_top,
            meter_right,
            meter_bottom,
            fill=self._app.COLOURS["border"],
            outline=""
        )
        target_left = random.randint(
            meter_left + 20,
            meter_right - initial_target_width - 20
        )
        target_right = target_left + initial_target_width
        target_id = meter_canvas.create_rectangle(
            target_left,
            meter_top,
            target_right,
            meter_bottom,
            fill=self._app.COLOURS["success"],
            outline=""
        )
        marker_id = meter_canvas.create_line(
            meter_left,
            meter_top - 5,
            meter_left,
            meter_bottom + 5,
            width=3,
            fill=self._app.COLOURS["danger"]
        )

        pref_frame = tk.Frame(container, bg=self._app.COLOURS["card_bg"])
        pref_frame.pack(fill="x", pady=(2, 8))
        tk.Label(
            pref_frame,
            text="Preference Meter",
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 10, "bold")
        ).pack(side="left")
        pref_value = tk.IntVar(value=0)
        pref_bar = ttk.Progressbar(
            pref_frame,
            orient="horizontal",
            mode="determinate",
            maximum=100,
            variable=pref_value,
            length=280
        )
        pref_bar.pack(side="left", padx=(10, 0))

        controls_frame = tk.Frame(container, bg=self._app.COLOURS["card_bg"])
        controls_frame.pack(anchor="w", pady=(4, 6))
        tk.Label(
            controls_frame,
            text="Toss Food:",
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 10)
        ).pack(side="left")

        available_food = sorted(
            food_type
            for food_type, quantity in self._zoo.food_stock.items()
            if quantity > 0
        )
        selected_food = tk.StringVar(
            value=animal.get_diet() if animal.get_diet() in available_food else available_food[0]
        )
        food_combo = ttk.Combobox(
            controls_frame,
            textvariable=selected_food,
            values=available_food,
            state="readonly",
            width=18
        )
        food_combo.pack(side="left", padx=(8, 0))
        food_stock_var = tk.StringVar(value="")
        tk.Label(
            container,
            textvariable=food_stock_var,
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["secondary"],
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(0, 4))

        score_var = tk.StringVar(value="Success: 0 | Misses: 0 | Rating: 0 out of 5 stars")
        tk.Label(
            container,
            textvariable=score_var,
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(2, 2))

        difficulty_var = tk.StringVar(value="Difficulty: Lv1 | Target width: 90 | Marker speed: 8.0")
        tk.Label(
            container,
            textvariable=difficulty_var,
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["accent"],
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(0, 2))

        status_var = tk.StringVar(value="Ready! Match the food and hit the green zone.")
        tk.Label(
            container,
            textvariable=status_var,
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["secondary"],
            wraplength=560,
            justify="left",
            font=("Segoe UI", 10, "italic")
        ).pack(anchor="w", pady=(0, 10))

        actions_frame = tk.Frame(container, bg=self._app.COLOURS["card_bg"])
        actions_frame.pack(anchor="w")
        toss_btn = tk.Button(
            actions_frame,
            text="🎯 Toss",
            bg=self._app.COLOURS["primary"],
            fg=self._app.COLOURS["text_light"],
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=16,
            pady=8
        )
        toss_btn.pack(side="left", padx=(0, 8))

        finish_btn = tk.Button(
            actions_frame,
            text="Finish Session",
            bg=self._app.COLOURS["secondary"],
            fg=self._app.COLOURS["text_light"],
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=12,
            pady=8
        )
        finish_btn.pack(side="left")

        state = {
            "marker_x": float(meter_left),
            "direction": 1.0,
            "attempts_used": 0,
            "successes": 0,
            "misses": 0,
            "preference": 0,
            "target_width": float(initial_target_width),
            "target_left": float(target_left),
            "target_right": float(target_right),
            "starting_health": animal.health,
            "injury_events": 0,
            "injury_damage": 0,
            "finished": False,
            "walked_away": False,
            "summary_shown": False,
        }
        walk_away_limit = 4
        min_target_width = 22.0
        shrink_per_success = 8.0
        injury_chance_on_zone_miss = 0.25
        injury_damage_min = 5
        injury_damage_max = 12

        def current_marker_speed() -> float:
            """Increase marker speed after each successful toss."""
            base_speed = 8.0
            linear_boost = state["successes"] * 1.4
            streak_boost = max(0, state["successes"] - 2) * 0.7
            return min(24.0, base_speed + linear_boost + streak_boost)

        def current_animation_delay_ms() -> int:
            """Reduce marker update delay as success streak grows."""
            return max(16, 35 - (state["successes"] * 3))

        def move_target_zone() -> None:
            """Relocate target zone after successful tosses."""
            min_left = meter_left + 20
            max_left = meter_right - int(state["target_width"]) - 20
            if max_left < min_left:
                max_left = min_left
            state["target_left"] = float(random.randint(min_left, max_left))
            state["target_right"] = state["target_left"] + state["target_width"]
            meter_canvas.coords(
                target_id,
                state["target_left"],
                meter_top,
                state["target_right"],
                meter_bottom
            )

        def refresh_food_options() -> None:
            """Refresh available food choices and selected-food stock display."""
            current_stock = self._zoo.food_stock
            in_stock_food = sorted(
                food_type for food_type, quantity in current_stock.items() if quantity > 0
            )

            if not in_stock_food:
                selected_food.set("")
                food_combo.config(values=[], state="disabled")
                food_stock_var.set("Food stock: empty")
                if not state["finished"]:
                    toss_btn.config(state="disabled")
                return

            current_selection = selected_food.get().strip().lower()
            if current_selection not in in_stock_food:
                preferred = animal.get_diet().lower()
                selected_food.set(preferred if preferred in in_stock_food else in_stock_food[0])

            if not state["finished"]:
                food_combo.config(values=in_stock_food, state="readonly")
                toss_btn.config(state="normal")

            selected = selected_food.get().strip().lower()
            food_stock_var.set(
                f"Stock: {selected.title()} ({current_stock.get(selected, 0)})"
            )

        def refresh_display() -> None:
            attempts_var.set(
                "Shared toss attempts today: "
                f"{self._zoo.feeding_frenzy_attempts_remaining}/{self._zoo.feeding_frenzy_attempts_total}"
            )
            pref_value.set(state["preference"])
            hit_ratio = 0.0
            if state["attempts_used"] > 0:
                hit_ratio = state["successes"] / state["attempts_used"]
            stars = max(1, min(5, round(hit_ratio * 5))) if state["attempts_used"] > 0 else 0
            score_var.set(
                f"Success: {state['successes']} | Misses: {state['misses']} | "
                f"Rating: {stars} out of 5 stars"
            )
            difficulty_var.set(
                f"Difficulty: Lv{state['successes'] + 1} | "
                f"Target width: {int(state['target_width'])} | "
                f"Marker speed: {current_marker_speed():.1f} | "
                f"Tick: {current_animation_delay_ms()}ms"
            )

        def finish_session(reason: str) -> None:
            if state["finished"]:
                return
            state["finished"] = True
            toss_btn.config(state="disabled")
            finish_btn.config(text="Close", command=dialog.destroy)
            food_combo.config(state="disabled")
            status_var.set(reason)
            refresh_display()

            if state["attempts_used"] == 0:
                return

            hit_ratio = state["successes"] / state["attempts_used"]
            stars = max(1, min(5, round(hit_ratio * 5)))
            stars_display = ("⭐" * stars) + ("☆" * (5 - stars))

            happiness_gain = min(25, (state["successes"] * 3) + (state["preference"] // 20))
            if state["walked_away"]:
                happiness_gain = max(0, happiness_gain - 5)

            old_happiness = animal.happiness
            if animal.is_alive:
                animal.happiness = old_happiness + happiness_gain
                actual_gain = animal.happiness - old_happiness
            else:
                actual_gain = 0

            self._app.update_header_info()
            self._show_animal_details(animal)
            self._refresh_animal_list()

            if not state["summary_shown"]:
                state["summary_shown"] = True
                summary = [
                    f"{animal.name} finished Feeding Frenzy!",
                    "",
                    f"Tosses used: {state['attempts_used']}",
                    f"Successful feeds: {state['successes']}",
                    f"Preference meter: {state['preference']}%",
                    f"Rating: {stars} out of 5 stars {stars_display}",
                    f"Happiness: {old_happiness}% → {animal.happiness}% (+{actual_gain})",
                    (
                        f"Health: {state['starting_health']}% → {animal.health}% "
                        f"({animal.health - state['starting_health']:+d})"
                    ),
                    "",
                    "Shared attempts left for all animals today: "
                    f"{self._zoo.feeding_frenzy_attempts_remaining}/{self._zoo.feeding_frenzy_attempts_total}",
                ]
                if state["injury_events"] > 0:
                    summary.append(
                        f"Injuries: {state['injury_events']} incident(s), "
                        f"-{state['injury_damage']} health total."
                    )
                if state["walked_away"]:
                    summary.append("Too many misses - the animal walked away unimpressed.")
                if not animal.is_alive:
                    summary.append(f"💀 {animal.name} did not survive the injuries.")
                self._app.show_info("Feeding Frenzy", "\n".join(summary))

        def toss_food() -> None:
            if state["finished"]:
                return

            selected_food_type = selected_food.get().strip().lower()
            if not selected_food_type:
                finish_session("No food stock remains. Buy more food to continue.")
                return

            consumed, consume_msg = self._zoo.use_feeding_frenzy_toss(selected_food_type)
            if not consumed:
                status_var.set(f"❌ {consume_msg}")
                refresh_food_options()
                if self._zoo.feeding_frenzy_attempts_remaining <= 0:
                    finish_session("No toss attempts remain for today.")
                elif sum(self._zoo.food_stock.values()) <= 0:
                    finish_session("No food stock remains. Buy more food to continue.")
                return

            state["attempts_used"] += 1

            in_target = state["target_left"] <= state["marker_x"] <= state["target_right"]
            correct_food = selected_food_type == animal.get_diet().lower()

            if in_target and correct_food:
                state["successes"] += 1
                state["preference"] = min(100, state["preference"] + 20)
                state["target_width"] = max(
                    min_target_width,
                    float(initial_target_width) - (state["successes"] * shrink_per_success)
                )
                move_target_zone()
                status_var.set(
                    "✅ Perfect toss! Correct food in target zone. "
                    "Difficulty increased: target narrowed and marker sped up."
                )
            else:
                state["misses"] += 1
                state["preference"] = max(0, state["preference"] - 10)

                injury_msg = ""
                if not in_target and random.random() < injury_chance_on_zone_miss:
                    damage_roll = random.randint(injury_damage_min, injury_damage_max)
                    prev_health = animal.health
                    animal.health = prev_health - damage_roll
                    damage_taken = max(0, prev_health - animal.health)
                    if damage_taken > 0:
                        state["injury_events"] += 1
                        state["injury_damage"] += damage_taken
                        injury_msg = (
                            f" ⚠ Injury! {animal.name} lost {damage_taken} health."
                        )
                    if not animal.is_alive:
                        refresh_display()
                        finish_session(
                            f"{animal.name} was critically injured after a missed toss."
                        )
                        return

                if not correct_food and not in_target:
                    status_var.set(
                        f"❌ Wrong food and missed target boundary.{injury_msg}"
                    )
                elif not correct_food:
                    status_var.set("❌ Wrong food for this animal.")
                else:
                    status_var.set(f"❌ Missed target boundary.{injury_msg}")

            refresh_display()
            refresh_food_options()

            if state["misses"] >= walk_away_limit:
                state["walked_away"] = True
                finish_session("Too many misses. The animal walked away unimpressed.")
            elif state["preference"] >= 100:
                finish_session("Preference meter filled! Great feeding session.")
            elif self._zoo.feeding_frenzy_attempts_remaining <= 0:
                finish_session("No toss attempts remain for today.")
            elif sum(self._zoo.food_stock.values()) <= 0:
                finish_session("No food stock remains. Buy more food to continue.")

        def animate_marker() -> None:
            if state["finished"] or not dialog.winfo_exists():
                return

            speed = current_marker_speed()
            next_x = state["marker_x"] + (speed * state["direction"])
            if next_x >= meter_right:
                next_x = float(meter_right)
                state["direction"] = -1.0
            elif next_x <= meter_left:
                next_x = float(meter_left)
                state["direction"] = 1.0

            state["marker_x"] = next_x
            meter_canvas.coords(
                marker_id,
                state["marker_x"],
                meter_top - 5,
                state["marker_x"],
                meter_bottom + 5
            )
            dialog.after(current_animation_delay_ms(), animate_marker)

        def on_close() -> None:
            if not state["finished"] and state["attempts_used"] > 0:
                finish_session("Session ended early.")
            dialog.destroy()

        toss_btn.config(command=toss_food)
        finish_btn.config(command=lambda: finish_session("Session finished by player."))
        food_combo.bind("<<ComboboxSelected>>", lambda _event: refresh_food_options())
        dialog.protocol("WM_DELETE_WINDOW", on_close)

        refresh_display()
        refresh_food_options()
        animate_marker()
