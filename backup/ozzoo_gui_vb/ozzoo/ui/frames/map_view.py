"""
Zoo Map View Frame
Visual grid-based map for placing enclosures, scenery, and shops.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..app import OzZooApp

from ...models.map_tile import TileType, ITEM_INFO, PLACEMENT_COSTS


class MapViewFrame(tk.Frame):
    """
    Map view frame showing 10x10 grid where players can place items.
    """
    
    TILE_SIZE = 55  # Pixels per tile
    
    # Tile colors by type
    TILE_COLORS = {
        TileType.EMPTY: "#90EE90",        # Light green (grass)
        TileType.ENCLOSURE: "#8B4513",    # Brown
        TileType.SCENERY: "#2E8B57",      # Sea green
        TileType.SHOP: "#FFD700",         # Gold
    }
    
    def __init__(self, parent: tk.Frame, app: OzZooApp):
        super().__init__(parent, bg=app.COLOURS["background"])
        self._app = app
        self._zoo = app.zoo
        self._selected_tile = None
        self._tile_buttons = {}  # Store tile button references
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the map view UI."""
        # Header
        header = tk.Frame(self, bg=self._app.COLOURS["background"])
        header.pack(fill="x", pady=(0, 10))
        
        tk.Label(
            header,
            text="🗺️ Zoo Map",
            bg=self._app.COLOURS["background"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 24, "bold")
        ).pack(side="left")
        
        # Budget display
        self._budget_label = tk.Label(
            header,
            text=f"💰 Budget: ${self._zoo.budget:,.2f}",
            bg=self._app.COLOURS["background"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 14)
        )
        self._budget_label.pack(side="right", padx=20)
        
        # Main container (grid + sidebar)
        main_container = tk.Frame(self, bg=self._app.COLOURS["background"])
        main_container.pack(fill="both", expand=True)
        
        # Left: Map grid
        self._create_map_grid(main_container)
        
        # Right: Item palette
        self._create_item_palette(main_container)
        
        # Bottom: Info panel
        self._create_info_panel()
    
    def _create_map_grid(self, parent: tk.Frame) -> None:
        """Create the 10x10 map grid."""
        grid_frame = tk.Frame(parent, bg=self._app.COLOURS["card_bg"], relief="solid", borderwidth=2)
        grid_frame.pack(side="left", padx=10, pady=10)
        
        # Title
        tk.Label(
            grid_frame,
            text="Zoo Layout",
            bg=self._app.COLOURS["card_bg"],
            font=("Segoe UI", 12, "bold")
        ).grid(row=0, column=0, columnspan=10, pady=5)
        
        # Create grid tiles
        for x in range(self._zoo.GRID_SIZE):
            for y in range(self._zoo.GRID_SIZE):
                tile = self._zoo.get_tile(x, y)
                
                # Create tile button
                btn = tk.Button(
                    grid_frame,
                    text=self._get_tile_display(tile),
                    width=4,
                    height=2,
                    bg=self.TILE_COLORS[tile.tile_type],
                    relief="raised",
                    borderwidth=1,
                    command=lambda tx=x, ty=y: self._on_tile_click(tx, ty),
                    font=("Segoe UI Emoji", 12)
                )
                btn.grid(row=y+1, column=x, padx=1, pady=1)
                self._tile_buttons[(x, y)] = btn
                
                # Hover tooltips
                self._bind_hover(btn, tile)
    
    def _create_item_palette(self, parent: tk.Frame) -> None:
        """Create sidebar with placeable items."""
        palette_frame = tk.Frame(parent, bg=self._app.COLOURS["card_bg"], relief="solid", borderwidth=2)
        palette_frame.pack(side="right", fill="y", padx=10, pady=10)
        
        # Title
        tk.Label(
            palette_frame,
            text="🛠️ Build Menu",
            bg=self._app.COLOURS["card_bg"],
            font=("Segoe UI", 14, "bold")
        ).pack(pady=10)
        
        # Scrollable frame
        canvas = tk.Canvas(palette_frame, bg=self._app.COLOURS["card_bg"], width=250, highlightthickness=0)
        scrollbar = ttk.Scrollbar(palette_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self._app.COLOURS["card_bg"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        def _is_inside_palette(widget: tk.Misc | None) -> bool:
            while widget is not None:
                if widget == palette_frame:
                    return True
                widget = widget.master
            return False

        def _on_mousewheel(event: tk.Event) -> str:
            target = self.winfo_containing(event.x_root, event.y_root)
            if not _is_inside_palette(target):
                return "break"
            if event.delta == 0:
                return "break"
            step = -1 if event.delta > 0 else 1
            canvas.yview_scroll(step, "units")
            return "break"

        def _on_mousewheel_linux(event: tk.Event) -> str:
            target = self.winfo_containing(event.x_root, event.y_root)
            if not _is_inside_palette(target):
                return "break"
            if getattr(event, "num", None) == 4:
                canvas.yview_scroll(-1, "units")
            elif getattr(event, "num", None) == 5:
                canvas.yview_scroll(1, "units")
            return "break"

        def _cleanup_mousewheel_bindings(event: tk.Event) -> None:
            if event.widget is self:
                canvas.unbind_all("<MouseWheel>")
                canvas.unbind_all("<Button-4>")
                canvas.unbind_all("<Button-5>")
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", _on_mousewheel_linux)
        canvas.bind_all("<Button-5>", _on_mousewheel_linux)
        self.bind("<Destroy>", _cleanup_mousewheel_bindings)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Enclosures section
        self._add_palette_section(scrollable_frame, "🏕️ Enclosures", [
            "eucalyptus_grove", "outback_savanna", "billabong",
            "rainforest_aviary", "reptile_house"
        ])
        
        # Scenery section
        self._add_palette_section(scrollable_frame, "🌳 Scenery", [
            "tree", "rock", "water", "flowers", "bush"
        ])
        
        # Shops section
        self._add_palette_section(scrollable_frame, "🏪 Facilities", [
            "food-stall", "ticket-booth", "restroom", "visitor-center", "bench"
        ])
        
        # Clear selection button
        tk.Button(
            palette_frame,
            text="❌ Clear Tile",
            command=self._on_clear_selection,
            bg=self._app.COLOURS["danger"],
            fg=self._app.COLOURS["text_light"],
            font=("Segoe UI", 10),
            relief="flat",
            padx=10,
            pady=5
        ).pack(pady=10)
    
    def _add_palette_section(self, parent: tk.Frame, title: str, items: list) -> None:
        """Add a section of items to the palette."""
        section = tk.LabelFrame(
            parent,
            text=title,
            bg=self._app.COLOURS["card_bg"],
            font=("Segoe UI", 11, "bold")
        )
        section.pack(fill="x", padx=10, pady=5)
        
        for item_id in items:
            info = ITEM_INFO.get(item_id, {})
            emoji = info.get("emoji", "")
            name = info.get("name", item_id)
            cost = PLACEMENT_COSTS.get(item_id, 0)
            
            btn = tk.Button(
                section,
                text=f"{emoji} {name}\n${cost:,}",
                command=lambda i=item_id: self._on_item_select(i),
                bg=self._app.COLOURS["primary"],
                fg=self._app.COLOURS["text_light"],
                font=("Segoe UI", 9),
                relief="raised",
                padx=5,
                pady=5,
                wraplength=200
            )
            btn.pack(fill="x", padx=5, pady=3)
    
    def _create_info_panel(self) -> None:
        """Create bottom info panel."""
        self._info_panel = tk.Label(
            self,
            text="Click a tile to select it, then choose an item from the Build Menu to place.",
            bg=self._app.COLOURS["secondary"],
            fg=self._app.COLOURS["text_light"],
            font=("Segoe UI", 10),
            anchor="w",
            padx=10,
            pady=8
        )
        self._info_panel.pack(fill="x", side="bottom")
    
    def _get_tile_display(self, tile) -> str:
        """Get emoji display for a tile."""
        if tile.is_empty:
            return ""
        
        # Check if it's a known item
        if tile.item_id in ITEM_INFO:
            return ITEM_INFO[tile.item_id]["emoji"]
        
        # For enclosures or unknown items
        if tile.tile_type == TileType.ENCLOSURE:
            return "🏕️"
        
        return "❓"
    
    def _bind_hover(self, button: tk.Button, tile) -> None:
        """Bind hover events for tooltips."""
        def on_enter(e):
            if tile.is_empty:
                info = f"Empty tile ({tile.x}, {tile.y})"
            else:
                item_name = ITEM_INFO.get(tile.item_id, {}).get("name", tile.item_id or "Unknown")
                info = f"{item_name} at ({tile.x}, {tile.y})"
            self._info_panel.config(text=info)
        
        def on_leave(e):
            self._info_panel.config(text="Click a tile to select it, then choose an item from the Build Menu to place.")
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
    
    def _on_tile_click(self, x: int, y: int) -> None:
        """Handle tile click."""
        # Clear previous selection highlight
        if self._selected_tile:
            old_x, old_y = self._selected_tile
            old_tile = self._zoo.get_tile(old_x, old_y)
            old_btn = self._tile_buttons.get((old_x, old_y))
            if old_btn:
                # Reset to normal appearance
                old_btn.config(
                    bg=self.TILE_COLORS[old_tile.tile_type],
                    relief="raised",
                    borderwidth=1
                )
        
        # Set new selection
        self._selected_tile = (x, y)
        tile = self._zoo.get_tile(x, y)
        
        # Highlight selected tile
        btn = self._tile_buttons.get((x, y))
        if btn:
            btn.config(
                bg=self._app.COLOURS["accent"],  # Orange highlight
                relief="sunken",
                borderwidth=3
            )
        
        if tile.is_empty:
            self._info_panel.config(
                text=f"Selected empty tile ({x}, {y}). Choose an item from the Build Menu to place here."
            )
        else:
            item_name = ITEM_INFO.get(tile.item_id, {}).get("name", tile.item_id or "Item")
            self._info_panel.config(
                text=f"Selected {item_name} at ({x}, {y}). Click 'Clear Tile' to remove it."
            )
    
    def _on_item_select(self, item_id: str) -> None:
        """Handle item selection from palette."""
        if not self._selected_tile:
            self._app.show_warning("No Tile Selected", "Please click a tile on the map first.")
            return
        
        x, y = self._selected_tile
        
        # Check if this is a multi-tile enclosure
        item_info = ITEM_INFO.get(item_id, {})
        size = item_info.get("size", (1, 1))
        
        # Determine tile type
        if item_id in ["eucalyptus_grove", "outback_savanna", "billabong", "rainforest_aviary", "reptile_house"]:
            # This is an enclosure - create it first
            self._place_enclosure(x, y, item_id, size)
        elif item_id in ["tree", "rock", "water", "flowers", "bush"]:
            tile_type = TileType.SCENERY
            self._place_single_item(x, y, item_id, tile_type)
        else:
            tile_type = TileType.SHOP
            self._place_single_item(x, y, item_id, tile_type)
    
    def _place_single_item(self, x: int, y: int, item_id: str, tile_type: TileType) -> None:
        """Place a single-tile item."""
        # Place item
        success, message = self._zoo.place_item(x, y, item_id, tile_type)
        
        if success:
            self._app.set_status(message)
            self._refresh_tile(x, y)
            self._update_budget_display()
            self._app.update_header_info()
        else:
            self._app.show_warning("Cannot Place Item", message)
    
    def _place_enclosure(self, x: int, y: int, enclosure_type: str, size: tuple) -> None:
        """Place a multi-tile enclosure."""
        from ...models.enclosure import create_enclosure
        from ...models.map_tile import PLACEMENT_COSTS
        from ...exceptions import InsufficientFundsError
        
        # Check cost
        cost = PLACEMENT_COSTS.get(enclosure_type, 0)
        if cost > 0 and self._zoo.budget < cost:
            self._app.show_warning(
                "Insufficient Funds",
                f"You need ${cost:,} to build this enclosure.\nCurrent budget: ${self._zoo.budget:,.2f}"
            )
            return
        
        # Check if area is clear (3x3)
        width, height = size
        for dx in range(width):
            for dy in range(height):
                check_x, check_y = x + dx, y + dy
                if check_x >= self._zoo.GRID_SIZE or check_y >= self._zoo.GRID_SIZE:
                    self._app.show_warning(
                        "Cannot Place Enclosure",
                        f"Enclosure extends beyond map boundary.\nNeed {width}x{height} space starting from selected tile."
                    )
                    return
                
                tile = self._zoo.get_tile(check_x, check_y)
                if not tile.is_empty:
                    self._app.show_warning(
                        "Cannot Place Enclosure",
                        f"Enclosure space is blocked at ({check_x}, {check_y}).\nNeed {width}x{height} clear space."
                    )
                    return
        
        # Deduct cost (place_item won't deduct since display_id has cost=0)
        if cost > 0:
            self._zoo._budget -= cost
            self._zoo._total_expenses += cost
        
        # Create the enclosure
        enc_id = f"enc_{enclosure_type}_{len(self._zoo.enclosures) + 1}"
        name_map = {
            "eucalyptus_grove": "Eucalyptus Grove",
            "outback_savanna": "Outback Savanna",
            "billabong": "Billabong Wetland",
            "rainforest_aviary": "Rainforest Aviary",
            "reptile_house": "Reptile House"
        }
        enc_name = name_map.get(enclosure_type, "New Enclosure")
        
        try:
            enclosure = create_enclosure(enclosure_type, enc_id, name=enc_name)
            self._zoo.add_enclosure(enclosure)
            
            # Place on all tiles
            emoji_map = {
                "eucalyptus_grove": "enclosure_koala",
                "outback_savanna": "enclosure_outback",
                "billabong": "enclosure_billabong",
                "rainforest_aviary": "enclosure_aviary",
                "reptile_house": "enclosure_reptile"
            }
            display_id = emoji_map.get(enclosure_type, "enclosure_koala")
            
            for dx in range(width):
                for dy in range(height):
                    tile_x, tile_y = x + dx, y + dy
                    self._zoo.place_item(tile_x, tile_y, display_id, TileType.ENCLOSURE, enclosure)
                    self._refresh_tile(tile_x, tile_y)
            
            cost_msg = f" for ${cost:,}" if cost > 0 else ""
            self._app.show_info(
                "Enclosure Placed!",
                f"{enc_name} has been built{cost_msg}!\nYou can now add animals to it from the Shop."
            )
            self._update_budget_display()
            self._app.update_header_info()
            
        except Exception as e:
            # Refund on error
            if cost > 0:
                self._zoo._budget += cost
                self._zoo._total_expenses -= cost
            self._app.show_error("Placement Failed", str(e))
    
    def _on_clear_selection(self) -> None:
        """Clear the selected tile."""
        if not self._selected_tile:
            self._app.show_warning("No Tile Selected", "Please click a tile on the map first.")
            return
        
        x, y = self._selected_tile
        success, message = self._zoo.remove_item(x, y)
        
        if success:
            self._app.set_status(message)
            self._refresh_tile(x, y)
        else:
            self._app.show_warning("Cannot Remove", message)
    
    def _refresh_tile(self, x: int, y: int) -> None:
        """Refresh a single tile's display."""
        tile = self._zoo.get_tile(x, y)
        btn = self._tile_buttons.get((x, y))
        
        if btn:
            # Check if this is the selected tile
            is_selected = self._selected_tile == (x, y)
            
            btn.config(
                text=self._get_tile_display(tile),
                bg=self._app.COLOURS["accent"] if is_selected else self.TILE_COLORS[tile.tile_type],
                relief="sunken" if is_selected else "raised",
                borderwidth=3 if is_selected else 1
            )
    
    def _update_budget_display(self) -> None:
        """Update the budget label with current budget."""
        self._budget_label.config(text=f"💰 Budget: ${self._zoo.budget:,.2f}")
