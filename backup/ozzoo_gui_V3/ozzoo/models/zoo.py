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
from .mission import Mission, generate_starter_mission, get_mission_animal_habitat
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
        self._current_mission: Optional[Mission] = None
        self._mission_keeper: Optional[ZooKeeper] = None
        self._consecutive_happy_days: Dict[str, int] = {}  # animal_name -> days happy
        
        # Review and reputation system
        self._reviews: List[Review] = []
        self._reputation = 50.0  # 0-100 scale, starts neutral
    
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
    def map_grid(self) -> List[List[MapTile]]:
        """Get the zoo map grid."""
        return self._map_grid
    
    @property
    def current_mission(self) -> Optional[Mission]:
        """Get the current active mission."""
        return self._current_mission
    
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
        return True
    
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
    
    def start_mission(self, mission: Mission) -> None:
        """
        Start a new mission.
        
        Args:
            mission: Mission to activate
        """
        self._current_mission = mission
        self._consecutive_happy_days = {}
    
    def update_mission_progress(self) -> None:
        """Update mission progress based on current zoo state."""
        if not self._current_mission or self._current_mission.is_complete or self._current_mission.is_failed:
            return
        
        from .mission import MissionType
        
        if self._current_mission.mission_type == MissionType.KEEP_HAPPY:
            # Count animals of target type that are happy (70+ happiness)
            target_type = self._current_mission.target_animal
            happy_animals = [
                a for a in self._animals.values()
                if a.is_alive and a.species == target_type and a.happiness >= 70
            ]
            
            # Check if we have enough happy animals to satisfy the mission requirement
            required_count = self._current_mission.target_value
            requirements_met = len(happy_animals) >= required_count
            
            if requirements_met:
                # All requirements met today - increment the mission progress
                # Mission progress = consecutive days where requirements are satisfied
                self._current_mission.update_progress(1)
            else:
                # Requirements NOT met - reset progress to 0
                self._current_mission.set_progress(0)
            
            # Check if mission is complete
            # Need required_days consecutive days where all requirements are met
            required_days = getattr(self._current_mission, 'required_days', 5)
            if self._current_mission.current_progress >= required_days:
                self._current_mission.is_complete = True
            
            # Track individual animal consecutive days (for display purposes)
            for animal in happy_animals:
                if animal.name not in self._consecutive_happy_days:
                    self._consecutive_happy_days[animal.name] = 0
                self._consecutive_happy_days[animal.name] += 1
            
            # Remove animals that are no longer happy or dead
            for animal_name in list(self._consecutive_happy_days.keys()):
                if animal_name not in [a.name for a in happy_animals]:
                    self._consecutive_happy_days[animal_name] = 0
    
    def complete_mission(self) -> tuple[bool, str]:
        """
        Complete the current mission and award rewards.
        
        Returns:
            Tuple of (success, message)
        """
        if not self._current_mission:
            return False, "No active mission."
        
        if not self._current_mission.is_complete:
            return False, "Mission not yet complete."
        
        # Award rewards
        self._budget += self._current_mission.reward.money
        # Note: reputation could be tracked if we add a reputation system
        
        msg = (
            f"🎉 Mission Complete: {self._current_mission.title}!\n"
            f"Rewards: {self._current_mission.reward.description}"
        )
        
        # Clear mission
        self._current_mission = None
        self._consecutive_happy_days = {}
        
        return True, msg
    
    def check_mission_failure(self) -> bool:
        """
        Check if mission has failed.
        
        Returns:
            True if mission failed
        """
        if self._current_mission:
            return self._current_mission.is_failed
        return False
    
    # ============ VISITORS ============
    
    def generate_daily_visitors(self) -> int:
        """Generate visitors for the day based on zoo appeal."""
        # Base visitors + bonus for welfare + penalty for sick animals
        base_visitors = 20 + (self._day // 5) * 5  # Grows over time
        welfare_bonus = int(self.average_animal_welfare / 10)
        sick_penalty = self.sick_animal_count * 2
        
        num_visitors = max(5, base_visitors + welfare_bonus - sick_penalty)
        
        self._visitors.clear()
        for i in range(num_visitors):
            visitor = generate_random_visitor(f"v_{self._day}_{i}")
            self._visitors.append(visitor)
        
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
        
        # Generate visitors
        num_visitors = self.generate_daily_visitors()
        report["visitors"] = num_visitors
        
        # Collect tickets
        ticket_revenue = self.collect_ticket_revenue()
        report["revenue"] += ticket_revenue
        
        # === MIDDAY ===
        # Update all animals
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
        
        # Check for breeding
        birth = self._check_breeding()
        if birth:
            report["births"].append(birth)
        
        # === EVENING ===
        # Collect donations
        donations = self.collect_donations()
        report["donations"] = donations
        report["revenue"] += donations
        
        # Pay staff
        wages = self.pay_staff_wages()
        report["expenses"] += wages
        
        # Reset keeper actions
        for keeper in self._keepers.values():
            keeper.reset_daily_actions()
        
        # Mission tracking
        if self._current_mission:
            self._current_mission.tick_day()
            self.update_mission_progress()
            
            if self._current_mission.is_complete:
                success, msg = self.complete_mission()
                if success:
                    report["events"].append(msg)
                    # Generate new mission
                    self._current_mission = generate_starter_mission("easy")
                    report["events"].append(
                        f"📋 New Mission Available: {self._current_mission.title}"
                    )
            elif self._current_mission.is_failed:
                report["events"].append(
                    f"❌ Mission Failed: {self._current_mission.title}"
                )
                # Clear failed mission and generate new one
                self._current_mission = None
                self._consecutive_happy_days = {}
                self._current_mission = generate_starter_mission("easy")
                report["events"].append(
                    f"📋 New Mission Available: {self._current_mission.title}"
                )
        
        # Generate visitor reviews
        daily_reviews = generate_reviews(self._animals, self._day)
        self._reviews.extend(daily_reviews)
        report["reviews"] = daily_reviews
        
        # Update reputation based on all reviews
        self._reputation = calculate_reputation_from_reviews(self._reviews)
        
        # Advance day counter
        self._day += 1
        
        self._event_manager.emit(EventTypes.DAY_END, self, f"Day {self._day - 1} ends")
        
        return report
    
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
            bonus_revenue = bonus_visitors * TicketType.CHILD.base_price * 0.5  # Discounted
            self._budget += bonus_revenue
            self._total_revenue += bonus_revenue
            return f"🎒 School Excursion! +{bonus_visitors} student visitors"
        
        return None
    
    def _check_breeding(self) -> Optional[str]:
        """Check if any animals breed. Returns baby name if birth occurs."""
        # Group animals by species
        species_groups: Dict[str, List[Animal]] = {}
        for animal in self._animals.values():
            if animal.is_alive and animal.can_breed:
                if animal.species not in species_groups:
                    species_groups[animal.species] = []
                species_groups[animal.species].append(animal)
        
        # Check each species for breeding pairs
        for species, animals in species_groups.items():
            if len(animals) >= 2:
                # 10% chance if conditions met
                if random.random() < 0.10:
                    parent = random.choice(animals)
                    baby_name = f"Baby {species} #{self._animals_born + 1}"
                    
                    # Create baby of same type
                    try:
                        baby = AnimalFactory.create_animal(
                            species.lower().replace(" ", "_"),
                            name=baby_name,
                            age=0,
                            gender=random.choice(["male", "female"])
                        )
                        
                        # Find enclosure
                        enclosure = self.get_enclosure_for_animal(parent)
                        if enclosure and not enclosure.is_full:
                            enclosure.add_animal(baby)
                            self._animals[baby_name] = baby
                            self._animals_born += 1
                            self._event_manager.emit(
                                EventTypes.ANIMAL_BIRTH, 
                                baby,
                                f"{baby_name} was born!"
                            )
                            return baby_name
                    except Exception:
                        pass  # Skip if creation fails
        
        return None
    
    # ============ REPORTS ============
    
    def get_daily_report(self) -> Dict[str, Any]:
        """Get a summary report for the current day."""
        return {
            "day": self._day,
            "budget": self._budget,
            "animal_count": self.animal_count,
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
            "enclosures": {k: v.to_dict() for k, v in self._enclosures.items()},
            "animals": {k: v.to_dict() for k, v in self._animals.items()},
            "keepers": {k: v.to_dict() for k, v in self._keepers.items()},
            "map_grid": [[tile.to_dict() for tile in row] for row in self._map_grid],
            "current_mission": self._current_mission.to_dict() if self._current_mission else None,
            "consecutive_happy_days": self._consecutive_happy_days,
            
            # Reviews and reputation
            "reviews": [r.to_dict() for r in self._reviews],
            "reputation": self._reputation,
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
        
        # Restore mission
        if "current_mission" in data and data["current_mission"]:
            from .mission import Mission
            zoo._current_mission = Mission.from_dict(data["current_mission"])
        zoo._consecutive_happy_days = data.get("consecutive_happy_days", {})
        
        # Restore reviews and reputation
        if "reviews" in data:
            from .review import Review
            zoo._reviews = [Review.from_dict(r) for r in data["reviews"]]
        zoo._reputation = data.get("reputation", 50.0)
        
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
    
    # Animal names for different species
    animal_names = {
        "koala": ["Blinky", "Bella", "Blue", "Bonnie", "Banjo"],
        "kangaroo": ["Skippy", "Sheila", "Skip", "Sandy", "Rusty"],
        "kookaburra": ["Kookie", "Kev", "Kerry", "Kayla", "Kai"],
        "saltwater_croc": ["Chomper", "Crikey", "Croc", "Cassie", "Clyde"],
        "wombat": ["Wally", "Wendy", "Winston", "Willow", "Wade"]
    }
    
    names = animal_names.get(mission.target_animal, ["Animal1", "Animal2", "Animal3", "Animal4", "Animal5"])
    genders = ["male", "female"]
    
    for i in range(min(required_count, len(names))):
        try:
            zoo.purchase_animal(
                mission.target_animal,
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

