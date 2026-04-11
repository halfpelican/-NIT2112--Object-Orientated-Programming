"""
OzZoo Enclosure Module.

Contains Enclosure ABC and all enclosure type implementations.
Each enclosure provides a specific habitat type for compatible animals.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from .animals.animal import Animal


class Enclosure(ABC):
    """
    Abstract base class for all zoo enclosures.

    Implements ICleanable interface.

    Attributes:
        enclosure_id (str): Unique identifier
        name (str): Display name
        capacity (int): Maximum number of animals
        animals (List[Animal]): Animals in this enclosure
        cleanliness (int): Cleanliness level 0-100
    """

    MAX_CLEANLINESS = 100
    DIRTY_THRESHOLD = 30  # Needs cleaning

    def __init__(self, enclosure_id: str, name: str, capacity: int) -> None:
        """
        Initialise an enclosure.

        Args:
            enclosure_id: Unique identifier for the enclosure
            name: Display name of the enclosure
            capacity: Maximum number of animals this enclosure can hold
        """
        self._enclosure_id = enclosure_id
        self._name = name
        self._capacity = capacity
        self._animals: List[Animal] = []
        self._cleanliness = 80  # Starts fairly clean

    # Properties (read-only for id/name/capacity, read-write for cleanliness)
    @property
    def enclosure_id(self) -> str:
        """Return the unique identifier for this enclosure."""
        return self._enclosure_id

    @property
    def name(self) -> str:
        """Return the display name of this enclosure."""
        return self._name

    @property
    def capacity(self) -> int:
        """Return the maximum capacity of this enclosure."""
        return self._capacity

    @property
    def animals(self) -> List[Animal]:
        """Return the list of animals in this enclosure."""
        return self._animals.copy()  # Return a copy to prevent external modification

    @property
    def cleanliness(self) -> int:
        """Return the current cleanliness level (0-100)."""
        return self._cleanliness

    @cleanliness.setter
    def cleanliness(self, value: int) -> None:
        """Set the cleanliness level, clamped to 0-100."""
        self._cleanliness = max(0, min(self.MAX_CLEANLINESS, value))

    @property
    def is_dirty(self) -> bool:
        """Check if cleanliness is below threshold."""
        return self._cleanliness < self.DIRTY_THRESHOLD

    @property
    def is_full(self) -> bool:
        """Check if at capacity."""
        return len(self._animals) >= self._capacity

    @property
    def available_space(self) -> int:
        """Return number of available spots."""
        return max(0, self._capacity - len(self._animals))

    # Abstract methods
    @abstractmethod
    def clean(self) -> str:
        """
        Clean the enclosure. Returns a description of the cleaning action.

        Each enclosure type has unique cleaning requirements.

        Returns:
            A string describing the cleaning action performed.
        """
        pass

    @abstractmethod
    def get_habitat_type(self) -> str:
        """Return the habitat type this enclosure provides."""
        pass

    @abstractmethod
    def get_compatible_species(self) -> List[str]:
        """Return list of species that can live in this enclosure."""
        pass

    # Concrete methods
    def add_animal(self, animal: Animal) -> None:
        """
        Add an animal to the enclosure.

        Args:
            animal: The animal to add to this enclosure.

        Raises:
            HabitatCapacityExceededError: If enclosure is full
            InvalidHabitatError: If animal's habitat type doesn't match
        """
        from ..exceptions import HabitatCapacityExceededError, InvalidHabitatError

        if self.is_full:
            raise HabitatCapacityExceededError(self._name, self._capacity)

        if animal.get_habitat_type() != self.get_habitat_type():
            raise InvalidHabitatError(
                animal.name, self._name, animal.get_habitat_type()
            )

        self._animals.append(animal)

    def remove_animal(self, animal: Animal) -> bool:
        """
        Remove an animal from the enclosure.

        Args:
            animal: The animal to remove.

        Returns:
            True if the animal was found and removed, False otherwise.
        """
        if animal in self._animals:
            self._animals.remove(animal)
            return True
        return False

    def daily_update(self) -> None:
        """
        Process daily changes.

        - Cleanliness decreases by (5 + number of animals * 2)
        - If dirty, all animals lose 10 happiness
        """
        # Decrease cleanliness based on animal population
        cleanliness_loss = 5 + len(self._animals) * 2
        self._cleanliness = max(0, self._cleanliness - cleanliness_loss)

        # If enclosure is dirty, animals become unhappy
        if self.is_dirty:
            for animal in self._animals:
                animal.happiness = max(0, animal.happiness - 10)

    def get_cleanliness(self) -> int:
        """Return current cleanliness level (ICleanable interface)."""
        return self._cleanliness

    def get_status(self) -> Dict[str, Any]:
        """Return current status as dictionary."""
        return {
            "id": self._enclosure_id,
            "name": self._name,
            "capacity": self._capacity,
            "animal_count": len(self._animals),
            "cleanliness": self._cleanliness,
            "is_dirty": self.is_dirty,
            "is_full": self.is_full,
            "habitat_type": self.get_habitat_type(),
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to dictionary for JSON save."""
        return {
            "enclosure_id": self._enclosure_id,
            "name": self._name,
            "capacity": self._capacity,
            "cleanliness": self._cleanliness,
            "habitat_type": self.get_habitat_type(),
            "animal_names": [animal.name for animal in self._animals],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Enclosure:
        """
        Deserialise from dictionary.

        Args:
            data: Dictionary containing enclosure data.

        Returns:
            An Enclosure instance of the appropriate type.
        """
        habitat_type = data.get("habitat_type", "")
        enclosure = create_enclosure(
            habitat_type=habitat_type,
            enclosure_id=data["enclosure_id"],
            name=data.get("name"),
            capacity=data.get("capacity"),
        )
        enclosure._cleanliness = data.get("cleanliness", 80)
        # Note: Animals are linked separately after all objects are loaded
        return enclosure

    def __str__(self) -> str:
        """Return a string representation of the enclosure."""
        if self._cleanliness > 70:
            clean_icon = "✨"
        elif self._cleanliness > 30:
            clean_icon = "🧹"
        else:
            clean_icon = "⚠️"
        return (
            f"{clean_icon} {self._name} ({len(self._animals)}/{self._capacity}) "
            f"- Clean: {self._cleanliness}%"
        )

    def __repr__(self) -> str:
        """Return a detailed representation of the enclosure."""
        return (
            f"{self.__class__.__name__}(enclosure_id={self._enclosure_id!r}, "
            f"name={self._name!r}, capacity={self._capacity})"
        )


# Concrete Enclosure Types


class EucalyptusGrove(Enclosure):
    """
    Enclosure for tree-dwelling animals like Koalas.

    Has eucalyptus trees for climbing and sleeping.

    Attributes:
        tree_count (int): Number of eucalyptus trees in the enclosure.
    """

    def __init__(
        self,
        enclosure_id: str,
        name: str = "Eucalyptus Grove",
        capacity: int = 6,
    ) -> None:
        """
        Initialise a Eucalyptus Grove enclosure.

        Args:
            enclosure_id: Unique identifier for the enclosure.
            name: Display name (default: "Eucalyptus Grove").
            capacity: Maximum number of animals (default: 6).
        """
        super().__init__(enclosure_id, name, capacity)
        self._tree_count = 12  # Number of eucalyptus trees

    @property
    def tree_count(self) -> int:
        """Return the number of eucalyptus trees."""
        return self._tree_count

    def clean(self) -> str:
        """Clean fallen leaves and check tree health."""
        self._cleanliness = min(self.MAX_CLEANLINESS, self._cleanliness + 40)
        return (
            f"Raked leaves and trimmed branches in {self._name}. "
            f"Tree count: {self._tree_count}"
        )

    def get_habitat_type(self) -> str:
        """Return the habitat type."""
        return "eucalyptus_grove"

    def get_compatible_species(self) -> List[str]:
        """Return list of compatible species."""
        return ["Koala"]

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to dictionary for JSON save."""
        data = super().to_dict()
        data["tree_count"] = self._tree_count
        return data


class OutbackSavanna(Enclosure):
    """
    Open grassland enclosure for kangaroos, wombats, echidnas.

    Features shade structures and grazing areas.

    Attributes:
        shade_areas (int): Number of shade structures in the enclosure.
    """

    def __init__(
        self,
        enclosure_id: str,
        name: str = "Outback Savanna",
        capacity: int = 10,
    ) -> None:
        """
        Initialise an Outback Savanna enclosure.

        Args:
            enclosure_id: Unique identifier for the enclosure.
            name: Display name (default: "Outback Savanna").
            capacity: Maximum number of animals (default: 10).
        """
        super().__init__(enclosure_id, name, capacity)
        self._shade_areas = 4  # Number of shade structures

    @property
    def shade_areas(self) -> int:
        """Return the number of shade areas."""
        return self._shade_areas

    def clean(self) -> str:
        """Clear droppings and maintain grass."""
        self._cleanliness = min(self.MAX_CLEANLINESS, self._cleanliness + 35)
        return (
            f"Cleared the savanna and checked {self._shade_areas} shade "
            f"structures in {self._name}."
        )

    def get_habitat_type(self) -> str:
        """Return the habitat type."""
        return "outback_savanna"

    def get_compatible_species(self) -> List[str]:
        """Return list of compatible species."""
        return ["Kangaroo", "Wombat", "Echidna", "TasmanianDevil"]

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to dictionary for JSON save."""
        data = super().to_dict()
        data["shade_areas"] = self._shade_areas
        return data


class Billabong(Enclosure):
    """
    Water-based enclosure for semi-aquatic animals.

    Features a pond/water body for crocodiles and platypus.

    Attributes:
        water_level (int): Current water level percentage.
    """

    def __init__(
        self,
        enclosure_id: str,
        name: str = "Billabong",
        capacity: int = 5,
    ) -> None:
        """
        Initialise a Billabong enclosure.

        Args:
            enclosure_id: Unique identifier for the enclosure.
            name: Display name (default: "Billabong").
            capacity: Maximum number of animals (default: 5).
        """
        super().__init__(enclosure_id, name, capacity)
        self._water_level = 100  # Water level percentage

    @property
    def water_level(self) -> int:
        """Return the current water level percentage."""
        return self._water_level

    def clean(self) -> str:
        """Filter water and clean banks."""
        self._cleanliness = min(self.MAX_CLEANLINESS, self._cleanliness + 45)
        self._water_level = 100  # Refill water
        return (
            f"Filtered water and cleaned banks in {self._name}. "
            f"Water level restored to 100%."
        )

    def get_habitat_type(self) -> str:
        """Return the habitat type."""
        return "billabong"

    def get_compatible_species(self) -> List[str]:
        """Return list of compatible species."""
        return ["SaltwaterCroc", "Platypus"]

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to dictionary for JSON save."""
        data = super().to_dict()
        data["water_level"] = self._water_level
        return data


class RainforestAviary(Enclosure):
    """
    Large netted enclosure for birds.

    Features trees, perches, and controlled humidity.

    Attributes:
        humidity (int): Current humidity percentage.
    """

    def __init__(
        self,
        enclosure_id: str,
        name: str = "Rainforest Aviary",
        capacity: int = 8,
    ) -> None:
        """
        Initialise a Rainforest Aviary enclosure.

        Args:
            enclosure_id: Unique identifier for the enclosure.
            name: Display name (default: "Rainforest Aviary").
            capacity: Maximum number of animals (default: 8).
        """
        super().__init__(enclosure_id, name, capacity)
        self._humidity = 70  # Humidity percentage

    @property
    def humidity(self) -> int:
        """Return the current humidity percentage."""
        return self._humidity

    def clean(self) -> str:
        """Clean perches and adjust humidity."""
        self._cleanliness = min(self.MAX_CLEANLINESS, self._cleanliness + 30)
        self._humidity = 70  # Reset humidity
        return (
            f"Cleaned perches and adjusted misting in {self._name}. "
            f"Humidity set to {self._humidity}%."
        )

    def get_habitat_type(self) -> str:
        """Return the habitat type."""
        return "rainforest_aviary"

    def get_compatible_species(self) -> List[str]:
        """Return list of compatible species."""
        return ["Emu", "WedgeTailedEagle"]

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to dictionary for JSON save."""
        data = super().to_dict()
        data["humidity"] = self._humidity
        return data


class ReptileHouse(Enclosure):
    """
    Temperature-controlled enclosure for reptiles.

    Features heat lamps and basking areas.

    Attributes:
        temperature (int): Current temperature in Celsius.
    """

    def __init__(
        self,
        enclosure_id: str,
        name: str = "Reptile House",
        capacity: int = 6,
    ) -> None:
        """
        Initialise a Reptile House enclosure.

        Args:
            enclosure_id: Unique identifier for the enclosure.
            name: Display name (default: "Reptile House").
            capacity: Maximum number of animals (default: 6).
        """
        super().__init__(enclosure_id, name, capacity)
        self._temperature = 28  # Temperature in Celsius

    @property
    def temperature(self) -> int:
        """Return the current temperature in Celsius."""
        return self._temperature

    def clean(self) -> str:
        """Clean glass, check heat lamps, sanitise surfaces."""
        self._cleanliness = min(self.MAX_CLEANLINESS, self._cleanliness + 50)
        return (
            f"Sanitised surfaces and calibrated heat lamps in {self._name}. "
            f"Temp: {self._temperature}°C."
        )

    def get_habitat_type(self) -> str:
        """Return the habitat type."""
        return "reptile_house"

    def get_compatible_species(self) -> List[str]:
        """Return list of compatible species."""
        return ["FrilledLizard"]

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to dictionary for JSON save."""
        data = super().to_dict()
        data["temperature"] = self._temperature
        return data


# Factory function for creating enclosures
ENCLOSURE_TYPES: Dict[str, type] = {
    "eucalyptus_grove": EucalyptusGrove,
    "outback_savanna": OutbackSavanna,
    "billabong": Billabong,
    "rainforest_aviary": RainforestAviary,
    "reptile_house": ReptileHouse,
}


def create_enclosure(
    habitat_type: str, enclosure_id: str, **kwargs: Any
) -> Enclosure:
    """
    Factory function to create enclosures by type.

    Args:
        habitat_type: One of eucalyptus_grove, outback_savanna, billabong,
                      rainforest_aviary, reptile_house
        enclosure_id: Unique identifier
        **kwargs: Additional arguments passed to the enclosure constructor
                  (e.g., name, capacity)

    Returns:
        An Enclosure instance of the specified type.

    Raises:
        ValueError: If habitat_type is not recognised.
    """
    if habitat_type not in ENCLOSURE_TYPES:
        valid_types = ", ".join(ENCLOSURE_TYPES.keys())
        raise ValueError(
            f"Unknown enclosure type: {habitat_type}. Valid types: {valid_types}"
        )

    # Filter out None values from kwargs to allow defaults to be used
    filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}
    return ENCLOSURE_TYPES[habitat_type](enclosure_id, **filtered_kwargs)
