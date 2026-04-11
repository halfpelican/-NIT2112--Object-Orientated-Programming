"""
OzZoo Main Zoo Module
Contains the Zoo class - the main game controller.
"""

from __future__ import annotations
import random
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Any
from datetime import datetime
import json

from .animal import Animal
from .enclosure import Enclosure, create_enclosure, ENCLOSURE_TYPES
from .resources import Food, Medicine, FOOD_TYPES, MEDICINE_TYPES
from .visitor import Visitor, generate_random_visitor, TicketType
from .staff import ZooKeeper, generate_random_keeper, Specialty
from .map_tile import MapTile, TileType, PLACEMENT_COSTS, ITEM_INFO
from .mission import (
    Mission,
    MissionType,
    generate_starter_mission,
    generate_random_mission,
    get_mission_animal_habitat,
)
from .review import Review, generate_reviews, calculate_reputation_from_reviews
from ..patterns.factory import AnimalFactory
from ..patterns.observer import EventManager, EventTypes
from ..exceptions import (
    InsufficientFundsError, InsufficientFoodError, 
    HabitatCapacityExceededError, InvalidHabitatError
)


class Zoo:
    """
    Main Zoo class - the game controller.
    
    Manages all zoo operations including animals, enclosures, visitors,
    staff, resources, and the day cycle.
    """
    
    DEFAULT_BUDGET = 10000.0
    TICKET_PRICE_MODIFIER = 1.0  # Can be adjusted
    GRID_SIZE = 10  # 10x10 map grid
    DAILY_SICKNESS_CHANCE = 0.07  # 7% daily chance per healthy animal
    BREEDING_MIN_HEALTH = 70
    BREEDING_MIN_HAPPINESS = 70
    BREEDING_COOLDOWN_DAYS = 3
    BARRIER_UPGRADE_COST = 1200.0
    EMERGENCY_RELOCATION_COST = 300.0
    PREDATION_LOW_RISK_THRESHOLD = 25
    PREDATION_HIGH_RISK_THRESHOLD = 75
    PREDATION_SHARED_RISK_GAIN = 28
    PREDATION_ADJACENT_RISK_GAIN = 16
    PREDATION_RISK_DECAY = 22
    PREDATION_SHARED_MISHAP_CHANCE = 0.35
    PREDATION_ADJACENT_MISHAP_CHANCE = 0.20
    PREDATION_FATAL_CHANCE = 0.30
    DEVIL_OUTBACK_RISK_GAIN = 20
    DEVIL_OUTBACK_MISHAP_CHANCE = 0.28
    DEVIL_OUTBACK_FATAL_CHANCE = 0.18
    RANDOM_BABY_NAMES: Dict[str, List[str]] = {
        "Koala": ["Blinky", "Milo", "Gumdrop", "Wattle", "Poppy"],
        "Kangaroo": ["Joey", "Skippy", "Roo", "Boomer", "Pouch"],
        "Wombat": ["Wally", "Nugget", "Pebble", "Burrow", "Mochi"],
        "Platypus": ["Paddle", "Perry", "Ripple", "Bubbles", "Nori"],
        "TasmanianDevil": ["Taz", "Fang", "Rascal", "Mischief", "Pepper"],
        "Echidna": ["Spike", "Prickle", "Quill", "Needle", "Scout"],
        "Kookaburra": ["Kookie", "Chuckles", "Cackle", "Sunny", "Echo"],
        "Emu": ["Dash", "Drum", "Flurry", "Sprout", "Dusty"],
        "WedgeTailedEagle": ["Aquila", "Sky", "Arrow", "Storm", "Soar"],
        "SaltwaterCroc": ["Snap", "Bitey", "Delta", "Murray", "Chomp"],
        "FrilledLizard": ["Frilly", "Ruffle", "Flash", "Scales", "Zippy"],
    }
    GENERIC_BABY_NAMES: List[str] = [
        "Pip", "Luna", "Sunny", "Rusty", "Willow", "Coco", "Indy", "Blue"
    ]
    
    def __init__(self, name: str = "OzZoo", budget: float = DEFAULT_BUDGET):
        self._name = name
        self._budget = budget
        self._day = 1
        
        # Core collections
        self._enclosures: Dict[str, Enclosure] = {}
        self._animals: Dict[str, Animal] = {}  # animal_name -> Animal
        self._visitors: List[Visitor] = []
        self._keepers: Dict[str, ZooKeeper] = {}
        
        # Map grid (10x10)
        self._map_grid: List[List[MapTile]] = self._init_grid()
        
        # Resources
        self._food_stock: Dict[str, int] = {
            "eucalyptus": 50,
            "grass": 80,
            "meat": 30,
            "fish": 20,
            "insects": 40
        }
        self._medicine_stock: Dict[str, int] = {
            "general": 5,
            "mammal_specialist": 3,
            "avian": 3,
            "reptile": 3
        }
        
        # Stats
        self._total_revenue = 0.0
        self._total_expenses = 0.0
        self._animals_died = 0
        self._animals_born = 0
        
        # Event system
        self._event_manager = EventManager()
        self._daily_events: List[str] = []
        
        # Ticket price modifier
        self._ticket_modifier = 1.0
        
        # Mission system
        self._active_missions: List[Mission] = []
        self._mission_keeper: Optional[ZooKeeper] = None
        self._consecutive_happy_days: Dict[str, int] = {}  # animal_name -> days happy
        self._total_visitors_served = 0
        
        # Review and reputation system
        self._reviews: List[Review] = []
        self._reputation = 50.0  # 0-100 scale, starts neutral
        self._species_last_bred_day: Dict[str, int] = {}

        # Feeding Frenzy mini-game state (shared attempts across all animals per day)
        self._feeding_frenzy_pool_day = self._day
        self._feeding_frenzy_attempts_total = 0
        self._feeding_frenzy_attempts_remaining = 0
        self._predation_risk_by_platypus: Dict[str, int] = {}
        self._outback_predation_risk_by_prey: Dict[str, int] = {}
    
    def _init_grid(self) -> List[List[MapTile]]:
        """Initialize empty 10x10 grid."""
        return [
            [MapTile(x, y) for y in range(self.GRID_SIZE)]
            for x in range(self.GRID_SIZE)
        ]
    
    # Properties
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def budget(self) -> float:
        return self._budget
    
    @property
    def day(self) -> int:
        return self._day
    
    @property
    def enclosures(self) -> Dict[str, Enclosure]:
        return self._enclosures.copy()
    
    @property
    def animals(self) -> Dict[str, Animal]:
        return self._animals.copy()
    
    @property
    def visitors(self) -> List[Visitor]:
        return self._visitors.copy()
    
    @property
    def keepers(self) -> Dict[str, ZooKeeper]:
        return self._keepers.copy()
    
    @property
    def food_stock(self) -> Dict[str, int]:
        return self._food_stock.copy()
    
    @property
    def medicine_stock(self) -> Dict[str, int]:
        return self._medicine_stock.copy()
    
    @property
    def event_manager(self) -> EventManager:
        return self._event_manager
    
    @property
    def daily_events(self) -> List[str]:
        return self._daily_events.copy()
    
    @property
    def animal_count(self) -> int:
        return len([a for a in self._animals.values() if a.is_alive])
    
    @property
    def sick_animal_count(self) -> int:
        return len([a for a in self._animals.values() if a.is_alive and a.is_sick])
    
    @property
    def hungry_animal_count(self) -> int:
        return len([a for a in self._animals.values() if a.is_alive and a.is_hungry])
    
    @property
    def average_visitor_satisfaction(self) -> float:
        if not self._visitors:
            return 0.0
        return sum(v.satisfaction for v in self._visitors) / len(self._visitors)
    
    @property
    def average_animal_welfare(self) -> float:
        alive = [a for a in self._animals.values() if a.is_alive]
        if not alive:
            return 0.0
        return sum((a.health + a.happiness) / 2 for a in alive) / len(alive)

    @property
    def species_diversity(self) -> int:
        """Number of unique living animal species in the zoo."""
        return len({a.species for a in self._animals.values() if a.is_alive})
    
    @property
    def map_grid(self) -> List[List[MapTile]]:
        """Get the zoo map grid."""
        return self._map_grid
    
    @property
    def current_mission(self) -> Optional[Mission]:
        """Get the first active mission (legacy compatibility)."""
        if not self._active_missions:
            return None
        return self._active_missions[0]

    @property
    def active_missions(self) -> List[Mission]:
        """Get all active missions."""
        return self._active_missions.copy()
    
    @property
    def mission_keeper(self) -> Optional[ZooKeeper]:
        """Get the keeper who assigned the mission."""
        return self._mission_keeper
    
    @property
    def reputation(self) -> float:
        """Zoo reputation (0-100) based on visitor reviews."""
        return self._reputation
    
    @property
    def reviews(self) -> List[Review]:
        """List of all visitor reviews."""
        return self._reviews.copy()

    @property
    def feeding_frenzy_attempts_total(self) -> int:
        """Total Feeding Frenzy toss attempts available for the current day."""
        return self._feeding_frenzy_attempts_total

    @property
    def feeding_frenzy_attempts_remaining(self) -> int:
        """Remaining Feeding Frenzy toss attempts for the current day."""
        return self._feeding_frenzy_attempts_remaining
    
    # ============ MAP MANAGEMENT ============
    
    def get_tile(self, x: int, y: int) -> Optional[MapTile]:
        """
        Get tile at coordinates.
        
        Args:
            x: X coordinate (0-9)
            y: Y coordinate (0-9)
            
        Returns:
            MapTile if coordinates valid, None otherwise.
        """
        if 0 <= x < self.GRID_SIZE and 0 <= y < self.GRID_SIZE:
            return self._map_grid[x][y]
        return None
    
    def place_item(
        self, 
        x: int, 
        y: int, 
        item_id: str, 
        tile_type: TileType,
        enclosure_ref: Optional[Enclosure] = None
    ) -> tuple[bool, str]:
        """
        Place an item on the map grid.
        
        Args:
            x: X coordinate
            y: Y coordinate
            item_id: ID of item to place
            tile_type: Type of tile
            enclosure_ref: Enclosure reference if placing enclosure
            
        Returns:
            Tuple of (success, message)
        """
        tile = self.get_tile(x, y)
        if not tile:
            return False, "Invalid coordinates"
        
        if not tile.is_empty:
            return False, "Tile is already occupied"
        
        # Check cost
        cost = PLACEMENT_COSTS.get(item_id, 0)
        if cost > self._budget:
            return False, f"Insufficient funds! Need ${cost:,.2f}"
        
        # Place item
        tile.tile_type = tile_type
        tile.item_id = item_id
        tile.enclosure_ref = enclosure_ref
        
        # Deduct cost
        self._budget -= cost
        self._total_expenses += cost
        
        item_name = ITEM_INFO.get(item_id, {}).get("name", item_id)
        return True, f"Placed {item_name} for ${cost:,.2f}"
    
    def remove_item(self, x: int, y: int) -> tuple[bool, str]:
        """
        Remove an item from the map grid.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Tuple of (success, message)
        """
        tile = self.get_tile(x, y)
        if not tile:
            return False, "Invalid coordinates"
        
        if tile.is_empty:
            return False, "Tile is already empty"
        
        item_name = ITEM_INFO.get(tile.item_id, {}).get("name", tile.item_id or "item")
        tile.clear()
        return True, f"Removed {item_name}"
    
    # ============ ENCLOSURE MANAGEMENT ============
    
    def add_enclosure(self, enclosure: Enclosure) -> None:
        """Add an enclosure to the zoo."""
        self._enclosures[enclosure.enclosure_id] = enclosure
    
    def build_enclosure(
        self, 
        habitat_type: str, 
        name: Optional[str] = None, 
        cost: float = 1000.0
    ) -> Enclosure:
        """
        Build a new enclosure.
        
        Raises:
            InsufficientFundsError: If budget is too low
        """
        if self._budget < cost:
            raise InsufficientFundsError(cost, self._budget)
        
        enclosure_id = f"enc_{habitat_type}_{len(self._enclosures) + 1}"
        kwargs = {"name": name} if name else {}
        enclosure = create_enclosure(habitat_type, enclosure_id, **kwargs)
        
        self._budget -= cost
        self._total_expenses += cost
        self._enclosures[enclosure_id] = enclosure
        
        self._event_manager.emit(
            EventTypes.PURCHASE, 
            enclosure, 
            f"Built new enclosure: {enclosure.name}", 
            cost=cost
        )
        return enclosure
    
    def get_enclosure_for_animal(self, animal: Animal) -> Optional[Enclosure]:
        """Find which enclosure an animal is in."""
        for enclosure in self._enclosures.values():
            if animal in enclosure.animals:
                return enclosure
        return None

    def _get_enclosure_tile_map(self) -> Dict[str, set[tuple[int, int]]]:
        """Build enclosure_id -> occupied map tile coordinates."""
        tile_map: Dict[str, set[tuple[int, int]]] = {}
        for x in range(self.GRID_SIZE):
            for y in range(self.GRID_SIZE):
                tile = self._map_grid[x][y]
                enclosure = tile.enclosure_ref
                if tile.tile_type != TileType.ENCLOSURE or enclosure is None:
                    continue
                tile_map.setdefault(enclosure.enclosure_id, set()).add((x, y))
        return tile_map

    def _enclosures_are_adjacent(
        self,
        enclosure_a: Enclosure,
        enclosure_b: Enclosure,
        tile_map: Dict[str, set[tuple[int, int]]],
    ) -> bool:
        """Return True when two enclosures touch on map edges."""
        tiles_a = tile_map.get(enclosure_a.enclosure_id)
        tiles_b = tile_map.get(enclosure_b.enclosure_id)
        if not tiles_a or not tiles_b:
            return False

        for ax, ay in tiles_a:
            for bx, by in tiles_b:
                if abs(ax - bx) + abs(ay - by) == 1:
                    return True
        return False

    def _predation_exposure_for_platypus(
        self,
        platypus: Animal,
        tile_map: Dict[str, set[tuple[int, int]]],
    ) -> tuple[str, Optional[Enclosure]]:
        """
        Return predation exposure for a platypus.

        Returns:
            Tuple of (exposure, crocodile_enclosure), where exposure is:
            "shared", "adjacent", or "none".
        """
        enclosure = self.get_enclosure_for_animal(platypus)
        if enclosure is None:
            return "none", None

        shared_croc = any(
            other.is_alive and other.species == "SaltwaterCroc"
            for other in enclosure.animals
        )
        if shared_croc:
            return "shared", enclosure

        for predator_enclosure in self._enclosures.values():
            if predator_enclosure.enclosure_id == enclosure.enclosure_id:
                continue
            has_croc = any(
                animal.is_alive and animal.species == "SaltwaterCroc"
                for animal in predator_enclosure.animals
            )
            if not has_croc:
                continue
            if self._enclosures_are_adjacent(enclosure, predator_enclosure, tile_map):
                return "adjacent", predator_enclosure

        return "none", None

    def _get_outback_devil_prey_animals(self, enclosure: Enclosure) -> List[Animal]:
        """Return living prey animals exposed to Tasmanian Devil in one outback enclosure."""
        if enclosure.get_habitat_type() != "outback_savanna":
            return []

        has_devil = any(
            animal.is_alive and animal.species == "TasmanianDevil"
            for animal in enclosure.animals
        )
        if not has_devil:
            return []

        return [
            animal
            for animal in enclosure.animals
            if animal.is_alive and animal.species != "TasmanianDevil"
        ]

    def _apply_outback_devil_entry_risk(self, enclosure: Enclosure, added_animal: Animal) -> None:
        """Apply immediate predation risk when devils and other species mix in outback."""
        prey_animals = self._get_outback_devil_prey_animals(enclosure)
        if not prey_animals:
            return

        for prey in prey_animals:
            self._outback_predation_risk_by_prey[prey.name] = max(
                self.PREDATION_LOW_RISK_THRESHOLD,
                int(self._outback_predation_risk_by_prey.get(prey.name, 0)),
            )

        if added_animal.species == "TasmanianDevil":
            msg = (
                f"⚠️ Predation risk: {added_animal.name} the Tasmanian Devil was added to "
                f"{enclosure.name} with other species present."
            )
        else:
            msg = (
                f"⚠️ Predation risk: {added_animal.name} was added to {enclosure.name} "
                "containing Tasmanian Devil(s)."
            )
        self._event_manager.emit(EventTypes.RANDOM_EVENT, added_animal, msg)

    def get_enclosure_predation_status(self, enclosure_id: str) -> tuple[int, str]:
        """
        Get predation risk summary for one enclosure.

        Returns:
            Tuple of (max_risk, summary_text). Empty summary means no active risk.
        """
        enclosure = self._enclosures.get(enclosure_id)
        if enclosure is None:
            return 0, ""

        platypuses = [
            animal
            for animal in enclosure.animals
            if animal.is_alive and animal.species == "Platypus"
        ]

        tile_map = self._get_enclosure_tile_map()
        lines: List[str] = []
        max_risk = 0
        for platypus in platypuses:
            risk = int(self._predation_risk_by_platypus.get(platypus.name, 0))
            exposure, predator_enclosure = self._predation_exposure_for_platypus(
                platypus,
                tile_map,
            )
            if exposure == "none" and risk <= 0:
                continue

            max_risk = max(max_risk, risk)
            if exposure == "shared":
                context = "sharing with crocodiles"
            elif exposure == "adjacent" and predator_enclosure is not None:
                context = f"near crocodiles in {predator_enclosure.name}"
            else:
                context = "currently stable"
            lines.append(f"{platypus.name}: {risk}% ({context})")

        has_crocodile = any(
            animal.is_alive and animal.species == "SaltwaterCroc"
            for animal in enclosure.animals
        )
        if has_crocodile:
            tracked = {platypus.name for platypus in platypuses}
            for animal in self._animals.values():
                if not animal.is_alive or animal.species != "Platypus":
                    continue
                if animal.name in tracked:
                    continue

                risk = int(self._predation_risk_by_platypus.get(animal.name, 0))
                if risk <= 0:
                    continue

                exposure, predator_enclosure = self._predation_exposure_for_platypus(
                    animal,
                    tile_map,
                )
                if exposure == "shared":
                    platypus_enclosure = self.get_enclosure_for_animal(animal)
                    if (
                        platypus_enclosure is None
                        or platypus_enclosure.enclosure_id != enclosure_id
                    ):
                        continue
                    context = "sharing this enclosure with crocodiles"
                elif exposure == "adjacent" and predator_enclosure is not None:
                    if predator_enclosure.enclosure_id != enclosure_id:
                        continue
                    context = "in adjacent enclosure"
                else:
                    continue

                max_risk = max(max_risk, risk)
                lines.append(f"{animal.name}: {risk}% ({context})")

        outback_prey = self._get_outback_devil_prey_animals(enclosure)
        for prey in outback_prey:
            risk = int(self._outback_predation_risk_by_prey.get(prey.name, 0))
            if risk <= 0:
                continue
            max_risk = max(max_risk, risk)
            lines.append(
                f"{prey.name}: {risk}% (sharing Outback with Tasmanian Devil)"
            )

        if enclosure.get_habitat_type() == "outback_savanna" and not outback_prey:
            for animal in enclosure.animals:
                if not animal.is_alive or animal.species == "TasmanianDevil":
                    continue
                risk = int(self._outback_predation_risk_by_prey.get(animal.name, 0))
                if risk <= 0:
                    continue
                max_risk = max(max_risk, risk)
                lines.append(f"{animal.name}: {risk}% (risk decaying)")

        return max_risk, " | ".join(lines)

    def reinforce_enclosure_barrier(self, enclosure_id: str) -> tuple[bool, str]:
        """
        Spend money to upgrade one enclosure's reinforced barriers.

        Returns:
            Tuple of (success, message).
        """
        enclosure = self._enclosures.get(enclosure_id)
        if enclosure is None:
            return False, "Enclosure not found."
        if enclosure.barrier_level >= enclosure.MAX_BARRIER_LEVEL:
            return False, f"{enclosure.name} already has maximum barrier reinforcement."
        if self._budget < self.BARRIER_UPGRADE_COST:
            return (
                False,
                (
                    f"Insufficient funds for barrier upgrade. Need ${self.BARRIER_UPGRADE_COST:,.2f}, "
                    f"have ${self._budget:,.2f}."
                ),
            )

        upgraded = enclosure.upgrade_barrier()
        if not upgraded:
            return False, f"{enclosure.name} already has maximum barrier reinforcement."

        self._budget -= self.BARRIER_UPGRADE_COST
        self._total_expenses += self.BARRIER_UPGRADE_COST

        msg = (
            f"🛡️ Reinforced barriers upgraded in {enclosure.name} "
            f"(Level {enclosure.barrier_level}/{enclosure.MAX_BARRIER_LEVEL})."
        )
        self._event_manager.emit(EventTypes.PURCHASE, enclosure, msg, cost=self.BARRIER_UPGRADE_COST)
        return True, msg

    def emergency_relocate_platypus(self, from_enclosure_id: str) -> tuple[bool, str]:
        """
        Move one platypus to the safest available billabong enclosure.

        Returns:
            Tuple of (success, message).
        """
        from_enclosure = self._enclosures.get(from_enclosure_id)
        if from_enclosure is None:
            return False, "Source enclosure not found."

        platypuses = [
            animal
            for animal in from_enclosure.animals
            if animal.is_alive and animal.species == "Platypus"
        ]
        if not platypuses:
            return False, "No living platypus available to relocate in this enclosure."

        if self._budget < self.EMERGENCY_RELOCATION_COST:
            return (
                False,
                (
                    f"Insufficient funds for relocation. Need ${self.EMERGENCY_RELOCATION_COST:,.2f}, "
                    f"have ${self._budget:,.2f}."
                ),
            )

        candidate_enclosures = [
            enclosure
            for enclosure in self._enclosures.values()
            if (
                enclosure.enclosure_id != from_enclosure_id
                and enclosure.get_habitat_type() == "billabong"
                and not enclosure.is_full
            )
        ]
        if not candidate_enclosures:
            return False, "No spare billabong enclosure is available for relocation."

        safe_candidates = [
            enclosure
            for enclosure in candidate_enclosures
            if not any(
                animal.is_alive and animal.species == "SaltwaterCroc"
                for animal in enclosure.animals
            )
        ]
        if not safe_candidates:
            return False, "No crocodile-free billabong enclosure is available for safe relocation."

        # Prefer enclosures that are not adjacent to crocodile enclosures (buffer zone).
        tile_map = self._get_enclosure_tile_map()
        crocodile_enclosures = [
            enclosure
            for enclosure in self._enclosures.values()
            if any(
                animal.is_alive and animal.species == "SaltwaterCroc"
                for animal in enclosure.animals
            )
        ]
        buffered_candidates = [
            enclosure
            for enclosure in safe_candidates
            if not any(
                self._enclosures_are_adjacent(enclosure, predator_enclosure, tile_map)
                for predator_enclosure in crocodile_enclosures
            )
        ]
        if buffered_candidates:
            safe_candidates = buffered_candidates

        # Move the most at-risk platypus first.
        platypus = max(
            platypuses,
            key=lambda animal: self._predation_risk_by_platypus.get(animal.name, 0),
        )
        target = min(safe_candidates, key=lambda enclosure: len(enclosure.animals))

        from_enclosure.remove_animal(platypus)
        target.add_animal(platypus)

        self._budget -= self.EMERGENCY_RELOCATION_COST
        self._total_expenses += self.EMERGENCY_RELOCATION_COST
        self._predation_risk_by_platypus[platypus.name] = 0

        msg = (
            f"🚚 Emergency relocation complete: {platypus.name} moved from "
            f"{from_enclosure.name} to {target.name}."
        )
        self._event_manager.emit(EventTypes.RANDOM_EVENT, platypus, msg)
        return True, msg
    
    # ============ ANIMAL MANAGEMENT ============
    
    def add_animal(self, animal: Animal, enclosure_id: str) -> None:
        """
        Add an animal to a specific enclosure.
        
        Raises:
            KeyError: If enclosure doesn't exist
            HabitatCapacityExceededError: If enclosure is full
            InvalidHabitatError: If habitat type doesn't match
            ValueError: If animal name already exists
        """
        if enclosure_id not in self._enclosures:
            raise KeyError(f"Enclosure '{enclosure_id}' not found")
        
        if animal.name in self._animals:
            raise ValueError(f"Animal named '{animal.name}' already exists!")
        
        enclosure = self._enclosures[enclosure_id]
        enclosure.add_animal(animal)  # May raise exceptions
        self._animals[animal.name] = animal
        self._apply_outback_devil_entry_risk(enclosure, animal)
    
    def purchase_animal(
        self, 
        animal_type: str, 
        name: str, 
        age: int, 
        enclosure_id: str, 
        gender: str = "unknown"
    ) -> Animal:
        """
        Purchase and add a new animal.
        
        Raises:
            InsufficientFundsError: If budget is too low
            ValueError: If animal type is unknown
        """
        info = AnimalFactory.get_animal_info(animal_type)
        cost = info["cost"]
        
        if self._budget < cost:
            raise InsufficientFundsError(cost, self._budget)
        
        animal = AnimalFactory.create_animal(
            animal_type, 
            name=name, 
            age=age, 
            gender=gender
        )
        self.add_animal(animal, enclosure_id)
        
        self._budget -= cost
        self._total_expenses += cost
        
        self._event_manager.emit(
            EventTypes.PURCHASE, 
            animal,
            f"Purchased {animal.species}: {name}", 
            cost=cost
        )
        return animal
    
    def remove_animal(self, animal_name: str) -> bool:
        """Remove an animal from the zoo (death or transfer)."""
        if animal_name not in self._animals:
            return False
        
        animal = self._animals[animal_name]
        enclosure = self.get_enclosure_for_animal(animal)
        if enclosure:
            enclosure.remove_animal(animal)
        
        del self._animals[animal_name]
        self._predation_risk_by_platypus.pop(animal_name, None)
        self._outback_predation_risk_by_prey.pop(animal_name, None)
        return True

    def rename_animal(self, current_name: str, new_name: str) -> tuple[bool, str]:
        """
        Rename an existing animal and update name-indexed state.

        Returns:
            Tuple of (success, message)
        """
        if current_name not in self._animals:
            return False, f"Animal '{current_name}' not found."

        cleaned_name = new_name.strip()
        if not cleaned_name:
            return False, "Name cannot be empty."

        if cleaned_name != current_name and cleaned_name in self._animals:
            return False, f"An animal named '{cleaned_name}' already exists."

        animal = self._animals[current_name]
        if cleaned_name == current_name:
            return True, f"{current_name} kept the same name."

        del self._animals[current_name]
        animal._name = cleaned_name
        self._animals[cleaned_name] = animal

        if current_name in self._consecutive_happy_days:
            self._consecutive_happy_days[cleaned_name] = self._consecutive_happy_days.pop(
                current_name
            )
        if current_name in self._predation_risk_by_platypus:
            self._predation_risk_by_platypus[cleaned_name] = self._predation_risk_by_platypus.pop(
                current_name
            )
        if current_name in self._outback_predation_risk_by_prey:
            self._outback_predation_risk_by_prey[cleaned_name] = self._outback_predation_risk_by_prey.pop(
                current_name
            )

        return True, f"Renamed {current_name} to {cleaned_name}."

    def generate_random_baby_name(self, species: str) -> str:
        """Generate a unique random name for a newborn of the given species."""
        pool = self.RANDOM_BABY_NAMES.get(species, self.GENERIC_BABY_NAMES)
        base = random.choice(pool)
        candidate = base
        suffix = 2
        while candidate in self._animals:
            candidate = f"{base} {suffix}"
            suffix += 1
        return candidate
    
    # ============ FEEDING ============
    
    def feed_animal(self, animal_name: str, food_type: str) -> tuple[bool, str]:
        """
        Feed an animal.
        
        Returns (success, message).
        """
        if animal_name not in self._animals:
            return False, f"Animal '{animal_name}' not found"
        
        animal = self._animals[animal_name]
        
        if not animal.is_alive:
            return False, f"{animal_name} is no longer alive"
        
        required_diet = animal.get_diet()
        if food_type != required_diet:
            return False, f"{animal_name} eats {required_diet}, not {food_type}"
        
        if self._food_stock.get(food_type, 0) < 1:
            return False, f"No {food_type} in stock!"
        
        # Get food item and feed
        food = FOOD_TYPES.get(food_type)
        if not food:
            return False, f"Unknown food type: {food_type}"
        if animal.feed(food):
            self._food_stock[food_type] -= 1
            self._event_manager.emit(
                EventTypes.ANIMAL_FED, 
                animal,
                f"{animal_name} was fed {food_type}"
            )
            return True, f"{animal_name} happily ate the {food.name}!"
        
        return False, f"{animal_name} refused to eat"

    def treat_sick_animal(self, animal_name: str, medicine_type: str) -> tuple[bool, str]:
        """
        Treat and cure a sick animal using one medicine dose.

        Returns (success, message).
        """
        if animal_name not in self._animals:
            return False, f"Animal '{animal_name}' not found"

        if medicine_type not in MEDICINE_TYPES:
            return False, f"Unknown medicine type: {medicine_type}"

        animal = self._animals[animal_name]
        if not animal.is_alive:
            return False, f"{animal_name} is no longer alive"
        if not animal.is_sick:
            return False, f"{animal_name} is not sick."

        if self._medicine_stock.get(medicine_type, 0) < 1:
            return False, f"No {medicine_type} medicine in stock!"

        medicine = MEDICINE_TYPES[medicine_type]
        if not medicine.can_treat(animal.get_animal_type()):
            return False, f"{medicine.name} cannot treat {animal.get_animal_type()}s."

        healing = medicine.apply(animal)
        self._medicine_stock[medicine_type] -= 1
        cured = animal.cure_sickness()

        if cured:
            self._event_manager.emit(
                EventTypes.ANIMAL_RECOVERED,
                animal,
                f"{animal_name} recovered from illness after treatment."
            )
            return True, f"{animal_name} was treated and recovered! Health +{healing}"

        return False, f"{animal_name} could not be cured."
    
    # ============ RESOURCES ============
    
    def buy_food(self, food_type: str, quantity: int) -> tuple[bool, str]:
        """Buy food for the zoo."""
        if food_type not in FOOD_TYPES:
            return False, f"Unknown food type: {food_type}"
        
        food = FOOD_TYPES[food_type]
        total_cost = food.cost * quantity
        
        if self._budget < total_cost:
            return False, (
                f"Insufficient funds: need ${total_cost:.2f}, "
                f"have ${self._budget:.2f}"
            )
        
        self._budget -= total_cost
        self._total_expenses += total_cost
        self._food_stock[food_type] = self._food_stock.get(food_type, 0) + quantity
        
        return True, f"Purchased {quantity}x {food.name} for ${total_cost:.2f}"
    
    def buy_medicine(self, medicine_type: str, quantity: int) -> tuple[bool, str]:
        """Buy medicine for the zoo."""
        if medicine_type not in MEDICINE_TYPES:
            return False, f"Unknown medicine type: {medicine_type}"
        
        medicine = MEDICINE_TYPES[medicine_type]
        total_cost = medicine.cost * quantity
        
        if self._budget < total_cost:
            return False, (
                f"Insufficient funds: need ${total_cost:.2f}, "
                f"have ${self._budget:.2f}"
            )
        
        self._budget -= total_cost
        self._total_expenses += total_cost
        self._medicine_stock[medicine_type] = (
            self._medicine_stock.get(medicine_type, 0) + quantity
        )
        
        return True, f"Purchased {quantity}x {medicine.name} for ${total_cost:.2f}"
    
    # ============ STAFF ============
    
    def hire_keeper(self, keeper: ZooKeeper, signing_bonus: float = 100.0) -> None:
        """Hire a new zookeeper."""
        if self._budget < signing_bonus:
            raise InsufficientFundsError(signing_bonus, self._budget)
        
        self._budget -= signing_bonus
        self._total_expenses += signing_bonus
        self._keepers[keeper.employee_id] = keeper
    
    def fire_keeper(self, employee_id: str) -> bool:
        """Fire a zookeeper."""
        if employee_id in self._keepers:
            del self._keepers[employee_id]
            return True
        return False
    
    def pay_staff_wages(self) -> float:
        """Pay daily wages to all staff. Returns total paid."""
        total = sum(k.daily_cost for k in self._keepers.values())
        self._budget -= total
        self._total_expenses += total
        return total
    
    # ============ MISSIONS ============
    
    def add_mission(self, mission: Mission) -> bool:
        """
        Add a mission to the active mission list.

        Returns:
            True if mission was added, False if duplicate mission_id exists.
        """
        if any(existing.mission_id == mission.mission_id for existing in self._active_missions):
            return False
        self._active_missions.append(mission)
        return True

    def start_mission(self, mission: Mission) -> None:
        """
        Start a new mission (legacy wrapper for add_mission).
        
        Args:
            mission: Mission to activate
        """
        self.add_mission(mission)

    def _mission_difficulty_for_day(self) -> str:
        """Choose mission difficulty band based on current day."""
        if self._day < 15:
            return "easy"
        if self._day < 30:
            return "medium"
        return "hard"

    def _add_periodic_mission_if_due(self) -> Optional[Mission]:
        """Add a new mission every 3 in-game days."""
        if self._day % 3 != 0:
            return None

        active_types = {
            mission.mission_type
            for mission in self._active_missions
            if not mission.is_complete and not mission.is_failed
        }
        mission = generate_random_mission(
            difficulty=self._mission_difficulty_for_day(),
            zoo=self,
            exclude_types=active_types,
        )
        if self.add_mission(mission):
            return mission
        return None

    def _update_global_happy_streaks(self) -> None:
        """Track consecutive happy days for each living, healthy animal."""
        currently_happy = {
            animal.name
            for animal in self._animals.values()
            if animal.is_alive and not animal.is_sick and animal.happiness >= 70
        }

        for animal_name in list(self._consecutive_happy_days.keys()):
            if animal_name in currently_happy:
                self._consecutive_happy_days[animal_name] += 1
            else:
                self._consecutive_happy_days[animal_name] = 0

        for animal_name in currently_happy:
            if animal_name not in self._consecutive_happy_days:
                self._consecutive_happy_days[animal_name] = 1

    def _update_single_mission_progress(self, mission: Mission) -> None:
        """Update progress for one mission based on current zoo state."""
        if mission.is_complete or mission.is_failed:
            return

        if mission.mission_type == MissionType.KEEP_HAPPY:
            target_type = mission.target_animal
            happy_animals = [
                animal
                for animal in self._animals.values()
                if (
                    animal.is_alive
                    and not animal.is_sick
                    and animal.species == target_type
                    and animal.happiness >= 70
                )
            ]
            required_count = mission.target_value
            requirements_met = len(happy_animals) >= required_count
            if requirements_met:
                mission.update_progress(1)
            else:
                mission.set_progress(0)

            required_days = int(
                mission.custom_data.get(
                    "required_days",
                    getattr(mission, "required_days", 5),
                )
            )
            if mission.current_progress >= required_days:
                mission.is_complete = True
            return

        if mission.mission_type == MissionType.BREED_ANIMALS:
            baseline_births = int(mission.custom_data.get("baseline_births", 0))
            mission.set_progress(max(0, self._animals_born - baseline_births))
            return

        if mission.mission_type == MissionType.VISITOR_COUNT:
            baseline_visitors = int(mission.custom_data.get("baseline_visitors", 0))
            mission.set_progress(max(0, self._total_visitors_served - baseline_visitors))
            return

        if mission.mission_type == MissionType.PROFIT_TARGET:
            baseline_profit = float(mission.custom_data.get("baseline_profit", 0.0))
            current_profit = self._total_revenue - self._total_expenses
            mission.set_progress(max(0, int(current_profit - baseline_profit)))
            return

        if mission.mission_type == MissionType.BUILD_ENCLOSURES:
            baseline_enclosures = int(mission.custom_data.get("baseline_enclosures", 0))
            mission.set_progress(max(0, len(self._enclosures) - baseline_enclosures))
    
    def update_mission_progress(
        self,
        include_types: Optional[set[MissionType]] = None,
    ) -> None:
        """Update mission progress based on current zoo state."""
        if not self._active_missions:
            return

        if include_types is None or MissionType.KEEP_HAPPY in include_types:
            self._update_global_happy_streaks()

        for mission in self._active_missions:
            if include_types is not None and mission.mission_type not in include_types:
                continue
            self._update_single_mission_progress(mission)
    
    def complete_mission(self, mission: Mission) -> tuple[bool, str, List[str], List[str]]:
        """
        Complete an active mission and award rewards.
        
        Returns:
            Tuple of (success, message, births, breeding_events)
        """
        if mission not in self._active_missions:
            return False, "No active mission.", [], []
        
        if not mission.is_complete:
            return False, "Mission not yet complete.", [], []
        
        # Award rewards
        self._budget += mission.reward.money
        mission_births, breeding_events = self._breed_animals_after_mission()
        
        msg = (
            f"🎉 Mission Complete: {mission.title}!\n"
            f"Rewards: {mission.reward.description}"
        )
        
        self._active_missions.remove(mission)
        
        return True, msg, mission_births, breeding_events

    def _resolve_active_missions(self) -> tuple[List[str], List[str]]:
        """Resolve completed or failed missions and return (events, births)."""
        events: List[str] = []
        births: List[str] = []

        for mission in list(self._active_missions):
            if mission.is_complete:
                success, msg, mission_births, breeding_events = self.complete_mission(mission)
                if success:
                    events.append(msg)
                    events.extend(breeding_events)
                    births.extend(mission_births)
            elif mission.is_failed:
                events.append(f"❌ Mission Failed: {mission.title}")
                self._active_missions.remove(mission)

        return events, births
    
    def check_mission_failure(self) -> bool:
        """
        Check if mission has failed.
        
        Returns:
            True if mission failed
        """
        return any(mission.is_failed for mission in self._active_missions)
    
    # ============ VISITORS ============

    def use_feeding_frenzy_attempt(self, count: int = 1) -> bool:
        """
        Consume Feeding Frenzy toss attempts from the shared daily pool.

        Args:
            count: Number of attempts to consume.

        Returns:
            True if attempts were consumed, False if not enough attempts remain.
        """
        if count < 1:
            return False
        if self._feeding_frenzy_attempts_remaining < count:
            return False

        self._feeding_frenzy_attempts_remaining -= count
        return True

    def use_feeding_frenzy_toss(self, food_type: str) -> tuple[bool, str]:
        """
        Consume one Feeding Frenzy toss and one unit of the chosen food.

        Returns:
            Tuple of (success, message)
        """
        normalised_food = food_type.strip().lower()
        if normalised_food not in FOOD_TYPES:
            return False, f"Unknown food type: {food_type}"

        if self._food_stock.get(normalised_food, 0) < 1:
            return False, f"No {normalised_food} in stock!"

        if not self.use_feeding_frenzy_attempt():
            return False, "No toss attempts remain for today."

        self._food_stock[normalised_food] -= 1
        return True, f"Tossed {normalised_food}. {self._food_stock[normalised_food]} left."
    
    def generate_daily_visitors(self) -> int:
        """Generate visitors for the day based on zoo appeal."""
        # Base visitors + welfare and diversity bonuses - penalty for sick animals
        base_visitors = 20
        welfare_bonus = int(self.average_animal_welfare / 10)
        # First species is baseline; extra variety attracts more visitors.
        diversity_bonus = min(18, max(0, self.species_diversity - 1) * 2)
        sick_penalty = self.sick_animal_count * 2
        
        num_visitors = max(5, base_visitors + welfare_bonus + diversity_bonus - sick_penalty)
        
        self._visitors.clear()
        for i in range(num_visitors):
            visitor = generate_random_visitor(f"v_{self._day}_{i}")
            self._visitors.append(visitor)
        self._total_visitors_served += num_visitors

        # Reset Feeding Frenzy daily attempt pool to match today's visitors.
        self._feeding_frenzy_pool_day = self._day
        self._feeding_frenzy_attempts_total = num_visitors
        self._feeding_frenzy_attempts_remaining = num_visitors
        
        return num_visitors
    
    def collect_ticket_revenue(self) -> float:
        """Collect ticket revenue from all visitors."""
        revenue = sum(
            v.ticket_type.base_price * self._ticket_modifier 
            for v in self._visitors
        )
        self._budget += revenue
        self._total_revenue += revenue
        return revenue
    
    def collect_donations(self) -> float:
        """Collect random donations from satisfied visitors."""
        total = 0.0
        for visitor in self._visitors:
            donation = visitor.random_donation()
            total += donation
        
        self._budget += total
        self._total_revenue += total
        
        if total > 0:
            self._event_manager.emit(
                EventTypes.VISITOR_DONATED, 
                None,
                f"Visitors donated ${total:.2f} today!"
            )
        return total

    def _process_predation_risk_events(self, report: Dict[str, Any]) -> List[str]:
        """
        Process predation risk, warnings, and mishaps.

        Includes:
        - Croc-versus-platypus risk (shared or adjacent billabongs)
        - Tasmanian Devil risk for mixed-species outback enclosures
        """
        events: List[str] = []
        living_platypus = {
            animal.name
            for animal in self._animals.values()
            if animal.is_alive and animal.species == "Platypus"
        }
        for tracked_name in list(self._predation_risk_by_platypus.keys()):
            if tracked_name not in living_platypus:
                del self._predation_risk_by_platypus[tracked_name]

        if not living_platypus:
            return events

        tile_map = self._get_enclosure_tile_map()
        incident_count = 0

        for platypus_name in living_platypus:
            platypus = self._animals.get(platypus_name)
            if not platypus or not platypus.is_alive:
                continue

            enclosure = self.get_enclosure_for_animal(platypus)
            if enclosure is None:
                continue

            exposure, predator_enclosure = self._predation_exposure_for_platypus(platypus, tile_map)
            current_risk = int(self._predation_risk_by_platypus.get(platypus.name, 0))

            if exposure == "shared":
                mitigation = enclosure.barrier_level * 4
                risk_gain = max(6, self.PREDATION_SHARED_RISK_GAIN - mitigation)
                new_risk = min(100, current_risk + risk_gain)
            elif exposure == "adjacent":
                adjacent_barrier = enclosure.barrier_level
                if predator_enclosure is not None:
                    adjacent_barrier += predator_enclosure.barrier_level
                risk_gain = max(2, self.PREDATION_ADJACENT_RISK_GAIN - (adjacent_barrier * 3))
                new_risk = min(100, current_risk + risk_gain)
            else:
                new_risk = max(0, current_risk - self.PREDATION_RISK_DECAY)

            self._predation_risk_by_platypus[platypus.name] = new_risk

            if exposure != "none" and new_risk >= self.PREDATION_LOW_RISK_THRESHOLD:
                health_loss = 2 + (new_risk // 35)
                happiness_loss = 3 + (new_risk // 25)
                platypus.health = platypus.health - health_loss
                platypus.happiness = platypus.happiness - happiness_loss
                events.append(
                    f"⚠️ Predation risk rising for {platypus.name}: {new_risk}% "
                    f"(-{health_loss} health, -{happiness_loss} happiness). "
                    "Consider relocation or barrier upgrades."
                )

            if not platypus.is_alive:
                if platypus.name not in report["deaths"]:
                    report["deaths"].append(platypus.name)
                    self._animals_died += 1
                events.append(
                    f"☠️ {platypus.name} succumbed to sustained predation stress."
                )
                self._event_manager.emit(
                    EventTypes.ANIMAL_DEATH,
                    platypus,
                    f"{platypus.name} died under predation pressure.",
                )
                self._predation_risk_by_platypus.pop(platypus.name, None)
                incident_count += 1
                continue

            if exposure == "none" or new_risk < self.PREDATION_HIGH_RISK_THRESHOLD:
                continue

            base_chance = (
                self.PREDATION_SHARED_MISHAP_CHANCE
                if exposure == "shared"
                else self.PREDATION_ADJACENT_MISHAP_CHANCE
            )
            mishap_chance = min(0.90, base_chance + ((new_risk - self.PREDATION_HIGH_RISK_THRESHOLD) * 0.004))
            if random.random() >= mishap_chance:
                events.append(
                    f"🚨 High predation risk for {platypus.name}: {new_risk}%. "
                    "Relocate platypus or reinforce barriers now."
                )
                continue

            incident_count += 1
            location_name = enclosure.name if exposure == "shared" else (
                predator_enclosure.name if predator_enclosure else enclosure.name
            )

            if exposure == "shared" and random.random() < self.PREDATION_FATAL_CHANCE:
                platypus.health = 0
                if platypus.name not in report["deaths"]:
                    report["deaths"].append(platypus.name)
                    self._animals_died += 1
                events.append(
                    f"☠️ Predation incident in {location_name}! {platypus.name} was lost."
                )
                self._event_manager.emit(
                    EventTypes.ANIMAL_DEATH,
                    platypus,
                    f"Predation incident: {platypus.name} was lost in {location_name}.",
                )
                self._predation_risk_by_platypus.pop(platypus.name, None)
                continue

            injury = random.randint(35, 55) if exposure == "shared" else random.randint(25, 40)
            platypus.health = platypus.health - injury
            platypus.happiness = platypus.happiness - 25
            events.append(
                f"🩸 Predation mishap in {location_name}! {platypus.name} was injured (-{injury} health)."
            )
            if not platypus.is_alive:
                if platypus.name not in report["deaths"]:
                    report["deaths"].append(platypus.name)
                    self._animals_died += 1
                self._event_manager.emit(
                    EventTypes.ANIMAL_DEATH,
                    platypus,
                    f"{platypus.name} died from predation injuries in {location_name}.",
                )
                self._predation_risk_by_platypus.pop(platypus.name, None)
            else:
                self._predation_risk_by_platypus[platypus.name] = max(25, new_risk - 45)

        # Tasmanian Devil predation pressure for mixed-species Outback enclosures.
        for tracked_name in list(self._outback_predation_risk_by_prey.keys()):
            tracked_animal = self._animals.get(tracked_name)
            if (
                tracked_animal is None
                or not tracked_animal.is_alive
                or tracked_animal.species == "TasmanianDevil"
            ):
                del self._outback_predation_risk_by_prey[tracked_name]

        outback_exposure_by_prey: Dict[str, Enclosure] = {}
        for enclosure in self._enclosures.values():
            prey_animals = self._get_outback_devil_prey_animals(enclosure)
            for prey in prey_animals:
                outback_exposure_by_prey[prey.name] = enclosure

        tracked_or_exposed = set(self._outback_predation_risk_by_prey.keys()) | set(
            outback_exposure_by_prey.keys()
        )
        for prey_name in tracked_or_exposed:
            prey = self._animals.get(prey_name)
            if prey is None or not prey.is_alive or prey.species == "TasmanianDevil":
                self._outback_predation_risk_by_prey.pop(prey_name, None)
                continue

            current_risk = int(self._outback_predation_risk_by_prey.get(prey.name, 0))
            exposure_enclosure = outback_exposure_by_prey.get(prey.name)
            if exposure_enclosure is None:
                decayed_risk = max(0, current_risk - self.PREDATION_RISK_DECAY)
                if decayed_risk <= 0:
                    self._outback_predation_risk_by_prey.pop(prey.name, None)
                else:
                    self._outback_predation_risk_by_prey[prey.name] = decayed_risk
                continue

            mitigation = exposure_enclosure.barrier_level * 4
            risk_gain = max(5, self.DEVIL_OUTBACK_RISK_GAIN - mitigation)
            new_risk = min(100, current_risk + risk_gain)
            self._outback_predation_risk_by_prey[prey.name] = new_risk

            if new_risk >= self.PREDATION_LOW_RISK_THRESHOLD:
                health_loss = 2 + (new_risk // 40)
                happiness_loss = 4 + (new_risk // 25)
                prey.health = prey.health - health_loss
                prey.happiness = prey.happiness - happiness_loss
                events.append(
                    f"⚠️ {prey.name} is under Tasmanian Devil predation stress in "
                    f"{exposure_enclosure.name}: {new_risk}% "
                    f"(-{health_loss} health, -{happiness_loss} happiness)."
                )

            if not prey.is_alive:
                if prey.name not in report["deaths"]:
                    report["deaths"].append(prey.name)
                    self._animals_died += 1
                events.append(
                    f"☠️ {prey.name} succumbed to Tasmanian Devil predation stress in "
                    f"{exposure_enclosure.name}."
                )
                self._event_manager.emit(
                    EventTypes.ANIMAL_DEATH,
                    prey,
                    f"{prey.name} died under Tasmanian Devil predation pressure.",
                )
                self._outback_predation_risk_by_prey.pop(prey.name, None)
                incident_count += 1
                continue

            if new_risk < self.PREDATION_HIGH_RISK_THRESHOLD:
                continue

            mishap_chance = min(
                0.90,
                self.DEVIL_OUTBACK_MISHAP_CHANCE
                + ((new_risk - self.PREDATION_HIGH_RISK_THRESHOLD) * 0.004),
            )
            if random.random() >= mishap_chance:
                events.append(
                    f"🚨 High Tasmanian Devil predation risk for {prey.name} in "
                    f"{exposure_enclosure.name}: {new_risk}%. Separate species or "
                    "reinforce barriers."
                )
                continue

            incident_count += 1
            if random.random() < self.DEVIL_OUTBACK_FATAL_CHANCE:
                prey.health = 0
                if prey.name not in report["deaths"]:
                    report["deaths"].append(prey.name)
                    self._animals_died += 1
                events.append(
                    f"☠️ Tasmanian Devil predation incident in {exposure_enclosure.name}! "
                    f"{prey.name} was lost."
                )
                self._event_manager.emit(
                    EventTypes.ANIMAL_DEATH,
                    prey,
                    f"Predation incident: {prey.name} was lost in {exposure_enclosure.name}.",
                )
                self._outback_predation_risk_by_prey.pop(prey.name, None)
                continue

            injury = random.randint(22, 40)
            prey.health = prey.health - injury
            prey.happiness = prey.happiness - 18
            events.append(
                f"🩸 Predation incident in {exposure_enclosure.name}! "
                f"{prey.name} was injured by Tasmanian Devil aggression (-{injury} health)."
            )
            if not prey.is_alive:
                if prey.name not in report["deaths"]:
                    report["deaths"].append(prey.name)
                    self._animals_died += 1
                self._event_manager.emit(
                    EventTypes.ANIMAL_DEATH,
                    prey,
                    f"{prey.name} died from Tasmanian Devil predation injuries in "
                    f"{exposure_enclosure.name}.",
                )
                self._outback_predation_risk_by_prey.pop(prey.name, None)
            else:
                self._outback_predation_risk_by_prey[prey.name] = max(20, new_risk - 35)

        if incident_count > 0:
            for visitor in self._visitors:
                visitor.adjust_satisfaction(-18, "predation incident")
            events.append("😨 Visitors were distressed by predator/prey incidents.")

        return events
    
    # ============ DAY CYCLE ============
    
    def advance_day(self) -> Dict[str, Any]:
        """
        Advance to the next day. Returns a report of what happened.
        """
        self._daily_events.clear()
        report = {
            "day": self._day,
            "events": [],
            "deaths": [],
            "births": [],
            "revenue": 0.0,
            "expenses": 0.0,
            "visitors": 0,
            "donations": 0.0
        }
        
        # === MORNING ===
        self._event_manager.emit(EventTypes.DAY_START, self, f"Day {self._day} begins!")

        # Add a new mission every 3 days (missions stack).
        periodic_mission = self._add_periodic_mission_if_due()
        if periodic_mission:
            report["events"].append(f"📋 New Mission Available: {periodic_mission.title}")

        # Mission tracking phase 1 (KEEP_HAPPY only, before daily stat decay).
        # This evaluates if happiness requirements were met at the end of the previous day.
        if self._active_missions:
            self.update_mission_progress(include_types={MissionType.KEEP_HAPPY})
            mission_events, mission_births = self._resolve_active_missions()
            if mission_births:
                report["births"].extend(mission_births)
            if mission_events:
                report["events"].extend(mission_events)
        
        # Generate visitors
        num_visitors = self.generate_daily_visitors()
        report["visitors"] = num_visitors
        
        # Collect tickets
        ticket_revenue = self.collect_ticket_revenue()
        report["revenue"] += ticket_revenue

        # Daily random sickness checks
        illness_events = self._process_daily_sickness_events()
        if illness_events:
            report["events"].extend(illness_events)
        
        # === MIDDAY ===
        # Update all animals (this will decrease hunger/happiness)
        for animal in list(self._animals.values()):
            if animal.is_alive:
                animal.daily_update()
                
                # Check for death
                if not animal.is_alive:
                    report["deaths"].append(animal.name)
                    self._animals_died += 1
                    self._event_manager.emit(
                        EventTypes.ANIMAL_DEATH, 
                        animal,
                        f"{animal.name} has passed away"
                    )
                    # Visitors get upset
                    for v in self._visitors:
                        v.adjust_satisfaction(-10, "animal death")
        
        # Update enclosures
        for enclosure in self._enclosures.values():
            enclosure.daily_update()
            if enclosure.is_dirty:
                # Dirty enclosures upset visitors
                for v in self._visitors:
                    v.adjust_satisfaction(-3, "dirty enclosure")

        predation_events = self._process_predation_risk_events(report)
        if predation_events:
            report["events"].extend(predation_events)

        
        # Visitors view animals
        for visitor in self._visitors:
            animals_list = [a for a in self._animals.values() if a.is_alive]
            if animals_list:
                # View 2-4 random animals
                to_view = random.sample(
                    animals_list, 
                    min(random.randint(2, 4), len(animals_list))
                )
                for animal in to_view:
                    visitor.view_animal(animal)
        
        # Process random events
        event_result = self._process_random_events()
        if event_result:
            report["events"].append(event_result)
        
        # === EVENING ===
        # Collect donations
        donations = self.collect_donations()
        report["donations"] = donations
        report["revenue"] += donations
        
        # Pay staff
        wages = self.pay_staff_wages()
        report["expenses"] += wages

        # Mission tracking phase 2 (non-happiness missions, after daily visitor/revenue changes).
        if self._active_missions:
            self.update_mission_progress(
                include_types={
                    MissionType.BREED_ANIMALS,
                    MissionType.VISITOR_COUNT,
                    MissionType.PROFIT_TARGET,
                    MissionType.BUILD_ENCLOSURES,
                }
            )
            mission_events, mission_births = self._resolve_active_missions()
            if mission_births:
                report["births"].extend(mission_births)
            if mission_events:
                report["events"].extend(mission_events)
        
        # Reset keeper actions
        for keeper in self._keepers.values():
            keeper.reset_daily_actions()
        
        # Tick mission timers (days remaining) at end of day
        for mission in self._active_missions:
            mission.tick_day()
        
        # Generate visitor reviews
        visitor_count_for_reviews = len(self._visitors)
        if self._day > 1 and visitor_count_for_reviews > 0:
            daily_reviews = generate_reviews(
                self._animals,
                self._day,
                visitor_count=visitor_count_for_reviews
            )
        else:
            daily_reviews = []
        self._reviews.extend(daily_reviews)
        report["reviews"] = daily_reviews
        
        # Update reputation based on all reviews
        self._reputation = calculate_reputation_from_reviews(self._reviews)
        
        # Advance day counter
        self._day += 1
        
        self._event_manager.emit(EventTypes.DAY_END, self, f"Day {self._day - 1} ends")
        
        return report

    def _process_daily_sickness_events(self) -> List[str]:
        """Process random sickness events for healthy animals."""
        events: List[str] = []
        for animal in self._animals.values():
            if not animal.is_alive or animal.is_sick:
                continue

            if random.random() < self.DAILY_SICKNESS_CHANCE and animal.become_sick():
                msg = f"🤒 {animal.name} the {animal.species} has fallen ill!"
                events.append(msg)
                self._event_manager.emit(EventTypes.ANIMAL_SICK, animal, msg)

        return events
    
    def _process_random_events(self) -> Optional[str]:
        """Process random events. Returns event description if one occurred."""
        roll = random.random()
        
        # Heatwave (10%)
        if roll < 0.10:
            for animal in self._animals.values():
                if animal.is_alive:
                    animal.happiness = animal.happiness - 10
            self._budget -= 200  # Extra water costs
            self._event_manager.emit(
                EventTypes.RANDOM_EVENT, 
                None, 
                "Heatwave hits the zoo!"
            )
            return "🌡️ Heatwave! All animals lost happiness, water bills +$200"
        
        # VIP Visitor (5%)
        elif roll < 0.15:
            if self.average_visitor_satisfaction > 70:
                self._budget += 500
                self._total_revenue += 500
                self._event_manager.emit(
                    EventTypes.RANDOM_EVENT, 
                    None, 
                    "VIP visitor donated $500!"
                )
                return "🌟 VIP Visitor donated $500!"
        
        # Conservation Grant (5%)
        elif roll < 0.20:
            if self.average_animal_welfare > 80:
                self._budget += 1000
                self._total_revenue += 1000
                self._event_manager.emit(
                    EventTypes.RANDOM_EVENT, 
                    None, 
                    "Conservation grant awarded!"
                )
                return "🏆 Conservation Grant: +$1000 for excellent animal welfare!"
        
        # School Excursion (15%)
        elif roll < 0.35:
            bonus_visitors = int(len(self._visitors) * 0.5)
            for i in range(bonus_visitors):
                visitor = Visitor(
                    f"student_{self._day}_{i}", 
                    f"Student {i+1}", 
                    TicketType.CHILD
                )
                self._visitors.append(visitor)
            self._total_visitors_served += bonus_visitors

            # School visitors also expand the Feeding Frenzy toss pool.
            self._feeding_frenzy_attempts_total += bonus_visitors
            self._feeding_frenzy_attempts_remaining += bonus_visitors

            bonus_revenue = bonus_visitors * TicketType.CHILD.base_price * 0.5  # Discounted
            self._budget += bonus_revenue
            self._total_revenue += bonus_revenue
            return f"🎒 School Excursion! +{bonus_visitors} student visitors"
        
        return None
    
    def _is_breeding_eligible(self, animal: Animal) -> bool:
        """Check if an animal can be considered for breeding."""
        return (
            animal.is_alive
            and not animal.is_sick
            and animal.health >= self.BREEDING_MIN_HEALTH
            and animal.happiness >= self.BREEDING_MIN_HAPPINESS
        )

    def _species_on_breeding_cooldown(self, species: str) -> bool:
        """Return True if species has bred too recently."""
        last_bred_day = self._species_last_bred_day.get(species)
        if last_bred_day is None:
            return False
        return (self._day - last_bred_day) < self.BREEDING_COOLDOWN_DAYS

    def _generate_unique_baby_name(self, species: str) -> str:
        """Generate a unique baby name for the given species."""
        suffix = self._animals_born + 1
        while True:
            candidate = f"Baby {species} #{suffix}"
            if candidate not in self._animals:
                return candidate
            suffix += 1

    def _breed_animals_after_mission(self) -> tuple[List[str], List[str]]:
        """
        Trigger breeding as a mission-completion reward.

        Eligibility rules:
        - pair of same species
        - both healthy and happy
        - in the same enclosure
        - enclosure has free capacity
        - species is not on cooldown
        """
        births: List[str] = []
        events: List[str] = []

        for enclosure in self._enclosures.values():
            if enclosure.is_full:
                continue

            eligible_by_species: Dict[str, List[Animal]] = {}
            for animal in enclosure.animals:
                if not self._is_breeding_eligible(animal):
                    continue
                eligible_by_species.setdefault(animal.species, []).append(animal)

            for species, candidates in eligible_by_species.items():
                if len(candidates) < 2:
                    continue
                if self._species_on_breeding_cooldown(species):
                    continue
                if enclosure.is_full:
                    continue

                baby_name = self._generate_unique_baby_name(species)
                animal_type = species.lower().replace(" ", "_")
                try:
                    baby = AnimalFactory.create_animal(
                        animal_type,
                        name=baby_name,
                        age=0,
                        gender=random.choice(["male", "female"]),
                    )
                except (TypeError, ValueError):
                    continue

                try:
                    enclosure.add_animal(baby)
                except (HabitatCapacityExceededError, InvalidHabitatError):
                    continue

                self._animals[baby_name] = baby
                self._animals_born += 1
                self._species_last_bred_day[species] = self._day

                births.append(baby_name)
                event_msg = (
                    f"🍼 Your {species} pair in {enclosure.name} welcomed {baby_name}!"
                )
                events.append(event_msg)
                self._event_manager.emit(EventTypes.ANIMAL_BIRTH, baby, event_msg)

        return births, events
    
    # ============ REPORTS ============
    
    def get_daily_report(self) -> Dict[str, Any]:
        """Get a summary report for the current day."""
        return {
            "day": self._day,
            "budget": self._budget,
            "animal_count": self.animal_count,
            "species_diversity": self.species_diversity,
            "sick_animals": self.sick_animal_count,
            "hungry_animals": self.hungry_animal_count,
            "enclosure_count": len(self._enclosures),
            "dirty_enclosures": len([
                e for e in self._enclosures.values() if e.is_dirty
            ]),
            "visitor_count": len(self._visitors),
            "avg_satisfaction": self.average_visitor_satisfaction,
            "avg_welfare": self.average_animal_welfare,
            "keeper_count": len(self._keepers),
            "food_stock": self._food_stock.copy(),
            "medicine_stock": self._medicine_stock.copy(),
            "total_revenue": self._total_revenue,
            "total_expenses": self._total_expenses,
            "animals_died": self._animals_died,
            "animals_born": self._animals_born
        }
    
    def get_alerts(self) -> List[str]:
        """Get current alerts/warnings."""
        alerts = []
        
        # Hungry animals
        hungry = [a.name for a in self._animals.values() if a.is_alive and a.is_hungry]
        if hungry:
            alerts.append(f"🔴 {len(hungry)} animal(s) hungry: {', '.join(hungry[:3])}")
        
        # Sick animals
        sick = [a.name for a in self._animals.values() if a.is_alive and a.is_sick]
        if sick:
            alerts.append(f"🏥 {len(sick)} animal(s) sick: {', '.join(sick[:3])}")
        
        # Dirty enclosures
        dirty = [e.name for e in self._enclosures.values() if e.is_dirty]
        if dirty:
            alerts.append(f"🧹 {len(dirty)} enclosure(s) need cleaning")
        
        # Low food
        for food_type, qty in self._food_stock.items():
            if qty < 10:
                alerts.append(f"📦 Low stock: {food_type} ({qty} remaining)")
        
        # Low budget
        if self._budget < 500:
            alerts.append(f"💰 Low budget: ${self._budget:.2f}")

        # High predation risk
        high_risk = [
            name
            for name, risk in self._predation_risk_by_platypus.items()
            if (
                risk >= self.PREDATION_HIGH_RISK_THRESHOLD
                and name in self._animals
                and self._animals[name].is_alive
                and self._animals[name].species == "Platypus"
            )
        ]
        devil_high_risk = [
            name
            for name, risk in self._outback_predation_risk_by_prey.items()
            if (
                risk >= self.PREDATION_HIGH_RISK_THRESHOLD
                and name in self._animals
                and self._animals[name].is_alive
                and self._animals[name].species != "TasmanianDevil"
            )
        ]
        critical_risk_animals = list(dict.fromkeys(high_risk + devil_high_risk))
        if critical_risk_animals:
            alerts.append(
                f"🚨 Predation risk critical for {len(critical_risk_animals)} animal(s): "
                f"{', '.join(critical_risk_animals[:3])}"
            )
        
        return alerts
    
    # ============ SERIALISATION ============
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialise zoo state for saving."""
        return {
            "name": self._name,
            "budget": self._budget,
            "day": self._day,
            "ticket_modifier": self._ticket_modifier,
            "food_stock": self._food_stock,
            "medicine_stock": self._medicine_stock,
            "total_revenue": self._total_revenue,
            "total_expenses": self._total_expenses,
            "animals_died": self._animals_died,
            "animals_born": self._animals_born,
            "total_visitors_served": self._total_visitors_served,
            "species_last_bred_day": self._species_last_bred_day,
            "enclosures": {k: v.to_dict() for k, v in self._enclosures.items()},
            "animals": {k: v.to_dict() for k, v in self._animals.items()},
            "keepers": {k: v.to_dict() for k, v in self._keepers.items()},
            "map_grid": [[tile.to_dict() for tile in row] for row in self._map_grid],
            "current_mission": self.current_mission.to_dict() if self.current_mission else None,
            "active_missions": [mission.to_dict() for mission in self._active_missions],
            "consecutive_happy_days": self._consecutive_happy_days,
            "predation_risk_by_platypus": self._predation_risk_by_platypus,
            "outback_predation_risk_by_prey": self._outback_predation_risk_by_prey,
            
            # Reviews and reputation
            "reviews": [r.to_dict() for r in self._reviews],
            "reputation": self._reputation,

            # Feeding Frenzy state
            "feeding_frenzy_pool_day": self._feeding_frenzy_pool_day,
            "feeding_frenzy_attempts_total": self._feeding_frenzy_attempts_total,
            "feeding_frenzy_attempts_remaining": self._feeding_frenzy_attempts_remaining,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Zoo:
        """Deserialise zoo from saved data."""
        zoo = cls(name=data["name"], budget=data["budget"])
        zoo._day = data["day"]
        zoo._ticket_modifier = data.get("ticket_modifier", 1.0)
        zoo._food_stock = data["food_stock"]
        zoo._medicine_stock = data["medicine_stock"]
        zoo._total_revenue = data["total_revenue"]
        zoo._total_expenses = data["total_expenses"]
        zoo._animals_died = data["animals_died"]
        zoo._animals_born = data["animals_born"]
        zoo._total_visitors_served = data.get("total_visitors_served", 0)
        zoo._species_last_bred_day = {
            species: int(day)
            for species, day in data.get("species_last_bred_day", {}).items()
        }
        
        # Reconstruct enclosures
        for enc_id, enc_data in data["enclosures"].items():
            enc = Enclosure.from_dict(enc_data)
            zoo._enclosures[enc_id] = enc
        
        # Reconstruct animals
        for name, animal_data in data["animals"].items():
            animal_class = animal_data.get("class", animal_data.get("species"))
            animal = AnimalFactory.create_animal(
                animal_class.lower().replace(" ", "_"),
                name=animal_data["name"],
                age=animal_data["age"],
                gender=animal_data.get("gender", "unknown")
            )
            # Restore state
            animal._health = animal_data["health"]
            animal._hunger = animal_data["hunger"]
            animal._happiness = animal_data["happiness"]
            animal._is_alive = animal_data["is_alive"]
            animal._is_sick = animal_data.get("is_sick", False)
            animal._sick_days = animal_data.get("sick_days", 0)
            zoo._animals[name] = animal
            
            # Add to enclosure if specified
            enc_id = animal_data.get("enclosure_id")
            if enc_id and enc_id in zoo._enclosures:
                zoo._enclosures[enc_id]._animals.append(animal)
        
        # Reconstruct keepers
        for emp_id, keeper_data in data["keepers"].items():
            keeper = ZooKeeper.from_dict(keeper_data)
            zoo._keepers[emp_id] = keeper
            # Check if this is the mission keeper
            if keeper.specialty == Specialty.GENERAL and not zoo._mission_keeper:
                zoo._mission_keeper = keeper
        
        # Reconstruct map grid if present
        if "map_grid" in data:
            zoo._map_grid = [
                [MapTile.from_dict(tile_data) for tile_data in row]
                for row in data["map_grid"]
            ]
            
            # Relink enclosure references in map tiles
            for row in zoo._map_grid:
                for tile in row:
                    if tile.tile_type == TileType.ENCLOSURE and tile.item_id:
                        # Try to link to actual enclosure
                        if tile.item_id in zoo._enclosures:
                            tile.enclosure_ref = zoo._enclosures[tile.item_id]
        
        # Restore missions (new stacked format first, then backward-compatible single mission)
        if "active_missions" in data and data["active_missions"]:
            from .mission import Mission
            zoo._active_missions = [Mission.from_dict(m) for m in data["active_missions"]]
        elif "current_mission" in data and data["current_mission"]:
            from .mission import Mission
            zoo._active_missions = [Mission.from_dict(data["current_mission"])]
        zoo._consecutive_happy_days = data.get("consecutive_happy_days", {})
        zoo._predation_risk_by_platypus = {
            name: max(0, min(100, int(risk)))
            for name, risk in data.get("predation_risk_by_platypus", {}).items()
            if (
                name in zoo._animals
                and zoo._animals[name].species == "Platypus"
                and zoo._animals[name].is_alive
            )
        }
        zoo._outback_predation_risk_by_prey = {
            name: max(0, min(100, int(risk)))
            for name, risk in data.get("outback_predation_risk_by_prey", {}).items()
            if (
                name in zoo._animals
                and zoo._animals[name].species != "TasmanianDevil"
                and zoo._animals[name].is_alive
            )
        }
        
        # Restore reviews and reputation
        if "reviews" in data:
            from .review import Review
            zoo._reviews = [Review.from_dict(r) for r in data["reviews"]]
        zoo._reputation = data.get("reputation", 50.0)

        # Restore Feeding Frenzy state
        zoo._feeding_frenzy_pool_day = data.get("feeding_frenzy_pool_day", zoo._day)
        zoo._feeding_frenzy_attempts_total = max(
            0,
            int(data.get("feeding_frenzy_attempts_total", 0))
        )
        zoo._feeding_frenzy_attempts_remaining = max(
            0,
            min(
                zoo._feeding_frenzy_attempts_total,
                int(data.get("feeding_frenzy_attempts_remaining", zoo._feeding_frenzy_attempts_total))
            )
        )
        
        return zoo


# ============ SAVE/LOAD FUNCTIONS ============

def save_game(zoo: Zoo, filepath: Path) -> None:
    """Save game to JSON file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(zoo.to_dict(), f, indent=2, default=str)


def load_game(filepath: Path) -> Zoo:
    """Load game from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return Zoo.from_dict(data)


def create_default_zoo() -> Zoo:
    """
    Create a new zoo with a mission-based starter setup.
    
    Generates a random starter mission and creates ONE enclosure
    based on the mission's requirements. Adds starter animals for the mission.
    """
    zoo = Zoo("OzZoo", budget=10000.0)
    
    # Generate random starter mission
    mission = generate_starter_mission(difficulty="easy")
    zoo.start_mission(mission)
    
    # Create mission keeper who gives the mission
    mission_keeper = generate_random_keeper("keeper_mission")
    zoo._mission_keeper = mission_keeper
    zoo.hire_keeper(mission_keeper, signing_bonus=0)  # Free starter keeper
    
    # Determine required habitat from mission
    required_habitat = get_mission_animal_habitat(mission)
    if not required_habitat:
        required_habitat = "eucalyptus_grove"  # Fallback
    
    # Build ONE starting enclosure based on mission
    enc_id = f"enc_starter_1"
    enclosure_name_map = {
        "eucalyptus_grove": "Koala Corner",
        "outback_savanna": "Outback Plains",
        "billabong": "Crocodile Creek",
        "rainforest_aviary": "Bird Paradise",
        "reptile_house": "Reptile Realm"
    }
    enc_name = enclosure_name_map.get(required_habitat, "Starter Enclosure")
    zoo.add_enclosure(create_enclosure(required_habitat, enc_id, name=enc_name))
    
    # Add starter animals for the mission
    # Extract count from mission description
    import re
    match = re.search(r'Keep (\d+)', mission.description)
    required_count = int(match.group(1)) if match else 2
    
    # Animal names for different species (keys match species names from mission templates)
    animal_names = {
        "Koala": ["Blinky", "Bella", "Blue", "Bonnie", "Banjo"],
        "Kangaroo": ["Skippy", "Sheila", "Skip", "Sandy", "Rusty"],
        "Kookaburra": ["Kookie", "Kev", "Kerry", "Kayla", "Kai"],
        "SaltwaterCroc": ["Chomper", "Crikey", "Croc", "Cassie", "Clyde"],
        "Wombat": ["Wally", "Wendy", "Winston", "Willow", "Wade"],
        "Platypus": ["Perry", "Paddles", "Pearl", "Phoenix", "Pip"],
        "Emu": ["Eddie", "Emma", "Earl", "Ellie", "Eric"],
        "WedgeTailedEagle": ["Aquila", "Sky", "Arrow", "Athena", "Apollo"],
        "TasmanianDevil": ["Taz", "Tara", "Thor", "Tilly", "Tex"],
        "Echidna": ["Spike", "Snuffle", "Spiky", "Sophie", "Sam"],
        "FrilledLizard": ["Frilly", "Fern", "Flash", "Flora", "Finn"],
    }
    
    # Try both species name (from mission) and lowercase (for factory)
    names = animal_names.get(mission.target_animal, ["Animal1", "Animal2", "Animal3", "Animal4", "Animal5"])
    
    # Normalise animal type for factory (lowercase with underscores)
    factory_type = mission.target_animal.lower()
    if factory_type == "saltwatercroc":
        factory_type = "saltwater_croc"
    elif factory_type == "wedgetailedeagle":
        factory_type = "wedge_tailed_eagle"
    elif factory_type == "tasmaniandevil":
        factory_type = "tasmanian_devil"
    elif factory_type == "frilledlizard":
        factory_type = "frilled_lizard"
    
    genders = ["male", "female"]
    
    for i in range(min(required_count, len(names))):
        try:
            zoo.purchase_animal(
                factory_type,
                names[i],
                random.randint(2, 5),
                enc_id,
                genders[i % 2]
            )
        except Exception as e:
            print(f"Could not add starter animal: {e}")
    
    # Pre-populate the map with the starter enclosure
    _populate_mission_starter_map(zoo, required_habitat, enc_id)
    
    return zoo


def _populate_mission_starter_map(zoo: Zoo, habitat_type: str, enclosure_id: str) -> None:
    """
    Pre-populate the map grid with a mission-based starter layout.
    
    Creates a simple starting zoo layout with ONE enclosure, basic scenery, and facilities.
    All starter items are free (no budget deduction).
    
    Args:
        zoo: The Zoo instance
        habitat_type: The habitat type of the starter enclosure
        enclosure_id: The ID of the starter enclosure
    """
    # Save current budget to restore after (starter items are free)
    original_budget = zoo._budget
    zoo._budget = 999999.0  # Temporarily set high budget
    
    # Place the single starter enclosure in the center-left area (3x3)
    enclosure_emoji_map = {
        "eucalyptus_grove": "enclosure_koala",
        "outback_savanna": "enclosure_outback",
        "billabong": "enclosure_billabong",
        "rainforest_aviary": "enclosure_aviary",
        "reptile_house": "enclosure_reptile"
    }
    enc_item_id = enclosure_emoji_map.get(habitat_type, "enclosure_koala")
    
    # Place 3x3 enclosure at (2,2) to (4,4)
    for x in range(2, 5):
        for y in range(2, 5):
            zoo.place_item(x, y, enc_item_id, TileType.ENCLOSURE, zoo._enclosures.get(enclosure_id))
    
    # Add minimal scenery around the zoo
    # Trees in corners
    zoo.place_item(0, 0, "tree", TileType.SCENERY)
    zoo.place_item(9, 0, "tree", TileType.SCENERY)
    zoo.place_item(0, 9, "tree", TileType.SCENERY)
    zoo.place_item(9, 9, "tree", TileType.SCENERY)
    
    # Bushes
    zoo.place_item(1, 0, "bush", TileType.SCENERY)
    zoo.place_item(8, 0, "bush", TileType.SCENERY)
    
    # Flowers near enclosure
    zoo.place_item(5, 2, "flowers", TileType.SCENERY)
    zoo.place_item(5, 3, "flowers", TileType.SCENERY)
    
    # Water feature
    zoo.place_item(6, 6, "water", TileType.SCENERY)
    
    # Basic visitor facilities at entrance (bottom)
    zoo.place_item(4, 8, "ticket-booth", TileType.SHOP)  # Entrance
    zoo.place_item(3, 8, "food-stall", TileType.SHOP)    # Food
    zoo.place_item(5, 8, "bench", TileType.SHOP)          # Bench
    
    # Restore original budget (starter items are free)
    zoo._budget = original_budget
    # Reset expenses to 0 since these are starter items
    zoo._total_expenses = 0.0


def _populate_starter_map(zoo: Zoo) -> None:
    """
    Pre-populate the map grid with a starter layout.
    
    Creates a nice starting zoo layout with enclosures, scenery, and facilities.
    All starter items are free (no budget deduction).
    """
    # Save current budget to restore after (starter items are free)
    original_budget = zoo._budget
    zoo._budget = 999999.0  # Temporarily set high budget
    
    # Place enclosures (representing the 5 starting enclosures)
    # Top-left: Koala Corner (2x2)
    zoo.place_item(1, 1, "enclosure_koala", TileType.ENCLOSURE, zoo._enclosures.get("enc_euc_1"))
    zoo.place_item(2, 1, "enclosure_koala", TileType.ENCLOSURE, zoo._enclosures.get("enc_euc_1"))
    zoo.place_item(1, 2, "enclosure_koala", TileType.ENCLOSURE, zoo._enclosures.get("enc_euc_1"))
    zoo.place_item(2, 2, "enclosure_koala", TileType.ENCLOSURE, zoo._enclosures.get("enc_euc_1"))
    
    # Top-right: Outback Plains (2x2)
    zoo.place_item(6, 1, "enclosure_outback", TileType.ENCLOSURE, zoo._enclosures.get("enc_out_1"))
    zoo.place_item(7, 1, "enclosure_outback", TileType.ENCLOSURE, zoo._enclosures.get("enc_out_1"))
    zoo.place_item(6, 2, "enclosure_outback", TileType.ENCLOSURE, zoo._enclosures.get("enc_out_1"))
    zoo.place_item(7, 2, "enclosure_outback", TileType.ENCLOSURE, zoo._enclosures.get("enc_out_1"))
    
    # Middle-left: Bird Paradise (2x2)
    zoo.place_item(1, 5, "enclosure_aviary", TileType.ENCLOSURE, zoo._enclosures.get("enc_avi_1"))
    zoo.place_item(2, 5, "enclosure_aviary", TileType.ENCLOSURE, zoo._enclosures.get("enc_avi_1"))
    zoo.place_item(1, 6, "enclosure_aviary", TileType.ENCLOSURE, zoo._enclosures.get("enc_avi_1"))
    zoo.place_item(2, 6, "enclosure_aviary", TileType.ENCLOSURE, zoo._enclosures.get("enc_avi_1"))
    
    # Middle-right: Crocodile Creek (2x2)
    zoo.place_item(6, 5, "enclosure_billabong", TileType.ENCLOSURE, zoo._enclosures.get("enc_bil_1"))
    zoo.place_item(7, 5, "enclosure_billabong", TileType.ENCLOSURE, zoo._enclosures.get("enc_bil_1"))
    zoo.place_item(6, 6, "enclosure_billabong", TileType.ENCLOSURE, zoo._enclosures.get("enc_bil_1"))
    zoo.place_item(7, 6, "enclosure_billabong", TileType.ENCLOSURE, zoo._enclosures.get("enc_bil_1"))
    
    # Bottom-center: Reptile Realm (2x2)
    zoo.place_item(4, 7, "enclosure_reptile", TileType.ENCLOSURE, zoo._enclosures.get("enc_rep_1"))
    zoo.place_item(5, 7, "enclosure_reptile", TileType.ENCLOSURE, zoo._enclosures.get("enc_rep_1"))
    zoo.place_item(4, 8, "enclosure_reptile", TileType.ENCLOSURE, zoo._enclosures.get("enc_rep_1"))
    zoo.place_item(5, 8, "enclosure_reptile", TileType.ENCLOSURE, zoo._enclosures.get("enc_rep_1"))
    
    # Add scenery around the zoo
    # Trees
    zoo.place_item(0, 0, "tree", TileType.SCENERY)
    zoo.place_item(3, 0, "tree", TileType.SCENERY)
    zoo.place_item(9, 0, "tree", TileType.SCENERY)
    zoo.place_item(0, 3, "tree", TileType.SCENERY)
    zoo.place_item(9, 3, "tree", TileType.SCENERY)
    zoo.place_item(0, 7, "tree", TileType.SCENERY)
    zoo.place_item(9, 7, "tree", TileType.SCENERY)
    zoo.place_item(3, 9, "tree", TileType.SCENERY)
    zoo.place_item(6, 9, "tree", TileType.SCENERY)
    
    # Bushes
    zoo.place_item(0, 1, "bush", TileType.SCENERY)
    zoo.place_item(9, 1, "bush", TileType.SCENERY)
    zoo.place_item(0, 8, "bush", TileType.SCENERY)
    zoo.place_item(9, 8, "bush", TileType.SCENERY)
    
    # Flowers
    zoo.place_item(4, 0, "flowers", TileType.SCENERY)
    zoo.place_item(5, 0, "flowers", TileType.SCENERY)
    
    # Water feature in center
    zoo.place_item(4, 4, "water", TileType.SCENERY)
    
    # Visitor facilities
    zoo.place_item(0, 9, "ticket-booth", TileType.SHOP)  # Entrance (bottom-left)
    zoo.place_item(1, 9, "food-stall", TileType.SHOP)    # Food nearby
    zoo.place_item(8, 9, "restroom", TileType.SHOP)      # Restroom (bottom-right)
    zoo.place_item(9, 9, "bench", TileType.SHOP)          # Bench for visitors
    
    # Restore original budget (starter items are free)
    zoo._budget = original_budget
    # Reset expenses to 0 since these are starter items
    zoo._total_expenses = 0.0
