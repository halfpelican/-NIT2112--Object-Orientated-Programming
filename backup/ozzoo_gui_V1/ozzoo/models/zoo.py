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
    
    def __init__(self, name: str = "OzZoo", budget: float = DEFAULT_BUDGET):
        self._name = name
        self._budget = budget
        self._day = 1
        
        # Core collections
        self._enclosures: Dict[str, Enclosure] = {}
        self._animals: Dict[str, Animal] = {}  # animal_name -> Animal
        self._visitors: List[Visitor] = []
        self._keepers: Dict[str, ZooKeeper] = {}
        
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
        """
        if enclosure_id not in self._enclosures:
            raise KeyError(f"Enclosure '{enclosure_id}' not found")
        
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
        
        food_data = FOOD_TYPES[food_type]
        total_cost = food_data["cost"] * quantity
        
        if self._budget < total_cost:
            return False, (
                f"Insufficient funds: need ${total_cost:.2f}, "
                f"have ${self._budget:.2f}"
            )
        
        self._budget -= total_cost
        self._total_expenses += total_cost
        self._food_stock[food_type] = self._food_stock.get(food_type, 0) + quantity
        
        return True, f"Purchased {quantity}x {food_data['name']} for ${total_cost:.2f}"
    
    def buy_medicine(self, medicine_type: str, quantity: int) -> tuple[bool, str]:
        """Buy medicine for the zoo."""
        if medicine_type not in MEDICINE_TYPES:
            return False, f"Unknown medicine type: {medicine_type}"
        
        med_data = MEDICINE_TYPES[medicine_type]
        total_cost = med_data["cost"] * quantity
        
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
        
        return True, f"Purchased {quantity}x {med_data['name']} for ${total_cost:.2f}"
    
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
    """Create a new zoo with default starting animals and enclosures."""
    zoo = Zoo("OzZoo", budget=10000.0)
    
    # Build starting enclosures
    zoo.add_enclosure(create_enclosure("eucalyptus_grove", "enc_euc_1", name="Koala Corner"))
    zoo.add_enclosure(create_enclosure("outback_savanna", "enc_out_1", name="Outback Plains"))
    zoo.add_enclosure(create_enclosure("billabong", "enc_bil_1", name="Crocodile Creek"))
    zoo.add_enclosure(create_enclosure("rainforest_aviary", "enc_avi_1", name="Bird Paradise"))
    zoo.add_enclosure(create_enclosure("reptile_house", "enc_rep_1", name="Reptile Realm"))
    
    # Add starting animals
    zoo.purchase_animal("koala", "Blinky", 3, "enc_euc_1", "male")
    zoo.purchase_animal("koala", "Bella", 2, "enc_euc_1", "female")
    zoo.purchase_animal("kangaroo", "Skippy", 5, "enc_out_1", "male")
    zoo.purchase_animal("kangaroo", "Sheila", 4, "enc_out_1", "female")
    zoo.purchase_animal("wombat", "Wally", 3, "enc_out_1", "male")
    zoo.purchase_animal("emu", "Eddie", 2, "enc_avi_1", "male")
    zoo.purchase_animal("saltwater_croc", "Chomper", 8, "enc_bil_1", "male")
    zoo.purchase_animal("frilled_lizard", "Frilly", 2, "enc_rep_1", "female")
    
    # Hire a starting keeper
    keeper = ZooKeeper("keeper_1", "Steve Wildman", Specialty.GENERAL)
    zoo.hire_keeper(keeper, signing_bonus=0)  # Free starting keeper
    
    return zoo
