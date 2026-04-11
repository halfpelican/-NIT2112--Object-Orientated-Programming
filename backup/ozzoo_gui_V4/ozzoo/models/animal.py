"""
OzZoo Animal Module.

Contains Animal ABC and intermediate class implementations (Mammal, Bird, Reptile).
These classes form the core animal hierarchy for the zoo simulation.
"""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .resources import Food
    from ..interfaces.base import IObserver


class Animal(ABC):
    """
    Abstract base class for all zoo animals.

    Implements IFeedable interface (but doesn't formally inherit to avoid circular imports).

    Attributes:
        name (str): Animal's name
        age (int): Age in years
        health (int): Health level 0-100
        hunger (int): Hunger level 0-100 (higher = hungrier)
        happiness (int): Happiness level 0-100
    """

    # Class constants
    MAX_HEALTH = 100
    MAX_HUNGER = 100
    MAX_HAPPINESS = 100
    HUNGER_THRESHOLD = 80  # Starving
    HEALTH_CRITICAL = 20   # Sick
    HAPPINESS_LOW = 30     # Stressed

    def __init__(self, name: str, age: int, species: str, gender: str = "unknown") -> None:
        """
        Initialise a new animal.

        Args:
            name: Animal's given name
            age: Age in years (must be >= 0)
            species: Species identifier
            gender: "male", "female", or "unknown"
        """
        self._name = name
        self._age = max(0, age)  # Ensure non-negative age
        self._species = species
        self._gender = gender
        self._health = 100
        self._hunger = 30  # Slightly hungry to start
        self._happiness = 70
        self._is_alive = True
        self._observers: List[IObserver] = []

    # -------------------------------------------------------------------------
    # Properties with encapsulation
    # -------------------------------------------------------------------------

    @property
    def name(self) -> str:
        """Return the animal's name."""
        return self._name

    @property
    def age(self) -> int:
        """Return the animal's age in years."""
        return self._age

    @property
    def species(self) -> str:
        """Return the animal's species identifier."""
        return self._species

    @property
    def gender(self) -> str:
        """Return the animal's gender."""
        return self._gender

    @property
    def health(self) -> int:
        """Return the animal's health level (0-100)."""
        return self._health

    @health.setter
    def health(self, value: int) -> None:
        """
        Set health level (clamped to 0-100).

        Notifies observers on death or when animal becomes sick.

        Args:
            value: New health value (will be clamped to 0-100).
        """
        old_health = self._health
        self._health = max(0, min(self.MAX_HEALTH, value))

        # Check for death
        if self._health <= 0 and self._is_alive:
            self._is_alive = False
            self._notify_observers("death")

        # Check if animal became sick
        elif old_health >= self.HEALTH_CRITICAL > self._health:
            self._notify_observers("sick")

    @property
    def hunger(self) -> int:
        """Return the animal's hunger level (0-100, higher = hungrier)."""
        return self._hunger

    @hunger.setter
    def hunger(self, value: int) -> None:
        """
        Set hunger level (clamped to 0-100).

        Notifies observers when animal starts starving.

        Args:
            value: New hunger value (will be clamped to 0-100).
        """
        old_hunger = self._hunger
        self._hunger = max(0, min(self.MAX_HUNGER, value))

        # Check if animal became starving
        if old_hunger < self.HUNGER_THRESHOLD <= self._hunger:
            self._notify_observers("starving")

    @property
    def happiness(self) -> int:
        """Return the animal's happiness level (0-100)."""
        return self._happiness

    @happiness.setter
    def happiness(self, value: int) -> None:
        """
        Set happiness level (clamped to 0-100).

        Notifies observers when animal becomes stressed.

        Args:
            value: New happiness value (will be clamped to 0-100).
        """
        old_happiness = self._happiness
        self._happiness = max(0, min(self.MAX_HAPPINESS, value))

        # Check if animal became stressed
        if old_happiness >= self.HAPPINESS_LOW > self._happiness:
            self._notify_observers("stressed")

    @property
    def is_alive(self) -> bool:
        """Return True if the animal is alive."""
        return self._is_alive

    @property
    def is_hungry(self) -> bool:
        """Check if animal is hungry (hunger > 50)."""
        return self._hunger > 50

    @property
    def is_starving(self) -> bool:
        """Check if animal is critically hungry (hunger >= 80)."""
        return self._hunger >= self.HUNGER_THRESHOLD

    @property
    def is_sick(self) -> bool:
        """Check if animal health is critical (health < 20)."""
        return self._health < self.HEALTH_CRITICAL

    @property
    def is_stressed(self) -> bool:
        """Check if animal happiness is low (happiness < 30)."""
        return self._happiness < self.HAPPINESS_LOW

    @property
    def can_breed(self) -> bool:
        """Check if animal meets breeding conditions (health > 70, happiness > 60)."""
        return self._health > 70 and self._happiness > 60 and self._is_alive

    # -------------------------------------------------------------------------
    # Abstract methods - MUST be overridden by subclasses
    # -------------------------------------------------------------------------

    @abstractmethod
    def make_sound(self) -> str:
        """Return the sound this animal makes. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def get_diet(self) -> str:
        """Return the diet type required (eucalyptus, grass, meat, fish, insects)."""
        pass

    @abstractmethod
    def get_habitat_type(self) -> str:
        """
        Return the required habitat type.

        Valid types: eucalyptus_grove, outback_savanna, billabong,
                     rainforest_aviary, reptile_house
        """
        pass

    @abstractmethod
    def get_animal_type(self) -> str:
        """Return the animal category (mammal, bird, reptile)."""
        pass

    # -------------------------------------------------------------------------
    # Concrete methods
    # -------------------------------------------------------------------------

    def feed(self, food: Food) -> bool:
        """
        Feed the animal.

        Returns True if feeding was successful (correct diet type).
        Reduces hunger by food.nutrition, increases happiness by 5.

        Args:
            food: The food item to feed to the animal.

        Returns:
            True if feeding was successful, False if wrong diet type or not hungry.
        """
        if not self._is_alive:
            return False

        # Check if animal is hungry (refuse food if hunger is 0)
        if self._hunger == 0:
            return False

        # Check if food matches the animal's diet
        if food.food_type != self.get_diet():
            return False

        # Apply nutrition (reduce hunger)
        self._hunger = max(0, self._hunger - food.nutrition)

        # Feeding makes the animal happier
        self._happiness = min(self.MAX_HAPPINESS, self._happiness + 5)

        self._notify_observers("fed")
        return True

    def daily_update(self) -> None:
        """
        Process daily changes to animal state.

        - Hunger increases by 15
        - If starving, health decreases by 10
        - Happiness decreases by 5
        - Stressed animals may attempt to escape (higher chance when less happy)
        """
        if not self._is_alive:
            return

        # Hunger increases daily
        self.hunger = self._hunger + 15

        # Starving animals lose health
        if self.is_starving:
            self.health = self._health - 10

        # Happiness decreases over time
        self.happiness = self._happiness - 5

        # Check for escape attempt if stressed (happiness < 30)
        if self.is_stressed:
            # Calculate escape probability: increases as happiness decreases
            # At 29% happiness: ~3% chance, at 0% happiness: ~30% chance
            escape_probability = (30 - self._happiness) / 100
            
            if random.random() < escape_probability:
                self._is_alive = False  # Animal has escaped
                self._notify_observers("escape")

    def heal(self, amount: int) -> None:
        """
        Restore health by the given amount.

        Args:
            amount: The amount of health to restore (positive integer).
        """
        if self._is_alive and amount > 0:
            self.health = self._health + amount

    def get_status(self) -> dict:
        """
        Return current status as dictionary.

        Returns:
            A dictionary containing all current animal status information.
        """
        return {
            "name": self._name,
            "species": self._species,
            "age": self._age,
            "gender": self._gender,
            "health": self._health,
            "hunger": self._hunger,
            "happiness": self._happiness,
            "is_alive": self._is_alive,
            "is_sick": self.is_sick,
            "is_hungry": self.is_hungry,
            "is_starving": self.is_starving,
            "is_stressed": self.is_stressed,
            "can_breed": self.can_breed,
        }

    # -------------------------------------------------------------------------
    # Observer pattern methods
    # -------------------------------------------------------------------------

    def attach(self, observer: IObserver) -> None:
        """
        Attach an observer to receive notifications.

        Args:
            observer: The observer to attach.
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: IObserver) -> None:
        """
        Detach an observer from receiving notifications.

        Args:
            observer: The observer to detach.
        """
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify_observers(self, event: str) -> None:
        """
        Notify all attached observers of an event.

        Args:
            event: A string describing the event that occurred.
        """
        for observer in self._observers:
            observer.update(self, event)

    # -------------------------------------------------------------------------
    # Serialisation
    # -------------------------------------------------------------------------

    def to_dict(self) -> dict:
        """
        Serialise to dictionary for JSON save.

        Returns:
            A dictionary containing all animal attributes for persistence.
        """
        return {
            "class": self.__class__.__name__,
            "name": self._name,
            "age": self._age,
            "species": self._species,
            "gender": self._gender,
            "health": self._health,
            "hunger": self._hunger,
            "happiness": self._happiness,
            "is_alive": self._is_alive,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Animal:
        """
        Deserialise from dictionary.

        Note: This must be called from concrete subclass as Animal is abstract.

        Args:
            data: Dictionary containing animal attributes.

        Returns:
            A new Animal instance (of the appropriate subclass).

        Raises:
            NotImplementedError: If called directly on Animal ABC.
        """
        if cls is Animal:
            raise NotImplementedError(
                "Cannot instantiate Animal directly. Use a concrete subclass."
            )

        # Create instance with constructor parameters
        instance = cls(
            name=data["name"],
            age=data["age"],
            species=data["species"],
            gender=data.get("gender", "unknown"),
        )

        # Restore state attributes
        instance._health = data.get("health", 100)
        instance._hunger = data.get("hunger", 30)
        instance._happiness = data.get("happiness", 70)
        instance._is_alive = data.get("is_alive", True)

        return instance

    # -------------------------------------------------------------------------
    # String representations
    # -------------------------------------------------------------------------

    def __str__(self) -> str:
        """Return a human-readable string representation with status indicator."""
        if not self._is_alive:
            status = "💀"
        elif self._health > 50:
            status = "🟢"
        elif self._health > 20:
            status = "🟡"
        else:
            status = "🔴"
        return f"{status} {self._name} ({self._species}) - Health: {self._health}, Hunger: {self._hunger}"

    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        return f"{self.__class__.__name__}(name='{self._name}', age={self._age})"


class Mammal(Animal):
    """
    Intermediate class for mammalian animals.

    Extends Animal with mammal-specific attributes and behaviours such as
    fur colour and nursing capability.
    """

    def __init__(
        self,
        name: str,
        age: int,
        species: str,
        fur_colour: str = "brown",
        gender: str = "unknown",
    ) -> None:
        """
        Initialise a new mammal.

        Args:
            name: Animal's given name.
            age: Age in years (must be >= 0).
            species: Species identifier.
            fur_colour: Colour of the mammal's fur.
            gender: "male", "female", or "unknown".
        """
        super().__init__(name, age, species, gender)
        self._fur_colour = fur_colour

    @property
    def fur_colour(self) -> str:
        """Return the mammal's fur colour."""
        return self._fur_colour

    def nurse(self) -> str:
        """
        Mammals can nurse their young.

        Returns:
            A string describing the nursing behaviour.
        """
        return f"{self._name} is nursing its young."

    def get_animal_type(self) -> str:
        """Return the animal category."""
        return "mammal"

    def to_dict(self) -> dict:
        """
        Include fur_colour in serialisation.

        Returns:
            A dictionary containing all mammal attributes.
        """
        data = super().to_dict()
        data["fur_colour"] = self._fur_colour
        return data

    @classmethod
    def from_dict(cls, data: dict) -> Mammal:
        """
        Deserialise from dictionary.

        Args:
            data: Dictionary containing mammal attributes.

        Returns:
            A new Mammal instance.
        """
        instance = cls(
            name=data["name"],
            age=data["age"],
            species=data["species"],
            fur_colour=data.get("fur_colour", "brown"),
            gender=data.get("gender", "unknown"),
        )

        # Restore state attributes
        instance._health = data.get("health", 100)
        instance._hunger = data.get("hunger", 30)
        instance._happiness = data.get("happiness", 70)
        instance._is_alive = data.get("is_alive", True)

        return instance


class Bird(Animal):
    """
    Intermediate class for bird animals.

    Extends Animal with bird-specific attributes and behaviours such as
    wingspan and flight capability.
    """

    def __init__(
        self,
        name: str,
        age: int,
        species: str,
        wingspan: float,
        can_fly: bool = True,
        gender: str = "unknown",
    ) -> None:
        """
        Initialise a new bird.

        Args:
            name: Animal's given name.
            age: Age in years (must be >= 0).
            species: Species identifier.
            wingspan: Wingspan in metres.
            can_fly: Whether this bird can fly.
            gender: "male", "female", or "unknown".
        """
        super().__init__(name, age, species, gender)
        self._wingspan = wingspan
        self._can_fly = can_fly

    @property
    def wingspan(self) -> float:
        """Return the bird's wingspan in metres."""
        return self._wingspan

    @property
    def can_fly(self) -> bool:
        """Return True if this bird can fly."""
        return self._can_fly

    def fly(self) -> str:
        """
        Attempt to fly.

        Returns:
            A string describing the flight attempt result.
        """
        if self._can_fly:
            return f"{self._name} soars through the air!"
        return f"{self._name} flaps its wings but stays on the ground."

    def get_animal_type(self) -> str:
        """Return the animal category."""
        return "bird"

    def to_dict(self) -> dict:
        """
        Include wingspan and can_fly in serialisation.

        Returns:
            A dictionary containing all bird attributes.
        """
        data = super().to_dict()
        data["wingspan"] = self._wingspan
        data["can_fly"] = self._can_fly
        return data

    @classmethod
    def from_dict(cls, data: dict) -> Bird:
        """
        Deserialise from dictionary.

        Args:
            data: Dictionary containing bird attributes.

        Returns:
            A new Bird instance.
        """
        instance = cls(
            name=data["name"],
            age=data["age"],
            species=data["species"],
            wingspan=data.get("wingspan", 1.0),
            can_fly=data.get("can_fly", True),
            gender=data.get("gender", "unknown"),
        )

        # Restore state attributes
        instance._health = data.get("health", 100)
        instance._hunger = data.get("hunger", 30)
        instance._happiness = data.get("happiness", 70)
        instance._is_alive = data.get("is_alive", True)

        return instance


class Reptile(Animal):
    """
    Intermediate class for reptile animals.

    Extends Animal with reptile-specific attributes and behaviours such as
    venom capability and basking.
    """

    def __init__(
        self,
        name: str,
        age: int,
        species: str,
        is_venomous: bool = False,
        gender: str = "unknown",
    ) -> None:
        """
        Initialise a new reptile.

        Args:
            name: Animal's given name.
            age: Age in years (must be >= 0).
            species: Species identifier.
            is_venomous: Whether this reptile is venomous.
            gender: "male", "female", or "unknown".
        """
        super().__init__(name, age, species, gender)
        self._is_venomous = is_venomous

    @property
    def is_venomous(self) -> bool:
        """Return True if this reptile is venomous."""
        return self._is_venomous

    def bask(self) -> str:
        """
        Reptiles bask in the sun, increasing happiness by 10.

        Returns:
            A string describing the basking behaviour.
        """
        self._happiness = min(self.MAX_HAPPINESS, self._happiness + 10)
        return f"{self._name} is basking in the warm sun."

    def get_animal_type(self) -> str:
        """Return the animal category."""
        return "reptile"

    def to_dict(self) -> dict:
        """
        Include is_venomous in serialisation.

        Returns:
            A dictionary containing all reptile attributes.
        """
        data = super().to_dict()
        data["is_venomous"] = self._is_venomous
        return data

    @classmethod
    def from_dict(cls, data: dict) -> Reptile:
        """
        Deserialise from dictionary.

        Args:
            data: Dictionary containing reptile attributes.

        Returns:
            A new Reptile instance.
        """
        instance = cls(
            name=data["name"],
            age=data["age"],
            species=data["species"],
            is_venomous=data.get("is_venomous", False),
            gender=data.get("gender", "unknown"),
        )

        # Restore state attributes
        instance._health = data.get("health", 100)
        instance._hunger = data.get("hunger", 30)
        instance._happiness = data.get("happiness", 70)
        instance._is_alive = data.get("is_alive", True)

        return instance
