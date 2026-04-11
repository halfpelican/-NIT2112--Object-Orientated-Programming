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
        enclosure_ref: Optional[Enclosure] = None,
        enclosure_id: Optional[str] = None,
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
        self._enclosure_id = enclosure_ref.enclosure_id if enclosure_ref else enclosure_id
    
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
        self._enclosure_id = value.enclosure_id if value else None

    @property
    def enclosure_id(self) -> Optional[str]:
        """Get enclosure ID stored on this tile."""
        return self._enclosure_id

    @enclosure_id.setter
    def enclosure_id(self, value: Optional[str]) -> None:
        """Set enclosure ID stored on this tile."""
        self._enclosure_id = value
    
    @property
    def is_empty(self) -> bool:
        """Check if tile is empty."""
        return self._tile_type == TileType.EMPTY
    
    def clear(self) -> None:
        """Clear the tile back to empty."""
        self._tile_type = TileType.EMPTY
        self._item_id = None
        self._enclosure_ref = None
        self._enclosure_id = None
    
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
            "enclosure_id": self._enclosure_id,
            # Don't serialize enclosure_ref object - it is relinked on load
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
            item_id=data.get("item_id"),
            enclosure_id=data.get("enclosure_id"),
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
            f"tile_type={self._tile_type}, item_id={self._item_id!r}, "
            f"enclosure_id={self._enclosure_id!r})"
        )


# Placement costs for different items
PLACEMENT_COSTS = {
    # Enclosures (2x2 multi-tile) - Purchasable from map
    "eucalyptus_grove": 5000,
    "outback_savanna": 6000,
    "billabong": 7000,
    "rainforest_aviary": 5500,
    "reptile_house": 6500,
    
    # Starter enclosures (free, pre-generated emoji versions)
    "enclosure_koala": 0,
    "enclosure_outback": 0,
    "enclosure_aviary": 0,
    "enclosure_billabong": 0,
    "enclosure_reptile": 0,
    
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
    # Enclosures (can be placed after purchase)
    "eucalyptus_grove": {"emoji": "🐨", "name": "Eucalyptus Grove", "size": (2, 2)},
    "outback_savanna": {"emoji": "🦘", "name": "Outback Savanna", "size": (2, 2)},
    "billabong": {"emoji": "🐊", "name": "Billabong Wetland", "size": (2, 2)},
    "rainforest_aviary": {"emoji": "🦅", "name": "Rainforest Aviary", "size": (2, 2)},
    "reptile_house": {"emoji": "🦎", "name": "Reptile House", "size": (2, 2)},
    
    # Scenery
    "tree": {"emoji": "🌳", "name": "Tree", "size": (1, 1)},
    "rock": {"emoji": "🪨", "name": "Rock Formation", "size": (1, 1)},
    "water": {"emoji": "💧", "name": "Water Feature", "size": (1, 1)},
    "flowers": {"emoji": "🌺", "name": "Flower Bed", "size": (1, 1)},
    "bush": {"emoji": "🌿", "name": "Bush", "size": (1, 1)},
    
    # Shops/Facilities
    "food-stall": {"emoji": "🍔", "name": "Food Stall", "size": (1, 1)},
    "ticket-booth": {"emoji": "🎟️", "name": "Ticket Booth", "size": (1, 1)},
    "restroom": {"emoji": "🚻", "name": "Restroom", "size": (1, 1)},
    "visitor-center": {"emoji": "ℹ️", "name": "Visitor Center", "size": (1, 1)},
    "bench": {"emoji": "🪑", "name": "Bench", "size": (1, 1)},
    
    # Starter enclosures (already placed)
    "enclosure_koala": {"emoji": "🐨", "name": "Koala Corner", "size": (2, 2)},
    "enclosure_outback": {"emoji": "🦘", "name": "Outback Plains", "size": (2, 2)},
    "enclosure_aviary": {"emoji": "🦅", "name": "Bird Paradise", "size": (2, 2)},
    "enclosure_billabong": {"emoji": "🐊", "name": "Crocodile Creek", "size": (2, 2)},
    "enclosure_reptile": {"emoji": "🦎", "name": "Reptile Realm", "size": (2, 2)},
}
