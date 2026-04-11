"""
Custom exception hierarchy for the OzZoo application.

This module defines a structured hierarchy of exceptions for handling
zoo-related errors including animal, resource, and enclosure issues.
"""


class ZooError(Exception):
    """Base exception for all zoo-related errors."""

    pass


class AnimalError(ZooError):
    """Base exception for animal-related errors."""

    pass


class IncompatibleSpeciesError(AnimalError):
    """Raised when incompatible species are placed together."""

    def __init__(self, animal1: str, animal2: str, enclosure: str) -> None:
        """
        Initialise the incompatible-species error message.

        Args:
            animal1: First species involved in the conflict.
            animal2: Second species involved in the conflict.
            enclosure: Enclosure where the conflict occurred.
        """
        self.animal1 = animal1
        self.animal2 = animal2
        self.enclosure = enclosure
        self.message = (
            f"Cannot place {animal1} with {animal2} in {enclosure} "
            f"- incompatible species!"
        )
        super().__init__(self.message)


class AnimalSickError(AnimalError):
    """Raised when an animal is too sick for an action."""

    def __init__(self, animal_name: str, action: str) -> None:
        """
        Initialise the sick-animal action error.

        Args:
            animal_name: Name of the animal that is too sick.
            action: Action that could not be performed.
        """
        self.animal_name = animal_name
        self.action = action
        self.message = f"{animal_name} is too sick to {action}!"
        super().__init__(self.message)


class ResourceError(ZooError):
    """Base exception for resource-related errors."""

    pass


class InsufficientFoodError(ResourceError):
    """Raised when there isn't enough food."""

    def __init__(self, food_type: str, required: int, available: int) -> None:
        """
        Initialise the insufficient-food error.

        Args:
            food_type: Type of food requested.
            required: Quantity required for the action.
            available: Quantity currently available.
        """
        self.food_type = food_type
        self.required = required
        self.available = available
        self.message = (
            f"Insufficient {food_type}: need {required}, have {available}"
        )
        super().__init__(self.message)


class InsufficientFundsError(ResourceError):
    """Raised when budget is insufficient."""

    def __init__(self, cost: float, budget: float) -> None:
        """
        Initialise the insufficient-funds error.

        Args:
            cost: Cost required to complete the action.
            budget: Current available budget.
        """
        self.cost = cost
        self.budget = budget
        self.message = f"Insufficient funds: need ${cost:.2f}, have ${budget:.2f}"
        super().__init__(self.message)


class EnclosureError(ZooError):
    """Base exception for enclosure-related errors."""

    pass


class HabitatCapacityExceededError(EnclosureError):
    """Raised when enclosure capacity is exceeded."""

    def __init__(self, enclosure_name: str, capacity: int) -> None:
        """
        Initialise the enclosure-capacity error.

        Args:
            enclosure_name: Name of the full enclosure.
            capacity: Maximum number of animals allowed.
        """
        self.enclosure_name = enclosure_name
        self.capacity = capacity
        self.message = (
            f"{enclosure_name} is at full capacity ({capacity} animals)!"
        )
        super().__init__(self.message)


class InvalidHabitatError(EnclosureError):
    """Raised when animal is placed in wrong habitat type."""

    def __init__(self, animal: str, enclosure: str, required: str) -> None:
        """
        Initialise the invalid-habitat error.

        Args:
            animal: Animal name/species being placed.
            enclosure: Target enclosure name.
            required: Habitat type required by the animal.
        """
        self.animal = animal
        self.enclosure = enclosure
        self.required = required
        self.message = (
            f"{animal} cannot live in {enclosure} - requires {required} habitat"
        )
        super().__init__(self.message)
