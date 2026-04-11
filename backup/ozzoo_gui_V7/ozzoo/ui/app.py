"""
OzZoo Main GUI Application
The main Tkinter application window and navigation controller.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
from typing import TYPE_CHECKING, Dict, Type, Optional, Callable
from pathlib import Path

if TYPE_CHECKING:
    from ..models.zoo import Zoo


class OzZooApp(tk.Tk):
    """
    Main application window for OzZoo.
    
    Manages frame navigation and provides access to the Zoo instance.
    """
    
    # Theme colours (Australian outback theme)
    COLOURS = {
        "primary": "#2E7D32",      # Forest green
        "secondary": "#8D6E63",    # Brown
        "background": "#FFF8E1",   # Cream
        "accent": "#FF8F00",       # Orange
        "danger": "#D32F2F",       # Red
        "success": "#388E3C",      # Green
        "text": "#3E2723",         # Dark brown
        "text_light": "#FFFFFF",   # White
        "card_bg": "#FFFFFF",      # White
        "border": "#BCAAA4"        # Light brown
    }
    
    def __init__(self, zoo: Optional[Zoo] = None):
        super().__init__()
        
        self._zoo = zoo
        self._frames: Dict[str, tk.Frame] = {}
        self._current_frame: Optional[str] = None
        
        # Configure window
        self.title("🦘 OzZoo - Australian Wildlife Park 🐨")
        self.geometry("1024x1024")
        self.minsize(800, 600)
        self.configure(bg=self.COLOURS["background"])
        
        # Configure styles
        self._setup_styles()
        
        # Create main container
        self._container = tk.Frame(self, bg=self.COLOURS["background"])
        self._container.pack(fill=tk.BOTH, expand=True)
        
        # Create header
        self._header = self._create_header()
        self._header.pack(fill=tk.X)
        
        # Create main content area
        self._content = tk.Frame(self._container, bg=self.COLOURS["background"])
        self._content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create status bar
        self._status_bar = self._create_status_bar()
        self._status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Navigation callbacks
        self._nav_callbacks: Dict[str, Callable] = {}
    
    def _setup_styles(self) -> None:
        """Configure ttk styles for the application."""
        style = ttk.Style()
        style.theme_use("clam")
        
        # Primary button
        style.configure(
            "Primary.TButton",
            background=self.COLOURS["primary"],
            foreground=self.COLOURS["text_light"],
            padding=(20, 10),
            font=("Segoe UI", 11, "bold")
        )
        style.map("Primary.TButton",
            background=[("active", "#1B5E20"), ("pressed", "#1B5E20")]
        )
        
        # Secondary button
        style.configure(
            "Secondary.TButton",
            background=self.COLOURS["secondary"],
            foreground=self.COLOURS["text_light"],
            padding=(15, 8),
            font=("Segoe UI", 10)
        )
        
        # Danger button
        style.configure(
            "Danger.TButton",
            background=self.COLOURS["danger"],
            foreground=self.COLOURS["text_light"],
            padding=(15, 8),
            font=("Segoe UI", 10)
        )
        
        # Card frame
        style.configure(
            "Card.TFrame",
            background=self.COLOURS["card_bg"],
            relief="raised",
            borderwidth=1
        )
        
        # Labels
        style.configure(
            "Header.TLabel",
            background=self.COLOURS["primary"],
            foreground=self.COLOURS["text_light"],
            font=("Segoe UI", 16, "bold"),
            padding=(10, 5)
        )
        
        style.configure(
            "Title.TLabel",
            background=self.COLOURS["background"],
            foreground=self.COLOURS["text"],
            font=("Segoe UI", 24, "bold")
        )
        
        style.configure(
            "Subtitle.TLabel",
            background=self.COLOURS["background"],
            foreground=self.COLOURS["text"],
            font=("Segoe UI", 14)
        )
    
    def _create_header(self) -> tk.Frame:
        """Create the application header with navigation."""
        header = tk.Frame(self._container, bg=self.COLOURS["primary"], height=60)
        
        # Logo/Title
        title_label = tk.Label(
            header,
            text="🦘 OzZoo 🐨",
            bg=self.COLOURS["primary"],
            fg=self.COLOURS["text_light"],
            font=("Segoe UI", 20, "bold")
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Navigation buttons frame
        self._nav_frame = tk.Frame(header, bg=self.COLOURS["primary"])
        self._nav_frame.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
        
        return header
    
    def _create_status_bar(self) -> tk.Frame:
        """Create the status bar at the bottom."""
        status_bar = tk.Frame(self._container, bg=self.COLOURS["secondary"], height=30)
        
        self._status_label = tk.Label(
            status_bar,
            text="Welcome to OzZoo! 🌿",
            bg=self.COLOURS["secondary"],
            fg=self.COLOURS["text_light"],
            font=("Segoe UI", 10)
        )
        self._status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        return status_bar
    
    # Properties
    @property
    def zoo(self) -> Optional[Zoo]:
        """Get the Zoo instance."""
        return self._zoo
    
    @zoo.setter
    def zoo(self, value: Zoo) -> None:
        """Set the Zoo instance and update the header."""
        self._zoo = value
        self.update_header_info()
    
    @property
    def content_frame(self) -> tk.Frame:
        """Get the main content frame for placing child frames."""
        return self._content
    
    # Frame Management
    def register_frame(self, name: str, frame_class: Type[tk.Frame]) -> None:
        """Register a frame class for navigation."""
        self._nav_callbacks[name] = frame_class
    
    def show_frame(self, name: str, **kwargs) -> None:
        """Show a registered frame by name."""
        # Clear current content
        for widget in self._content.winfo_children():
            widget.destroy()
        
        # Create and show new frame
        if name in self._nav_callbacks:
            frame_class = self._nav_callbacks[name]
            frame = frame_class(self._content, self, **kwargs)
            frame.pack(fill=tk.BOTH, expand=True)
            self._current_frame = name
        else:
            messagebox.showerror("Error", f"Unknown frame: {name}")
    
    def add_nav_button(self, text: str, frame_name: str, icon: str = "") -> None:
        """Add a navigation button to the header."""
        btn_text = f"{icon} {text}" if icon else text
        btn = tk.Button(
            self._nav_frame,
            text=btn_text,
            bg=self.COLOURS["primary"],
            fg=self.COLOURS["text_light"],
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            activebackground="#1B5E20",
            activeforeground=self.COLOURS["text_light"],
            command=lambda: self.show_frame(frame_name)
        )
        btn.pack(side=tk.LEFT, padx=5, pady=5)
    
    # UI Updates
    def update_header_info(self) -> None:
        """Header info moved to frame-local UI; kept for compatibility."""
        return
    
    def set_status(self, message: str) -> None:
        """Update the status bar message."""
        self._status_label.config(text=message)
    
    def show_info(self, title: str, message: str) -> None:
        """Show an info dialog."""
        messagebox.showinfo(title, message)
    
    def show_warning(self, title: str, message: str) -> None:
        """Show a warning dialog."""
        messagebox.showwarning(title, message)
    
    def show_error(self, title: str, message: str) -> None:
        """Show an error dialog."""
        messagebox.showerror(title, message)
    
    def ask_yes_no(self, title: str, message: str) -> bool:
        """Show a yes/no dialog and return the result."""
        return messagebox.askyesno(title, message)
    
    def refresh_current_frame(self) -> None:
        """Refresh the current frame (useful after game state changes)."""
        if self._current_frame:
            self.show_frame(self._current_frame)


def create_app(zoo: Optional[Zoo] = None) -> OzZooApp:
    """Factory function to create the application."""
    return OzZooApp(zoo)
