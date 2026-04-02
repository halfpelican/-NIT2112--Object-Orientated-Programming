"""
OzZoo Settings Frame
Save game, load game, return to main menu, quit.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk, filedialog
from typing import TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
    from ..app import OzZooApp


class SettingsFrame(tk.Frame):
    """
    Settings frame with save/load and navigation options.
    """
    
    def __init__(self, parent: tk.Frame, app: OzZooApp):
        super().__init__(parent, bg=app.COLOURS["background"])
        self._app = app
        self._zoo = app.zoo
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        # Header
        tk.Label(
            self,
            text="⚙️ Settings",
            bg=self._app.COLOURS["background"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 24, "bold")
        ).pack(anchor="w", pady=(0, 20))
        
        # Cards container
        cards = tk.Frame(self, bg=self._app.COLOURS["background"])
        cards.pack(fill="both", expand=True)
        
        # Save/Load section
        save_card = tk.LabelFrame(cards, text="💾 Save & Load", bg=self._app.COLOURS["card_bg"], font=("Segoe UI", 12, "bold"))
        save_card.pack(fill="x", pady=10)
        
        btn_frame = tk.Frame(save_card, bg=self._app.COLOURS["card_bg"])
        btn_frame.pack(pady=20)
        
        tk.Button(
            btn_frame,
            text="💾 Save Game",
            command=self._on_save,
            bg=self._app.COLOURS["success"],
            fg=self._app.COLOURS["text_light"],
            font=("Segoe UI", 12),
            relief=tk.FLAT,
            padx=30,
            pady=10
        ).pack(side="left", padx=10)
        
        tk.Button(
            btn_frame,
            text="📂 Load Game",
            command=self._on_load,
            bg=self._app.COLOURS["accent"],
            fg=self._app.COLOURS["text_light"],
            font=("Segoe UI", 12),
            relief=tk.FLAT,
            padx=30,
            pady=10
        ).pack(side="left", padx=10)
        
        # Game info section
        if self._zoo:
            info_card = tk.LabelFrame(cards, text="📊 Game Info", bg=self._app.COLOURS["card_bg"], font=("Segoe UI", 12, "bold"))
            info_card.pack(fill="x", pady=10)
            
            report = self._zoo.get_daily_report()
            info_text = f"""Zoo Name: {self._zoo.name}
Current Day: {report['day']}
Budget: ${report['budget']:,.2f}
Total Animals: {report['animal_count']}
Total Enclosures: {report['enclosure_count']}
Animals Born: {report['animals_born']}
Animals Died: {report['animals_died']}
Total Revenue: ${report['total_revenue']:,.2f}
Total Expenses: ${report['total_expenses']:,.2f}"""
            
            tk.Label(
                info_card,
                text=info_text,
                bg=self._app.COLOURS["card_bg"],
                fg=self._app.COLOURS["text"],
                font=("Segoe UI", 11),
                justify="left"
            ).pack(anchor="w", padx=20, pady=15)
        
        # Navigation section
        nav_card = tk.LabelFrame(cards, text="🚪 Navigation", bg=self._app.COLOURS["card_bg"], font=("Segoe UI", 12, "bold"))
        nav_card.pack(fill="x", pady=10)
        
        nav_frame = tk.Frame(nav_card, bg=self._app.COLOURS["card_bg"])
        nav_frame.pack(pady=20)
        
        tk.Button(
            nav_frame,
            text="🏠 Main Menu",
            command=self._on_main_menu,
            bg=self._app.COLOURS["secondary"],
            fg=self._app.COLOURS["text_light"],
            font=("Segoe UI", 12),
            relief=tk.FLAT,
            padx=30,
            pady=10
        ).pack(side="left", padx=10)
        
        tk.Button(
            nav_frame,
            text="🚪 Quit Game",
            command=self._on_quit,
            bg=self._app.COLOURS["danger"],
            fg=self._app.COLOURS["text_light"],
            font=("Segoe UI", 12),
            relief=tk.FLAT,
            padx=30,
            pady=10
        ).pack(side="left", padx=10)
    
    def _on_save(self) -> None:
        """Save the current game."""
        from ...models.zoo import save_game
        
        saves_dir = Path(__file__).parent.parent.parent / "saves"
        saves_dir.mkdir(exist_ok=True)
        
        filepath = filedialog.asksaveasfilename(
            title="Save Game",
            initialdir=saves_dir,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        
        if filepath:
            try:
                save_game(self._zoo, Path(filepath))
                self._app.show_info("Save Game", "Game saved successfully!")
                self._app.set_status(f"Saved to {Path(filepath).name}")
            except Exception as e:
                self._app.show_error("Save Error", str(e))
    
    def _on_load(self) -> None:
        """Load a saved game."""
        from ...models.zoo import load_game
        
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
                self._app.show_info("Load Game", f"Loaded game: Day {zoo.day}")
                self._app.show_frame("zoo_status")
            except Exception as e:
                self._app.show_error("Load Error", str(e))
    
    def _on_main_menu(self) -> None:
        """Return to main menu."""
        if self._app.ask_yes_no("Main Menu", "Return to main menu? Unsaved progress will be lost."):
            # Clear navigation
            for widget in self._app._nav_frame.winfo_children():
                widget.destroy()
            self._app.zoo = None
            self._app.show_frame("main_menu")
    
    def _on_quit(self) -> None:
        """Quit the game."""
        if self._app.ask_yes_no("Quit", "Are you sure you want to quit? Unsaved progress will be lost."):
            self._app.destroy()
