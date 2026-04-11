"""
OzZoo Shop Frame
Purchase food, medicine, and new animals.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..app import OzZooApp


class ShopFrame(tk.Frame):
    """
    Shop frame with tabs for Food, Medicine, and Animals.
    
    Features:
    - Tabbed interface for different shop categories
    - Current stock display
    - Price list with buy buttons
    - Quantity spinbox for purchases
    - Budget display
    """
    
    def __init__(self, parent: tk.Frame, app: OzZooApp):
        super().__init__(parent, bg=app.COLOURS["background"])
        self._app = app
        self._zoo = app.zoo
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the shop user interface."""
        if not self._zoo:
            tk.Label(
                self,
                text="No zoo loaded.",
                bg=self._app.COLOURS["background"]
            ).pack(expand=True)
            return
        
        # Header with budget
        header = tk.Frame(self, bg=self._app.COLOURS["background"])
        header.pack(fill="x", pady=(0, 10))
        
        tk.Label(
            header,
            text="🛒 Zoo Shop",
            bg=self._app.COLOURS["background"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 24, "bold")
        ).pack(side="left")
        
        self._budget_label = tk.Label(
            header,
            text=f"💰 Budget: ${self._zoo.budget:,.2f}",
            bg=self._app.COLOURS["background"],
            fg=self._app.COLOURS["success"],
            font=("Segoe UI", 16, "bold")
        )
        self._budget_label.pack(side="right")
        
        # Notebook for tabs
        style = ttk.Style()
        style.configure("TNotebook.Tab", font=("Segoe UI", 11))
        
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)
        
        # Create tabs
        self._create_food_tab(notebook)
        self._create_medicine_tab(notebook)
        self._create_animals_tab(notebook)
    
    def _create_food_tab(self, notebook: ttk.Notebook) -> None:
        """Create the food purchasing tab."""
        from ...models.resources import FOOD_TYPES
        
        frame = tk.Frame(notebook, bg=self._app.COLOURS["card_bg"])
        notebook.add(frame, text="🍖 Food")
        
        # Current stock header
        stock_frame = tk.LabelFrame(
            frame,
            text="Current Stock",
            bg=self._app.COLOURS["card_bg"]
        )
        stock_frame.pack(fill="x", padx=15, pady=10)
        
        stock_text = "  |  ".join(
            [f"{k}: {v}" for k, v in self._zoo.food_stock.items()]
        )
        tk.Label(
            stock_frame,
            text=stock_text,
            bg=self._app.COLOURS["card_bg"],
            font=("Segoe UI", 10)
        ).pack(pady=10)
        
        # Food items for purchase
        items_frame = tk.Frame(frame, bg=self._app.COLOURS["card_bg"])
        items_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        for food_type, food in FOOD_TYPES.items():
            self._create_purchase_row(
                items_frame,
                food_type,
                food.name,
                food.cost,
                "food"
            )
    
    def _create_medicine_tab(self, notebook: ttk.Notebook) -> None:
        """Create the medicine purchasing tab."""
        from ...models.resources import MEDICINE_TYPES
        
        frame = tk.Frame(notebook, bg=self._app.COLOURS["card_bg"])
        notebook.add(frame, text="💊 Medicine")
        
        # Current stock
        stock_frame = tk.LabelFrame(
            frame,
            text="Current Stock",
            bg=self._app.COLOURS["card_bg"]
        )
        stock_frame.pack(fill="x", padx=15, pady=10)
        
        stock_text = "  |  ".join(
            [f"{k}: {v}" for k, v in self._zoo.medicine_stock.items()]
        )
        tk.Label(
            stock_frame,
            text=stock_text,
            bg=self._app.COLOURS["card_bg"],
            font=("Segoe UI", 10)
        ).pack(pady=10)
        
        # Medicine items
        items_frame = tk.Frame(frame, bg=self._app.COLOURS["card_bg"])
        items_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        for med_type, medicine in MEDICINE_TYPES.items():
            treats = ", ".join(medicine.treats)
            self._create_purchase_row(
                items_frame,
                med_type,
                f"{medicine.name} (treats: {treats})",
                medicine.cost,
                "medicine"
            )
    
    def _create_animals_tab(self, notebook: ttk.Notebook) -> None:
        """Create the animals purchasing tab."""
        from ...patterns.factory import AnimalFactory
        
        frame = tk.Frame(notebook, bg=self._app.COLOURS["card_bg"])
        notebook.add(frame, text="🦘 Animals")
        
        # Scrollable frame
        canvas = tk.Canvas(
            frame,
            bg=self._app.COLOURS["card_bg"],
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=self._app.COLOURS["card_bg"])
        
        scrollable.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Animal purchase cards
        all_info = AnimalFactory.get_all_animal_info()
        for animal_type, info in all_info.items():
            self._create_animal_card(scrollable, animal_type, info)
    
    def _create_enclosures_tab(self, notebook: ttk.Notebook) -> None:
        """Create the enclosure purchasing tab."""
        from ...models.enclosure import ENCLOSURE_TYPES
        
        frame = tk.Frame(notebook, bg=self._app.COLOURS["card_bg"])
        notebook.add(frame, text="🏕️ Enclosures")
        
        # Info header
        info_frame = tk.LabelFrame(
            frame,
            text="Build New Enclosures",
            bg=self._app.COLOURS["card_bg"],
            font=("Segoe UI", 11, "bold")
        )
        info_frame.pack(fill="x", padx=15, pady=10)
        
        tk.Label(
            info_frame,
            text="Purchase enclosures to house more animals. After purchase, place them on the Zoo Map.",
            bg=self._app.COLOURS["card_bg"],
            font=("Segoe UI", 9),
            wraplength=600
        ).pack(pady=10, padx=10)
        
        # Scrollable frame
        canvas = tk.Canvas(
            frame,
            bg=self._app.COLOURS["card_bg"],
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=self._app.COLOURS["card_bg"])
        
        scrollable.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Enclosure types with info
        enclosure_info = {
            "eucalyptus_grove": {
                "name": "Eucalyptus Grove",
                "emoji": "🐨",
                "capacity": 8,
                "cost": 5000,
                "description": "Perfect for koalas and other eucalyptus-loving animals"
            },
            "outback_savanna": {
                "name": "Outback Savanna",
                "emoji": "🦘",
                "capacity": 10,
                "cost": 6000,
                "description": "Wide open spaces for kangaroos, emus, and wombats"
            },
            "billabong": {
                "name": "Billabong Wetland",
                "emoji": "🐊",
                "capacity": 6,
                "cost": 7000,
                "description": "Aquatic habitat for crocodiles and water-loving animals"
            },
            "rainforest_aviary": {
                "name": "Rainforest Aviary",
                "emoji": "🦅",
                "capacity": 12,
                "cost": 5500,
                "description": "High canopy for birds of all kinds"
            },
            "reptile_house": {
                "name": "Reptile House",
                "emoji": "🦎",
                "capacity": 10,
                "cost": 6500,
                "description": "Climate-controlled environment for reptiles"
            }
        }
        
        for enc_type, info in enclosure_info.items():
            self._create_enclosure_card(scrollable, enc_type, info)
    
    def _create_enclosure_card(
        self,
        parent: tk.Frame,
        enclosure_type: str,
        info: dict
    ) -> None:
        """Create a card for purchasing an enclosure."""
        card = tk.Frame(
            parent,
            bg=self._app.COLOURS["background"],
            relief="raised",
            bd=2
        )
        card.pack(fill="x", padx=15, pady=8)
        
        # Info section
        info_section = tk.Frame(card, bg=self._app.COLOURS["background"])
        info_section.pack(side="left", fill="x", expand=True, padx=15, pady=12)
        
        # Title row
        title_frame = tk.Frame(info_section, bg=self._app.COLOURS["background"])
        title_frame.pack(anchor="w", fill="x")
        
        tk.Label(
            title_frame,
            text=f"{info['emoji']} {info['name']}",
            bg=self._app.COLOURS["background"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 13, "bold")
        ).pack(side="left")
        
        # Details
        tk.Label(
            info_section,
            text=info["description"],
            bg=self._app.COLOURS["background"],
            fg=self._app.COLOURS["secondary"],
            font=("Segoe UI", 9),
            wraplength=400
        ).pack(anchor="w", pady=(3, 0))
        
        tk.Label(
            info_section,
            text=f"Capacity: {info['capacity']} animals | Size: 3x3 tiles",
            bg=self._app.COLOURS["background"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(3, 0))
        
        tk.Label(
            info_section,
            text=f"Cost: ${info['cost']:,}",
            bg=self._app.COLOURS["background"],
            fg=self._app.COLOURS["success"],
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", pady=(5, 0))
        
        # Purchase button
        buy_btn = tk.Button(
            card,
            text="Purchase",
            command=lambda: self._buy_enclosure(enclosure_type, info),
            bg=self._app.COLOURS["primary"],
            fg=self._app.COLOURS["text_light"],
            font=("Segoe UI", 11),
            relief=tk.FLAT,
            padx=25,
            pady=10
        )
        buy_btn.pack(side="right", padx=15, pady=12)
    
    def _buy_enclosure(self, enclosure_type: str, info: dict) -> None:
        """Purchase an enclosure (to be placed on map later)."""
        from ...exceptions import InsufficientFundsError
        
        if self._zoo.budget < info['cost']:
            self._app.show_warning(
                "Insufficient Funds",
                f"You need ${info['cost']:,} to purchase this enclosure.\n"
                f"Current budget: ${self._zoo.budget:,.2f}"
            )
            return
        
        # Deduct cost
        self._zoo._budget -= info['cost']
        self._zoo._total_expenses += info['cost']
        
        self._app.show_info(
            "Enclosure Purchased!",
            f"{info['emoji']} {info['name']} purchased for ${info['cost']:,}!\n\n"
            f"Go to the Zoo Map to place your new enclosure.\n"
            f"It requires a 3x3 space."
        )
        
        self._update_budget()
        self._app.update_header_info()
    
    def _create_purchase_row(
        self,
        parent: tk.Frame,
        item_type: str,
        name: str,
        cost: float,
        category: str
    ) -> None:
        """Create a row for purchasing an item."""
        row = tk.Frame(
            parent,
            bg=self._app.COLOURS["background"],
            relief="raised",
            bd=1
        )
        row.pack(fill="x", pady=5)
        
        # Item info
        info_frame = tk.Frame(row, bg=self._app.COLOURS["background"])
        info_frame.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        
        tk.Label(
            info_frame,
            text=name,
            bg=self._app.COLOURS["background"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w")
        
        tk.Label(
            info_frame,
            text=f"${cost:.2f} each",
            bg=self._app.COLOURS["background"],
            fg=self._app.COLOURS["success"],
            font=("Segoe UI", 10)
        ).pack(anchor="w")
        
        # Quantity and buy
        buy_frame = tk.Frame(row, bg=self._app.COLOURS["background"])
        buy_frame.pack(side="right", padx=10, pady=10)
        
        qty_var = tk.IntVar(value=1)
        spinbox = ttk.Spinbox(
            buy_frame,
            from_=1,
            to=99,
            textvariable=qty_var,
            width=5
        )
        spinbox.pack(side="left", padx=5)
        
        buy_btn = tk.Button(
            buy_frame,
            text="Buy",
            command=lambda: self._buy_item(item_type, qty_var.get(), category),
            bg=self._app.COLOURS["primary"],
            fg=self._app.COLOURS["text_light"],
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=15
        )
        buy_btn.pack(side="left")
    
    def _create_animal_card(
        self,
        parent: tk.Frame,
        animal_type: str,
        info: dict
    ) -> None:
        """Create a card for purchasing an animal."""
        card = tk.Frame(
            parent,
            bg=self._app.COLOURS["card_bg"],
            relief="raised",
            bd=1
        )
        card.pack(fill="x", padx=15, pady=5)
        
        # Info
        info_frame = tk.Frame(card, bg=self._app.COLOURS["card_bg"])
        info_frame.pack(side="left", fill="x", expand=True, padx=15, pady=10)
        
        tk.Label(
            info_frame,
            text=info["display_name"],
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w")
        
        habitat_display = info["habitat"].replace("_", " ").title()
        tk.Label(
            info_frame,
            text=(
                f"Category: {info['category'].title()} | "
                f"Diet: {info['diet'].title()} | "
                f"Habitat: {habitat_display}"
            ),
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["secondary"],
            font=("Segoe UI", 9)
        ).pack(anchor="w")
        
        tk.Label(
            info_frame,
            text=f"${info['cost']:.2f}",
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["success"],
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w")
        
        # Buy button
        buy_btn = tk.Button(
            card,
            text="Purchase",
            command=lambda: self._buy_animal_dialog(animal_type, info),
            bg=self._app.COLOURS["primary"],
            fg=self._app.COLOURS["text_light"],
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=20,
            pady=8
        )
        buy_btn.pack(side="right", padx=15, pady=10)
    
    def _buy_item(self, item_type: str, quantity: int, category: str) -> None:
        """Purchase food or medicine."""
        if category == "food":
            success, msg = self._zoo.buy_food(item_type, quantity)
        else:
            success, msg = self._zoo.buy_medicine(item_type, quantity)
        
        if success:
            self._app.show_info("Purchase Complete", msg)
        else:
            self._app.show_warning("Purchase Failed", msg)
        
        self._update_budget()
        self._app.update_header_info()
    
    def _buy_animal_dialog(self, animal_type: str, info: dict) -> None:
        """Show dialogue to purchase an animal."""
        # Create dialogue
        dialog = tk.Toplevel(self._app)
        dialog.title(f"Purchase {info['display_name']}")
        dialog.geometry("450x500")
        dialog.transient(self._app)
        dialog.grab_set()
        
        # Form
        form = tk.Frame(dialog, bg=self._app.COLOURS["card_bg"])
        form.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(
            form,
            text=f"Purchase {info['display_name']}",
            bg=self._app.COLOURS["card_bg"],
            font=("Segoe UI", 14, "bold")
        ).pack(pady=(0, 15))
        
        tk.Label(
            form,
            text=f"Cost: ${info['cost']:.2f}",
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["success"]
        ).pack()
        
        # Name entry
        tk.Label(
            form,
            text="Animal Name:",
            bg=self._app.COLOURS["card_bg"]
        ).pack(anchor="w", pady=(15, 5))
        name_var = tk.StringVar()
        tk.Entry(form, textvariable=name_var, width=30).pack(anchor="w")
        
        # Age entry
        tk.Label(
            form,
            text="Age (years):",
            bg=self._app.COLOURS["card_bg"]
        ).pack(anchor="w", pady=(10, 5))
        age_var = tk.IntVar(value=2)
        ttk.Spinbox(
            form,
            from_=0,
            to=50,
            textvariable=age_var,
            width=10
        ).pack(anchor="w")
        
        # Gender selection
        tk.Label(
            form,
            text="Gender:",
            bg=self._app.COLOURS["card_bg"]
        ).pack(anchor="w", pady=(10, 5))
        gender_var = tk.StringVar(value="unknown")
        gender_frame = tk.Frame(form, bg=self._app.COLOURS["card_bg"])
        gender_frame.pack(anchor="w")
        for g in ["male", "female", "unknown"]:
            tk.Radiobutton(
                gender_frame,
                text=g.title(),
                variable=gender_var,
                value=g,
                bg=self._app.COLOURS["card_bg"]
            ).pack(side="left")
        
        # Enclosure selection
        tk.Label(
            form,
            text="Enclosure:",
            bg=self._app.COLOURS["card_bg"]
        ).pack(anchor="w", pady=(10, 5))
        
        # Get all non-full enclosures (both compatible and incompatible)
        all_encs = [e for e in self._zoo.enclosures.values() if not e.is_full]
        compatible_encs = [
            e for e in all_encs
            if e.get_habitat_type() == info["habitat"]
        ]
        incompatible_encs = [
            e for e in all_encs
            if e.get_habitat_type() != info["habitat"]
        ]
        
        enc_var = tk.StringVar()
        enc_ids = []
        enc_types = []  # Track if compatible or not
        enc_combo = None
        
        if all_encs:
            enc_options = []
            # Add compatible enclosures first
            for e in compatible_encs:
                enc_options.append(
                    f"{e.name} ({len(e.animals)}/{e.capacity}) - {e.get_habitat_type().replace('_', ' ').title()}"
                )
                enc_ids.append(e.enclosure_id)
                enc_types.append(True)  # Compatible
            
            # Add incompatible enclosures with warning
            for e in incompatible_encs:
                enc_options.append(
                    f"{e.name} ({len(e.animals)}/{e.capacity}) - {e.get_habitat_type().replace('_', ' ').title()} [WRONG HABITAT!]"
                )
                enc_ids.append(e.enclosure_id)
                enc_types.append(False)  # Incompatible
            
            enc_combo = ttk.Combobox(
                form,
                textvariable=enc_var,
                values=enc_options,
                state="readonly",
                width=50
            )
            enc_combo.pack(anchor="w")
            enc_combo.current(0)
            
            # Show warning label
            warning_label = tk.Label(
                form,
                text="⚠ Animals placed in wrong habitats will have health issues!",
                bg=self._app.COLOURS["card_bg"],
                fg=self._app.COLOURS["accent"],
                font=("Segoe UI", 9, "italic")
            )
            warning_label.pack(anchor="w", pady=(5, 0))
        else:
            tk.Label(
                form,
                text="No available enclosure!",
                bg=self._app.COLOURS["card_bg"],
                fg=self._app.COLOURS["danger"]
            ).pack(anchor="w")
        
        def do_purchase():
            name = name_var.get().strip()
            if not name:
                self._app.show_warning(
                    "Invalid Name",
                    "Please enter a name for the animal."
                )
                return
            if not all_encs:
                self._app.show_warning(
                    "No Enclosure",
                    "Build an enclosure first!"
                )
                return
            
            enc_idx = enc_combo.current() if all_encs else -1
            if enc_idx < 0:
                return
            
            enc_id = enc_ids[enc_idx]
            is_compatible = enc_types[enc_idx]
            
            # Prevent purchase if placing in wrong habitat
            if not is_compatible:
                from tkinter import messagebox
                messagebox.showwarning(
                    "Wrong Habitat Warning!",
                    f"{name} ({info['display_name']}) cannot be placed in this enclosure!\n\n"
                    f"Required Habitat: {info['habitat'].replace('_', ' ').title()}\n"
                    f"Selected Enclosure: {self._zoo.enclosures[enc_id].get_habitat_type().replace('_', ' ').title()}\n\n"
                    f"This animal will suffer health problems and may die!\n\n"
                    f"Please select a compatible enclosure."
                )
                return
            
            try:
                self._zoo.purchase_animal(
                    animal_type,
                    name,
                    age_var.get(),
                    enc_id,
                    gender_var.get()
                )
                self._app.show_info(
                    "Purchase Complete",
                    f"Welcome {name} to OzZoo! They are happy in their new home."
                )
                self._update_budget()
                self._app.update_header_info()
                dialog.destroy()
            except Exception as e:
                self._app.show_error("Purchase Failed", str(e))
        
        # Buttons
        btn_frame = tk.Frame(form, bg=self._app.COLOURS["card_bg"])
        btn_frame.pack(pady=20)
        
        tk.Button(
            btn_frame,
            text="Purchase",
            command=do_purchase,
            bg=self._app.COLOURS["primary"],
            fg=self._app.COLOURS["text_light"]
        ).pack(side="left", padx=5)
        
        tk.Button(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            bg=self._app.COLOURS["secondary"],
            fg=self._app.COLOURS["text_light"]
        ).pack(side="left", padx=5)
    
    def _update_budget(self) -> None:
        """Update the budget display."""
        self._budget_label.config(text=f"💰 Budget: ${self._zoo.budget:,.2f}")
