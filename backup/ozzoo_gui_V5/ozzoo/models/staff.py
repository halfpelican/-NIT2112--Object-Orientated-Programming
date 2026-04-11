"""
OzZoo Staff Module
Contains the ZooKeeper class representing zoo employees.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, List
from enum import Enum

if TYPE_CHECKING:
    from .animal import Animal
    from .enclosure import Enclosure
    from .resources import Food, Medicine


class Specialty(Enum):
    """Zookeeper specialties with efficiency bonuses."""
    GENERAL = ("General", 1.0)
    MAMMAL_EXPERT = ("Mammal Expert", 1.3)
    BIRD_EXPERT = ("Bird Expert", 1.3)
    REPTILE_EXPERT = ("Reptile Expert", 1.3)
    VETERINARIAN = ("Veterinarian", 1.5)  # Healing bonus
    
    def __init__(self, display_name: str, efficiency: float):
        self.display_name = display_name
        self.efficiency = efficiency


class ZooKeeper:
    """
    Represents a zoo staff member who can care for animals.
    
    Zookeepers have specialties that give bonuses when working with
    certain animal types.
    
    Attributes:
        DAILY_WAGE: Base daily wage for all keepers.
        employee_id: Unique identifier for the keeper.
        name: The keeper's full name.
        specialty: The keeper's area of expertise.
        assigned_enclosures: List of enclosure IDs the keeper is responsible for.
        actions_remaining: Number of actions the keeper can still perform today.
        is_available: Whether the keeper can perform more actions today.
        daily_cost: The keeper's daily wage (affected by specialty).
    """
    
    DAILY_WAGE = 150.0  # Base daily wage in dollars
    
    def __init__(
        self,
        employee_id: str,
        name: str,
        specialty: Specialty = Specialty.GENERAL
    ):
        """
        Initialise a new ZooKeeper.
        
        Args:
            employee_id: Unique identifier for the keeper.
            name: The keeper's full name.
            specialty: The keeper's area of expertise (defaults to GENERAL).
        """
        self._employee_id = employee_id
        self._name = name
        self._specialty = specialty
        self._assigned_enclosures: List[str] = []  # List of enclosure IDs
        self._actions_today = 0
        self._max_actions = 5  # Can do 5 major actions per day
    
    # Properties
    @property
    def employee_id(self) -> str:
        """Return the keeper's unique employee ID."""
        return self._employee_id
    
    @property
    def name(self) -> str:
        """Return the keeper's name."""
        return self._name
    
    @property
    def specialty(self) -> Specialty:
        """Return the keeper's specialty."""
        return self._specialty
    
    @property
    def assigned_enclosures(self) -> List[str]:
        """Return list of enclosure IDs the keeper is assigned to."""
        return self._assigned_enclosures.copy()
    
    @property
    def actions_remaining(self) -> int:
        """Return the number of actions the keeper can still perform today."""
        return self._max_actions - self._actions_today
    
    @property
    def is_available(self) -> bool:
        """Return True if the keeper can perform more actions today."""
        return self._actions_today < self._max_actions
    
    @property
    def daily_cost(self) -> float:
        """
        Calculate daily wage (specialists cost more).
        
        Returns:
            The keeper's daily wage, modified by their specialty efficiency.
        """
        return self.DAILY_WAGE * self._specialty.efficiency
    
    def assign_enclosure(self, enclosure_id: str) -> None:
        """
        Assign keeper to an enclosure.
        
        Args:
            enclosure_id: The ID of the enclosure to assign.
        """
        if enclosure_id not in self._assigned_enclosures:
            self._assigned_enclosures.append(enclosure_id)
    
    def unassign_enclosure(self, enclosure_id: str) -> None:
        """
        Remove keeper from an enclosure.
        
        Args:
            enclosure_id: The ID of the enclosure to unassign.
        """
        if enclosure_id in self._assigned_enclosures:
            self._assigned_enclosures.remove(enclosure_id)
    
    def feed_animal(self, animal: Animal, food: Food) -> tuple[bool, str]:
        """
        Feed an animal.
        
        Specialists get bonus efficiency when feeding their specialty type.
        Uses one action.
        
        Args:
            animal: The animal to feed.
            food: The food to give the animal.
        
        Returns:
            A tuple of (success, message) indicating the result.
        """
        if not self.is_available:
            return False, f"{self._name} has no actions remaining today."
        
        self._actions_today += 1
        
        # Check if food matches diet
        if not animal.feed(food):
            return False, f"{animal.name} doesn't eat {food.food_type}!"
        
        # Apply specialty bonus
        bonus_msg = ""
        if self._matches_specialty(animal):
            animal.happiness = min(100, animal.happiness + 5)  # Extra happiness
            bonus_msg = " (Specialty bonus applied!)"
        
        return True, f"{self._name} fed {animal.name} with {food.name}.{bonus_msg}"
    
    def clean_enclosure(self, enclosure: Enclosure) -> tuple[bool, str]:
        """
        Clean an enclosure.
        
        Uses one action.
        
        Args:
            enclosure: The enclosure to clean.
        
        Returns:
            A tuple of (success, message) indicating the result.
        """
        if not self.is_available:
            return False, f"{self._name} has no actions remaining today."
        
        self._actions_today += 1
        result = enclosure.clean()
        return True, f"{self._name} cleaned {enclosure.name}. {result}"
    
    def heal_animal(self, animal: Animal, medicine: Medicine) -> tuple[bool, str]:
        """
        Administer medicine to a sick animal.
        
        Veterinarians get a healing bonus.
        Uses one action.
        
        Args:
            animal: The animal to treat.
            medicine: The medicine to administer.
        
        Returns:
            A tuple of (success, message) indicating the result.
        """
        if not self.is_available:
            return False, f"{self._name} has no actions remaining today."
        
        if not medicine.can_treat(animal.get_animal_type()):
            return False, f"{medicine.name} cannot treat {animal.get_animal_type()}s!"

        if not animal.is_alive:
            return False, f"{animal.name} is no longer alive."

        if not animal.is_sick:
            return False, f"{animal.name} is not sick."
        
        self._actions_today += 1
        
        # Calculate healing amount
        healing = medicine.healing
        if self._specialty == Specialty.VETERINARIAN:
            healing = int(healing * 1.5)
        
        animal.heal(healing)
        animal.cure_sickness()

        return True, (
            f"{self._name} treated {animal.name} with {medicine.name}. "
            f"Health +{healing}, sickness cured."
        )
    
    def _matches_specialty(self, animal: Animal) -> bool:
        """
        Check if keeper's specialty matches the animal type.
        
        Args:
            animal: The animal to check against.
        
        Returns:
            True if the keeper's specialty matches the animal type.
        """
        animal_type = animal.get_animal_type()
        if self._specialty == Specialty.MAMMAL_EXPERT and animal_type == "mammal":
            return True
        if self._specialty == Specialty.BIRD_EXPERT and animal_type == "bird":
            return True
        if self._specialty == Specialty.REPTILE_EXPERT and animal_type == "reptile":
            return True
        return False
    
    def reset_daily_actions(self) -> None:
        """Reset action count at start of new day."""
        self._actions_today = 0
    
    def get_status(self) -> dict:
        """
        Return current status as dictionary.
        
        Returns:
            A dictionary containing the keeper's current status information.
        """
        return {
            "id": self._employee_id,
            "name": self._name,
            "specialty": self._specialty.name,
            "specialty_display": self._specialty.display_name,
            "assigned_enclosures": self._assigned_enclosures.copy(),
            "actions_remaining": self.actions_remaining,
            "daily_cost": self.daily_cost
        }
    
    def to_dict(self) -> dict:
        """
        Serialise to dictionary for JSON save.
        
        Returns:
            A dictionary representation suitable for JSON serialisation.
        """
        return {
            "employee_id": self._employee_id,
            "name": self._name,
            "specialty": self._specialty.name,
            "assigned_enclosures": self._assigned_enclosures.copy(),
            "actions_today": self._actions_today
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> ZooKeeper:
        """
        Deserialise from dictionary.
        
        Args:
            data: Dictionary containing keeper data.
        
        Returns:
            A new ZooKeeper instance.
        """
        keeper = cls(
            employee_id=data["employee_id"],
            name=data["name"],
            specialty=Specialty[data["specialty"]]
        )
        keeper._assigned_enclosures = list(data["assigned_enclosures"])
        keeper._actions_today = data.get("actions_today", 0)
        return keeper
    
    def __str__(self) -> str:
        """Return a string representation of the keeper."""
        return (
            f"👤 {self._name} ({self._specialty.display_name}) - "
            f"Actions: {self.actions_remaining}/{self._max_actions}"
        )
    
    def __repr__(self) -> str:
        """Return a developer-friendly representation."""
        return (
            f"ZooKeeper(employee_id={self._employee_id!r}, "
            f"name={self._name!r}, specialty={self._specialty.name})"
        )


# Keeper name generator data
KEEPER_FIRST_NAMES = [
    "Steve", "Bindi", "Robert", "Terri", "Jack", "Sarah", "Mike",
    "Lisa", "Dave", "Amy", "Chris", "Kate", "Tom", "Emma"
]

KEEPER_LAST_NAMES = [
    "Irwin", "Corwin", "Attenborough", "Goodall", "Fossey",
    "Marlin", "Wildlife", "Nature", "Bush", "Creek"
]


def generate_random_keeper(employee_id: str) -> ZooKeeper:
    """
    Generate a zookeeper with random name and specialty.
    
    Args:
        employee_id: The unique employee ID for the new keeper.
    
    Returns:
        A new ZooKeeper with a randomly generated name and specialty.
    """
    import random
    name = f"{random.choice(KEEPER_FIRST_NAMES)} {random.choice(KEEPER_LAST_NAMES)}"
    specialty = random.choice(list(Specialty))
    return ZooKeeper(employee_id, name, specialty)
