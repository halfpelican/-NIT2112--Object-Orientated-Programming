"""
OzZoo Status Dashboard Frame
Main dashboard showing zoo overview and quick actions.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk, simpledialog
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..app import OzZooApp


class ZooStatusFrame(tk.Frame):
    """
    Main dashboard frame showing zoo overview.
    
    Layout:
    ┌─────────────────────────────────────────────────┐
    │  DAILY REPORT (Day X)                           │
    ├─────────────────────────────────────────────────┤
    │  ┌─────────┐  ┌─────────┐  ┌─────────┐         │
    │  │ Budget  │  │ Animals │  │ Visitors│         │
    │  │ $X,XXX  │  │   XX    │  │   XX    │         │
    │  └─────────┘  └─────────┘  └─────────┘         │
    ├─────────────────────────────────────────────────┤
    │  ALERTS                                         │
    │  • 🔴 X animals hungry                          │
    │  • 🏥 X animals sick                            │
    │  • 🧹 X enclosures need cleaning                │
    ├─────────────────────────────────────────────────┤
    │  QUICK ACTIONS                                  │
    │  [Advance Day]  [Feed All]  [Clean All]        │
    ├─────────────────────────────────────────────────┤
    │  RESOURCE SUMMARY                               │
    │  Food: eucalyptus(XX) grass(XX) meat(XX)...    │
    │  Medicine: general(X) mammal(X) ...             │
    └─────────────────────────────────────────────────┘
    """
    
    def __init__(self, parent: tk.Frame, app: OzZooApp):
        super().__init__(parent, bg=app.COLOURS["background"])
        self._app = app
        self._zoo = app.zoo
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Build the dashboard UI."""
        if not self._zoo:
            self._show_no_zoo_message()
            return
        
        # Scrollable canvas for content
        canvas = tk.Canvas(self, bg=self._app.COLOURS["background"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self._scrollable_frame = tk.Frame(canvas, bg=self._app.COLOURS["background"])

        self._scrollable_window_id = canvas.create_window(
            (0, 0),
            window=self._scrollable_frame,
            anchor="n",
        )
        canvas.configure(yscrollcommand=scrollbar.set)

        def _update_scrollregion(_event: tk.Event) -> None:
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _center_content(event: tk.Event) -> None:
            content_width = max(0, min(1024, event.width - 20))
            canvas.itemconfigure(self._scrollable_window_id, width=content_width)
            canvas.coords(self._scrollable_window_id, event.width / 2, 0)

        def _on_mousewheel(event: tk.Event) -> str:
            """Scroll canvas with mouse wheel on Windows/macOS."""
            if event.delta == 0:
                return "break"
            step = -1 if event.delta > 0 else 1
            canvas.yview_scroll(step, "units")
            return "break"

        def _on_mousewheel_linux(event: tk.Event) -> str:
            """Scroll canvas with mouse wheel on Linux/X11."""
            if getattr(event, "num", None) == 4:
                canvas.yview_scroll(-1, "units")
            elif getattr(event, "num", None) == 5:
                canvas.yview_scroll(1, "units")
            return "break"

        def _bind_mousewheel(_event: tk.Event) -> None:
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            canvas.bind_all("<Button-4>", _on_mousewheel_linux)
            canvas.bind_all("<Button-5>", _on_mousewheel_linux)

        def _unbind_mousewheel(_event: tk.Event | None = None) -> None:
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")

        def _cleanup_mousewheel_bindings(event: tk.Event) -> None:
            if event.widget is self:
                _unbind_mousewheel()

        self._scrollable_frame.bind("<Configure>", _update_scrollregion)
        canvas.bind("<Configure>", _center_content)
        canvas.bind("<Enter>", _bind_mousewheel)
        canvas.bind("<Leave>", _unbind_mousewheel)
        self._scrollable_frame.bind("<Enter>", _bind_mousewheel)
        self._scrollable_frame.bind("<Leave>", _unbind_mousewheel)
        self.bind("<Destroy>", _cleanup_mousewheel_bindings)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Build sections
        self._create_header_section()
        self._create_mission_section()
        self._create_stats_cards()
        self._create_alerts_section()
        self._create_quick_actions()
        self._create_resource_section()
    
    def _create_mission_section(self) -> None:
        """Create mission display section."""
        from ..widgets.mission_widget import MissionWidget
        self._mission_widget = MissionWidget(self._scrollable_frame, self._app)
        self._mission_widget.pack(fill="x", pady=(0, 20))
    
    def _show_no_zoo_message(self) -> None:
        """Show message when no zoo is loaded."""
        label = tk.Label(
            self,
            text="No zoo loaded. Please start a new game or load a save.",
            bg=self._app.COLOURS["background"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 14)
        )
        label.pack(expand=True)
    
    def _create_header_section(self) -> None:
        """Create the header with day number."""
        header = tk.Frame(self._scrollable_frame, bg=self._app.COLOURS["background"])
        header.pack(fill="x", pady=(0, 20))
        
        title = tk.Label(
            header,
            text=f"📊 Daily Report - Day {self._zoo.day}",
            bg=self._app.COLOURS["background"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 24, "bold")
        )
        title.pack(anchor="w")
        
        subtitle = tk.Label(
            header,
            text=f"Welcome to {self._zoo.name}!",
            bg=self._app.COLOURS["background"],
            fg=self._app.COLOURS["secondary"],
            font=("Segoe UI", 12)
        )
        subtitle.pack(anchor="w")
    
    def _create_stats_cards(self) -> None:
        """Create stat cards showing key metrics."""
        cards_frame = tk.Frame(self._scrollable_frame, bg=self._app.COLOURS["background"])
        cards_frame.pack(fill="x", pady=10)
        
        # Get report data
        report = self._zoo.get_daily_report()
        
        # Define cards
        cards_data = [
            ("💰 Budget", f"${report['budget']:,.2f}", self._app.COLOURS["success"]),
            ("🦘 Animals", f"{report['animal_count']}", self._app.COLOURS["primary"]),
            ("🧬 Diversity", f"{report['species_diversity']} spp", self._app.COLOURS["secondary"]),
            ("👥 Visitors", f"{report['visitor_count']}", self._app.COLOURS["accent"]),
            ("🏥 Sick", f"{report['sick_animals']}", self._app.COLOURS["danger"]),
            ("🏕️ Enclosures", f"{report['enclosure_count']}", self._app.COLOURS["secondary"]),
            ("⭐ Welfare", f"{report['avg_welfare']:.0f}%", self._get_welfare_color(report['avg_welfare'])),
            ("🌟 Reputation", f"{self._zoo.reputation:.0f}/100", self._get_reputation_color(self._zoo.reputation)),
        ]
        
        for i, (title, value, colour) in enumerate(cards_data):
            card = self._create_stat_card(cards_frame, title, value, colour)
            card.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")
            cards_frame.columnconfigure(i, weight=1)
    
    def _create_stat_card(self, parent: tk.Frame, title: str, value: str, colour: str) -> tk.Frame:
        """Create a single stat card."""
        card = tk.Frame(
            parent,
            bg=self._app.COLOURS["card_bg"],
            relief="raised",
            borderwidth=1
        )
        
        # Colour strip at top
        strip = tk.Frame(card, bg=colour, height=5)
        strip.pack(fill="x")
        
        # Title
        title_label = tk.Label(
            card,
            text=title,
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 10)
        )
        title_label.pack(pady=(10, 0))
        
        # Value
        value_label = tk.Label(
            card,
            text=value,
            bg=self._app.COLOURS["card_bg"],
            fg=colour,
            font=("Segoe UI", 20, "bold")
        )
        value_label.pack(pady=(0, 10))
        
        return card
    
    def _create_alerts_section(self) -> None:
        """Create the alerts/warnings section."""
        section = tk.LabelFrame(
            self._scrollable_frame,
            text="⚠️ Alerts",
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 12, "bold"),
            padx=15,
            pady=10
        )
        section.pack(fill="x", pady=10)
        
        alerts = self._zoo.get_alerts()
        
        if not alerts:
            no_alerts = tk.Label(
                section,
                text="✅ All systems running smoothly!",
                bg=self._app.COLOURS["card_bg"],
                fg=self._app.COLOURS["success"],
                font=("Segoe UI", 11)
            )
            no_alerts.pack(anchor="w")
        else:
            for alert in alerts:
                alert_label = tk.Label(
                    section,
                    text=f"• {alert}",
                    bg=self._app.COLOURS["card_bg"],
                    fg=self._app.COLOURS["text"],
                    font=("Segoe UI", 11)
                )
                alert_label.pack(anchor="w", pady=2)
    
    def _create_quick_actions(self) -> None:
        """Create quick action buttons."""
        section = tk.LabelFrame(
            self._scrollable_frame,
            text="🎮 Quick Actions",
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 12, "bold"),
            padx=15,
            pady=10
        )
        section.pack(fill="x", pady=10)
        
        buttons_frame = tk.Frame(section, bg=self._app.COLOURS["card_bg"])
        buttons_frame.pack(fill="x")
        
        # Advance Day button
        advance_btn = tk.Button(
            buttons_frame,
            text="⏭️ Advance Day",
            command=self._on_advance_day,
            bg=self._app.COLOURS["primary"],
            fg=self._app.COLOURS["text_light"],
            font=("Segoe UI", 11, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=10
        )
        advance_btn.pack(side="left", padx=5, pady=5)
        
        # Feed All button
        feed_btn = tk.Button(
            buttons_frame,
            text="🍖 Feed Hungry",
            command=self._on_feed_all,
            bg=self._app.COLOURS["accent"],
            fg=self._app.COLOURS["text_light"],
            font=("Segoe UI", 11),
            relief=tk.FLAT,
            padx=20,
            pady=10
        )
        feed_btn.pack(side="left", padx=5, pady=5)
        
        # Clean All button
        clean_btn = tk.Button(
            buttons_frame,
            text="🧹 Clean Dirty",
            command=self._on_clean_all,
            bg=self._app.COLOURS["secondary"],
            fg=self._app.COLOURS["text_light"],
            font=("Segoe UI", 11),
            relief=tk.FLAT,
            padx=20,
            pady=10
        )
        clean_btn.pack(side="left", padx=5, pady=5)
        
        # Save Game button
        save_btn = tk.Button(
            buttons_frame,
            text="💾 Save Game",
            command=self._on_save_game,
            bg=self._app.COLOURS["success"],
            fg=self._app.COLOURS["text_light"],
            font=("Segoe UI", 11),
            relief=tk.FLAT,
            padx=20,
            pady=10
        )
        save_btn.pack(side="left", padx=5, pady=5)
    
    def _create_resource_section(self) -> None:
        """Create the resource summary section."""
        section = tk.LabelFrame(
            self._scrollable_frame,
            text="📦 Resources",
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 12, "bold"),
            padx=15,
            pady=10
        )
        section.pack(fill="x", pady=10)
        
        report = self._zoo.get_daily_report()
        
        # Food stock
        food_frame = tk.Frame(section, bg=self._app.COLOURS["card_bg"])
        food_frame.pack(fill="x", pady=5)
        
        food_label = tk.Label(
            food_frame,
            text="🍽️ Food Stock:",
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 11, "bold")
        )
        food_label.pack(side="left")
        
        food_items = [f"{k}({v})" for k, v in report["food_stock"].items()]
        food_values = tk.Label(
            food_frame,
            text="  " + "  |  ".join(food_items),
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 10)
        )
        food_values.pack(side="left")
        
        # Medicine stock
        med_frame = tk.Frame(section, bg=self._app.COLOURS["card_bg"])
        med_frame.pack(fill="x", pady=5)
        
        med_label = tk.Label(
            med_frame,
            text="💊 Medicine:",
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 11, "bold")
        )
        med_label.pack(side="left")
        
        med_items = [f"{k}({v})" for k, v in report["medicine_stock"].items()]
        med_values = tk.Label(
            med_frame,
            text="  " + "  |  ".join(med_items),
            bg=self._app.COLOURS["card_bg"],
            fg=self._app.COLOURS["text"],
            font=("Segoe UI", 10)
        )
        med_values.pack(side="left")
    
    # Event handlers
    def _on_advance_day(self) -> None:
        """Advance to the next day and show report."""
        if self._app.ask_yes_no("Advance Day", "Are you sure you want to advance to the next day?"):
            report = self._zoo.advance_day()
            self._app.update_header_info()
            self._show_day_report(report)
            self._app.refresh_current_frame()
    
    def _show_day_report(self, report: dict) -> None:
        """Show the day end report dialogue."""
        self._handle_newborn_naming(report)

        # Build report message
        msg = f"Day {report['day']} Summary\n"
        msg += "=" * 30 + "\n\n"
        msg += f"👥 Visitors: {report['visitors']}\n"
        msg += f"💰 Revenue: ${report['revenue']:.2f}\n"
        msg += f"💸 Expenses: ${report['expenses']:.2f}\n"
        msg += f"🎁 Donations: ${report['donations']:.2f}\n\n"
        
        if report["deaths"]:
            msg += f"💀 Deaths: {', '.join(report['deaths'])}\n"
        if report["births"]:
            msg += f"🎉 Births: {', '.join(report['births'])}\n"
        if report["events"]:
            msg += f"\n📰 Events:\n" + "\n".join(f"  • {e}" for e in report["events"])
        
        # Add visitor reviews
        if "reviews" in report and report["reviews"]:
            msg += "\n\n📝 Visitor Reviews:\n"
            msg += "-" * 30 + "\n"
            for review in report["reviews"]:
                msg += f"\n{review.get_star_display()}\n"
                msg += f"{review.visitor_name}: \"{review.comment}\"\n"
        
        self._app.show_info("Day Complete", msg)

    def _handle_newborn_naming(self, report: dict) -> None:
        """Offer naming prompts for newborn animals in the current report."""
        births = report.get("births", [])
        if not births:
            return

        report_events = report.setdefault("events", [])
        for index, birth_name in enumerate(list(births)):
            animal = self._zoo.animals.get(birth_name)
            if not animal:
                continue

            species = animal.species
            wants_custom_name = self._app.ask_yes_no(
                "Newborn Naming",
                (
                    f"A new {species} was born: {birth_name}\n\n"
                    "Would you like to choose a custom name?"
                ),
            )

            if wants_custom_name:
                entered_name = simpledialog.askstring(
                    "Name Newborn",
                    (
                        f"Enter a name for the new {species}.\n"
                        "Leave blank to auto-generate a random name."
                    ),
                    parent=self,
                )
                chosen_name = (entered_name or "").strip()
                if not chosen_name:
                    chosen_name = self._zoo.generate_random_baby_name(species)
            else:
                chosen_name = self._zoo.generate_random_baby_name(species)

            final_name = birth_name
            if chosen_name and chosen_name != birth_name:
                renamed, rename_msg = self._zoo.rename_animal(birth_name, chosen_name)
                if renamed:
                    final_name = chosen_name
                else:
                    fallback_name = self._zoo.generate_random_baby_name(species)
                    fallback_ok, _ = self._zoo.rename_animal(birth_name, fallback_name)
                    if fallback_ok:
                        final_name = fallback_name
                    else:
                        self._app.show_warning("Newborn Naming", rename_msg)

            if final_name != birth_name:
                report["births"][index] = final_name
                report["events"] = [
                    event.replace(birth_name, final_name) for event in report_events
                ]
                report_events = report["events"]
                report_events.append(f"📝 You named {birth_name} the {species} as {final_name}.")
    
    def _on_feed_all(self) -> None:
        """Feed all hungry animals."""
        hungry = [a for a in self._zoo.animals.values() if a.is_alive and a.is_hungry]
        if not hungry:
            self._app.show_info("Feed Animals", "No animals are hungry!")
            return
        
        fed_count = 0
        for animal in hungry:
            diet = animal.get_diet()
            success, msg = self._zoo.feed_animal(animal.name, diet)
            if success:
                fed_count += 1
        
        self._app.show_info("Feed Animals", f"Fed {fed_count} of {len(hungry)} hungry animals.")
        self._app.refresh_current_frame()
    
    def _on_clean_all(self) -> None:
        """Clean all dirty enclosures."""
        dirty = [e for e in self._zoo.enclosures.values() if e.is_dirty]
        if not dirty:
            self._app.show_info("Clean Enclosures", "No enclosures need cleaning!")
            return
        
        for enclosure in dirty:
            enclosure.clean()
        
        self._app.show_info("Clean Enclosures", f"Cleaned {len(dirty)} enclosures.")
        self._app.refresh_current_frame()
    
    def _get_welfare_color(self, welfare: float) -> str:
        """Get color based on welfare score."""
        if welfare >= 70:
            return self._app.COLOURS["success"]
        elif welfare >= 50:
            return self._app.COLOURS["accent"]
        else:
            return self._app.COLOURS["danger"]
    
    def _get_reputation_color(self, reputation: float) -> str:
        """Get color based on reputation score."""
        if reputation >= 70:
            return self._app.COLOURS["success"]
        elif reputation >= 50:
            return self._app.COLOURS["accent"]
        else:
            return self._app.COLOURS["danger"]
    
    def _on_save_game(self) -> None:
        """Save the current game."""
        from tkinter import filedialog
        from pathlib import Path
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
                self._app.set_status(f"Game saved to {Path(filepath).name}")
            except Exception as e:
                self._app.show_error("Save Error", f"Failed to save game: {e}")
