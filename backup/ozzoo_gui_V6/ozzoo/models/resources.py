"""
Resource classes for the OzZoo application.

This module provides Food and Medicine classes that represent consumable
resources used to care for zoo animals.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ozzoo.models.animals.base import Animal


class Food:
    """Represents food items for zoo animals."""

    def __init__(self, name: str, food_type: str, cost: float, nutrition: int) -> None:
        """
        Initialise a Food instance.

        Args:
            name: Display name (e.g., "Fresh Eucalyptus Leaves").
            food_type: Diet category (e.g., "eucalyptus", "grass", "meat", "fish", "insects").
            cost: Cost per unit in dollars.
            nutrition: Hunger reduction value (typically 30-80).
        """
        self._name = name
        self._food_type = food_type
        self._cost = cost
        self._nutrition = nutrition

    @property
    def name(self) -> str:
        """Return the display name of the food."""
        return self._name

    @property
    def food_type(self) -> str:
        """Return the diet category of the food."""
        return self._food_type

    @property
    def cost(self) -> float:
        """Return the cost per unit in dollars."""
        return self._cost

    @property
    def nutrition(self) -> int:
        """Return the hunger reduction value."""
        return self._nutrition

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return f"{self._name} (${self._cost:.2f}) - Nutrition: {self._nutrition}"

    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        return (
            f"Food(name={self._name!r}, food_type={self._food_type!r}, "
            f"cost={self._cost!r}, nutrition={self._nutrition!r})"
        )

    def to_dict(self) -> dict:
        """
        Serialise to dictionary for JSON save.

        Returns:
            A dictionary containing all food attributes.
        """
        return {
            "name": self._name,
            "food_type": self._food_type,
            "cost": self._cost,
            "nutrition": self._nutrition,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Food:
        """
        Deserialise from dictionary.

        Args:
            data: Dictionary containing food attributes.

        Returns:
            A new Food instance.
        """
        return cls(
            name=data["name"],
            food_type=data["food_type"],
            cost=data["cost"],
            nutrition=data["nutrition"],
        )


class Medicine:
    """Represents medicine for treating sick animals."""

    def __init__(
        self,
        name: str,
        treats: list[str],
        cost: float,
        healing: int = 30,
    ) -> None:
        """
        Initialise a Medicine instance.

        Args:
            name: Display name (e.g., "General Antibiotics").
            treats: List of conditions/species it treats (e.g., ["all"] or ["mammal", "bird"]).
            cost: Cost per dose in dollars.
            healing: Health restoration value (typically 20-50).
        """
        self._name = name
        self._treats = treats
        self._cost = cost
        self._healing = healing

    @property
    def name(self) -> str:
        """Return the display name of the medicine."""
        return self._name

    @property
    def treats(self) -> list[str]:
        """Return the list of conditions/species this medicine treats."""
        return self._treats.copy()

    @property
    def cost(self) -> float:
        """Return the cost per dose in dollars."""
        return self._cost

    @property
    def healing(self) -> int:
        """Return the health restoration value."""
        return self._healing

    def can_treat(self, animal_type: str) -> bool:
        """
        Check if this medicine can treat the given animal type.

        Args:
            animal_type: The type of animal (e.g., "mammal", "bird", "reptile").

        Returns:
            True if this medicine can treat the animal type, False otherwise.
        """
        return "all" in self._treats or animal_type.lower() in [
            t.lower() for t in self._treats
        ]

    def apply(self, animal: Animal) -> int:
        """
        Apply medicine to an animal.

        This method increases the animal's health by the healing value,
        capped at 100.

        Args:
            animal: The animal to treat.

        Returns:
            The amount of health actually restored.
        """
        old_health = animal.health
        new_health = min(100, old_health + self._healing)
        animal.health = new_health
        return new_health - old_health

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return f"{self._name} (${self._cost:.2f}) - Heals: +{self._healing}"

    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        return (
            f"Medicine(name={self._name!r}, treats={self._treats!r}, "
            f"cost={self._cost!r}, healing={self._healing!r})"
        )

    def to_dict(self) -> dict:
        """
        Serialise to dictionary for JSON save.

        Returns:
            A dictionary containing all medicine attributes.
        """
        return {
            "name": self._name,
            "treats": self._treats,
            "cost": self._cost,
            "healing": self._healing,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Medicine:
        """
        Deserialise from dictionary.

        Args:
            data: Dictionary containing medicine attributes.

        Returns:
            A new Medicine instance.
        """
        return cls(
            name=data["name"],
            treats=data["treats"],
            cost=data["cost"],
            healing=data.get("healing", 30),
        )


# Predefined food types available in the zoo
FOOD_TYPES: dict[str, Food] = {
    "eucalyptus": Food(
        name="Fresh Eucalyptus Leaves",
        food_type="eucalyptus",
        cost=5.0,
        nutrition=60,
    ),
    "grass": Food(
        name="Native Grass Bundle",
        food_type="grass",
        cost=3.0,
        nutrition=50,
    ),
    "meat": Food(
        name="Fresh Meat",
        food_type="meat",
        cost=15.0,
        nutrition=70,
    ),
    "fish": Food(
        name="Fresh Fish",
        food_type="fish",
        cost=12.0,
        nutrition=65,
    ),
    "insects": Food(
        name="Mixed Insects",
        food_type="insects",
        cost=8.0,
        nutrition=55,
    ),
}

# Predefined medicine types available in the zoo
MEDICINE_TYPES: dict[str, Medicine] = {
    "general": Medicine(
        name="General Antibiotics",
        treats=["all"],
        cost=50.0,
        healing=30,
    ),
    "mammal_specialist": Medicine(
        name="Mammal Care Plus",
        treats=["mammal"],
        cost=40.0,
        healing=40,
    ),
    "avian": Medicine(
        name="Avian Wellness",
        treats=["bird"],
        cost=45.0,
        healing=35,
    ),
    "reptile": Medicine(
        name="Reptile Remedy",
        treats=["reptile"],
        cost=55.0,
        healing=45,
    ),
}
