"""
Map tile model for the zoo grid system.

Represents individual tiles in the 10x10 zoo map grid.
"""

from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .enclosure import Enclosure


class TileType(Enum):
    """Types of tiles that can be placed on the zoo map."""
    
    EMPTY = "empty"           # Empty grass/path
    ENCLOSURE = "enclosure"   # Animal enclosure
    SCENERY = "scenery"       # Decorative items (trees, rocks, water)
    SHOP = "shop"            # Visitor facilities (food, restrooms)


class MapTile:
    """
    Represents a single tile in the zoo map grid.
    
    Attributes:
        x: X coordinate (0-9)
        y: Y coordinate (0-9)
        tile_type: Type of tile (TileType enum)
        item_id: ID of the item placed (e.g., "tree", "food-stall", enclosure name)
        enclosure_ref: Reference to Enclosure object if tile_type is ENCLOSURE
    """
    
    def __init__(
        self,
        x: int,
        y: int,
        tile_type: TileType = TileType.EMPTY,
        item_id: Optional[str] = None,
        enclosure_ref: Optional[Enclosure] = None
    ) -> None:
        """
        Initialize a map tile.
        
        Args:
            x: X coordinate (0-9)
            y: Y coordinate (0-9)
            tile_type: Type of tile
            item_id: ID of placed item
            enclosure_ref: Reference to enclosure if applicable
        """
        self._x = x
        self._y = y
        self._tile_type = tile_type
        self._item_id = item_id
        self._enclosure_ref = enclosure_ref
    
    @property
    def x(self) -> int:
        """Get X coordinate."""
        return self._x
    
    @property
    def y(self) -> int:
        """Get Y coordinate."""
        return self._y
    
    @property
    def tile_type(self) -> TileType:
        """Get tile type."""
        return self._tile_type
    
    @tile_type.setter
    def tile_type(self, value: TileType) -> None:
        """Set tile type."""
        self._tile_type = value
    
    @property
    def item_id(self) -> Optional[str]:
        """Get item ID."""
        return self._item_id
    
    @item_id.setter
    def item_id(self, value: Optional[str]) -> None:
        """Set item ID."""
        self._item_id = value
    
    @property
    def enclosure_ref(self) -> Optional[Enclosure]:
        """Get enclosure reference."""
        return self._enclosure_ref
    
    @enclosure_ref.setter
    def enclosure_ref(self, value: Optional[Enclosure]) -> None:
        """Set enclosure reference."""
        self._enclosure_ref = value
    
    @property
    def is_empty(self) -> bool:
        """Check if tile is empty."""
        return self._tile_type == TileType.EMPTY
    
    def clear(self) -> None:
        """Clear the tile back to empty."""
        self._tile_type = TileType.EMPTY
        self._item_id = None
        self._enclosure_ref = None
    
    def to_dict(self) -> dict:
        """
        Serialize to dictionary for JSON save.
        
        Returns:
            Dictionary containing tile data.
        """
        return {
            "x": self._x,
            "y": self._y,
            "tile_type": self._tile_type.value,
            "item_id": self._item_id,
            # Don't serialize enclosure_ref - will be relinked on load
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> MapTile:
        """
        Deserialize from dictionary.
        
        Args:
            data: Dictionary containing tile data.
            
        Returns:
            New MapTile instance.
        """
        return cls(
            x=data["x"],
            y=data["y"],
            tile_type=TileType(data["tile_type"]),
            item_id=data.get("item_id")
        )
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        if self.is_empty:
            return f"Tile({self._x},{self._y}): Empty"
        return f"Tile({self._x},{self._y}): {self._tile_type.value} - {self._item_id}"
    
    def __repr__(self) -> str:
        """Developer-friendly string representation."""
        return (
            f"MapTile(x={self._x}, y={self._y}, "
            f"tile_type={self._tile_type}, item_id={self._item_id!r})"
        )


# Placement costs for different items
PLACEMENT_COSTS = {
    # Enclosures (multi-tile, linked to Enclosure objects)
    "enclosure_small": 4000,    # 2x2 enclosure
    "enclosure_large": 7000,    # 3x3 enclosure
    "enclosure_koala": 0,       # Starter enclosure (free)
    "enclosure_outback": 0,     # Starter enclosure (free)
    "enclosure_aviary": 0,      # Starter enclosure (free)
    "enclosure_billabong": 0,   # Starter enclosure (free)
    "enclosure_reptile": 0,     # Starter enclosure (free)
    
    # Scenery (single tile decorations)
    "tree": 100,
    "rock": 200,
    "water": 500,
    "flowers": 150,
    "bush": 80,
    
    # Shops/Facilities (single tile)
    "food-stall": 1500,
    "ticket-booth": 2000,
    "restroom": 1000,
    "visitor-center": 3000,
    "bench": 50,
}


# Item display info (emoji and name for UI)
ITEM_INFO = {
    # Scenery
    "tree": {"emoji": "🌳", "name": "Tree"},
    "rock": {"emoji": "🪨", "name": "Rock Formation"},
    "water": {"emoji": "💧", "name": "Water Feature"},
    "flowers": {"emoji": "🌺", "name": "Flower Bed"},
    "bush": {"emoji": "🌿", "name": "Bush"},
    
    # Shops/Facilities
    "food-stall": {"emoji": "🍔", "name": "Food Stall"},
    "ticket-booth": {"emoji": "🎟️", "name": "Ticket Booth"},
    "restroom": {"emoji": "🚻", "name": "Restroom"},
    "visitor-center": {"emoji": "ℹ️", "name": "Visitor Center"},
    "bench": {"emoji": "🪑", "name": "Bench"},
    
    # Enclosures (starter enclosures)
    "enclosure_koala": {"emoji": "🐨", "name": "Koala Corner"},
    "enclosure_outback": {"emoji": "🦘", "name": "Outback Plains"},
    "enclosure_aviary": {"emoji": "🦅", "name": "Bird Paradise"},
    "enclosure_billabong": {"emoji": "🐊", "name": "Crocodile Creek"},
    "enclosure_reptile": {"emoji": "🦎", "name": "Reptile Realm"},
}
