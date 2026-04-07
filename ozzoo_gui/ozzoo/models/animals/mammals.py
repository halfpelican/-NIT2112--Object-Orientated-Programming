"""
OzZoo Mammal Species Module.

Contains all concrete mammal implementations for the OzZoo simulation.
Each species inherits from the Mammal intermediate class and implements
species-specific behaviours and attributes.
"""

from __future__ import annotations

from ..animal import Mammal


class Koala(Mammal):
    """
    Australian Koala - sleepy eucalyptus eater.

    Inheritance: Animal -> Mammal -> Koala (3 levels)

    Koalas are arboreal herbivorous marsupials native to Australia.
    They are famous for sleeping up to 20 hours per day and eating
    exclusively eucalyptus leaves.
    """

    def __init__(self, name: str, age: int, gender: str = "unknown") -> None:
        """
        Initialise a new Koala.

        Args:
            name: The koala's given name.
            age: Age in years (must be >= 0).
            gender: "male", "female", or "unknown".
        """
        super().__init__(name, age, species="Koala", fur_colour="grey", gender=gender)
        self._sleep_hours = 20  # Koalas sleep a lot!

    @property
    def sleep_hours(self) -> int:
        """Return the number of hours this koala sleeps per day."""
        return self._sleep_hours

    def make_sound(self) -> str:
        """Return the sound a koala makes."""
        return f"{self._name} makes a deep bellowing sound!"

    def get_diet(self) -> str:
        """Return the koala's diet type."""
        return "eucalyptus"

    def get_habitat_type(self) -> str:
        """Return the required habitat type for koalas."""
        return "eucalyptus_grove"

    def sleep(self) -> str:
        """
        Koalas are famous for sleeping.

        Increases happiness by 15 (capped at MAX_HAPPINESS).

        Returns:
            A string describing the sleeping behaviour.
        """
        self._happiness = min(self.MAX_HAPPINESS, self._happiness + 15)
        return f"{self._name} curls up for a nap (only {self._sleep_hours} hours today!)"

    def to_dict(self) -> dict:
        """
        Serialise to dictionary for JSON save.

        Returns:
            A dictionary containing all koala attributes for persistence.
        """
        data = super().to_dict()
        data["class"] = "Koala"
        data["sleep_hours"] = self._sleep_hours
        return data


class Kangaroo(Mammal):
    """
    Australian Kangaroo - hopping marsupial.

    Kangaroos are large marsupials native to Australia, known for their
    powerful hind legs used for hopping and their boxing behaviour.
    Females carry their young (joeys) in a pouch.
    """

    def __init__(
        self, name: str, age: int, gender: str = "unknown", has_joey: bool = False
    ) -> None:
        """
        Initialise a new Kangaroo.

        Args:
            name: The kangaroo's given name.
            age: Age in years (must be >= 0).
            gender: "male", "female", or "unknown".
            has_joey: Whether this kangaroo has a joey in its pouch.
        """
        super().__init__(
            name, age, species="Kangaroo", fur_colour="red-brown", gender=gender
        )
        self._has_joey = has_joey
        self._hop_strength = 80

    @property
    def has_joey(self) -> bool:
        """Return True if this kangaroo has a joey in its pouch."""
        return self._has_joey

    @property
    def hop_strength(self) -> int:
        """Return the kangaroo's hop strength (0-100)."""
        return self._hop_strength

    def make_sound(self) -> str:
        """Return the sound a kangaroo makes."""
        return f"{self._name} makes a soft clucking sound!"

    def get_diet(self) -> str:
        """Return the kangaroo's diet type."""
        return "grass"

    def get_habitat_type(self) -> str:
        """Return the required habitat type for kangaroos."""
        return "outback_savanna"

    def hop(self) -> str:
        """
        Kangaroos love to hop.

        Returns:
            A string describing the hopping behaviour.
        """
        return f"{self._name} hops around energetically!"

    def box(self) -> str:
        """
        Kangaroos can box!

        Returns:
            A string describing the boxing behaviour.
        """
        return f"{self._name} stands up and boxes the air!"

    def to_dict(self) -> dict:
        """
        Serialise to dictionary for JSON save.

        Returns:
            A dictionary containing all kangaroo attributes for persistence.
        """
        data = super().to_dict()
        data["class"] = "Kangaroo"
        data["has_joey"] = self._has_joey
        data["hop_strength"] = self._hop_strength
        return data


class Wombat(Mammal):
    """
    Australian Wombat - burrowing marsupial with cube-shaped droppings.

    Wombats are short-legged, muscular quadrupedal marsupials native to
    Australia. They are excellent diggers and create extensive burrow systems.
    """

    def __init__(self, name: str, age: int, gender: str = "unknown") -> None:
        """
        Initialise a new Wombat.

        Args:
            name: The wombat's given name.
            age: Age in years (must be >= 0).
            gender: "male", "female", or "unknown".
        """
        super().__init__(
            name, age, species="Wombat", fur_colour="brown", gender=gender
        )
        self._burrow_depth = 3  # Metres

    @property
    def burrow_depth(self) -> int:
        """Return the depth of the wombat's burrow in metres."""
        return self._burrow_depth

    def make_sound(self) -> str:
        """Return the sound a wombat makes."""
        return f"{self._name} makes a grunting hiss!"

    def get_diet(self) -> str:
        """Return the wombat's diet type."""
        return "grass"

    def get_habitat_type(self) -> str:
        """Return the required habitat type for wombats."""
        return "outback_savanna"

    def burrow(self) -> str:
        """
        Wombats dig burrows.

        Returns:
            A string describing the burrowing behaviour.
        """
        return f"{self._name} digs industriously, burrow now {self._burrow_depth}m deep!"

    def to_dict(self) -> dict:
        """
        Serialise to dictionary for JSON save.

        Returns:
            A dictionary containing all wombat attributes for persistence.
        """
        data = super().to_dict()
        data["class"] = "Wombat"
        data["burrow_depth"] = self._burrow_depth
        return data


class Platypus(Mammal):
    """
    Australian Platypus - venomous egg-laying mammal.

    The platypus is a semi-aquatic egg-laying mammal endemic to Australia.
    Males have a venomous spur on their hind legs. They use their
    duck-like bill to detect prey in the water.
    """

    def __init__(self, name: str, age: int, gender: str = "unknown") -> None:
        """
        Initialise a new Platypus.

        Args:
            name: The platypus's given name.
            age: Age in years (must be >= 0).
            gender: "male", "female", or "unknown".
        """
        super().__init__(
            name, age, species="Platypus", fur_colour="brown", gender=gender
        )
        self._has_venomous_spur = gender == "male"  # Only males have venomous spurs

    @property
    def has_venomous_spur(self) -> bool:
        """Return True if this platypus has a venomous spur (males only)."""
        return self._has_venomous_spur

    def make_sound(self) -> str:
        """Return the sound a platypus makes."""
        return f"{self._name} makes a soft growling sound!"

    def get_diet(self) -> str:
        """Return the platypus's diet type."""
        return "insects"  # Actually eats invertebrates

    def get_habitat_type(self) -> str:
        """Return the required habitat type for platypuses."""
        return "billabong"

    def swim(self) -> str:
        """
        Platypus are excellent swimmers.

        Returns:
            A string describing the swimming behaviour.
        """
        return f"{self._name} glides through the water, using its bill to find food!"

    def to_dict(self) -> dict:
        """
        Serialise to dictionary for JSON save.

        Returns:
            A dictionary containing all platypus attributes for persistence.
        """
        data = super().to_dict()
        data["class"] = "Platypus"
        data["has_venomous_spur"] = self._has_venomous_spur
        return data


class TasmanianDevil(Mammal):
    """
    Tasmanian Devil - fierce carnivorous marsupial.

    The Tasmanian devil is a carnivorous marsupial native to Tasmania.
    They are known for their extremely loud and disturbing screeches,
    powerful bite, and feisty temperament.
    """

    def __init__(self, name: str, age: int, gender: str = "unknown") -> None:
        """
        Initialise a new Tasmanian Devil.

        Args:
            name: The devil's given name.
            age: Age in years (must be >= 0).
            gender: "male", "female", or "unknown".
        """
        super().__init__(
            name, age, species="TasmanianDevil", fur_colour="black", gender=gender
        )
        self._screech_volume = 100  # They're LOUD

    @property
    def screech_volume(self) -> int:
        """Return the devil's screech volume in decibels."""
        return self._screech_volume

    def make_sound(self) -> str:
        """Return the sound a Tasmanian devil makes."""
        return f"{self._name} lets out an ear-piercing screech!"

    def get_diet(self) -> str:
        """Return the Tasmanian devil's diet type."""
        return "meat"

    def get_habitat_type(self) -> str:
        """Return the required habitat type for Tasmanian devils."""
        return "outback_savanna"

    def screech(self) -> str:
        """
        Tasmanian Devils are known for their terrifying screech.

        Returns:
            A string describing the screeching behaviour.
        """
        return (
            f"{self._name} screeches loudly at {self._screech_volume} decibels! "
            "Everyone nearby covers their ears!"
        )

    def to_dict(self) -> dict:
        """
        Serialise to dictionary for JSON save.

        Returns:
            A dictionary containing all Tasmanian devil attributes for persistence.
        """
        data = super().to_dict()
        data["class"] = "TasmanianDevil"
        data["screech_volume"] = self._screech_volume
        return data


class Echidna(Mammal):
    """
    Australian Echidna - spiny egg-laying mammal.

    The echidna (or spiny anteater) is one of only two types of egg-laying
    mammals (monotremes). They are covered in sharp spines and curl into
    a ball for defence.
    """

    def __init__(self, name: str, age: int, gender: str = "unknown") -> None:
        """
        Initialise a new Echidna.

        Args:
            name: The echidna's given name.
            age: Age in years (must be >= 0).
            gender: "male", "female", or "unknown".
        """
        super().__init__(
            name, age, species="Echidna", fur_colour="brown-spiny", gender=gender
        )
        self._spine_count = 5000  # Approximate

    @property
    def spine_count(self) -> int:
        """Return the approximate number of spines on this echidna."""
        return self._spine_count

    def make_sound(self) -> str:
        """Return the sound an echidna makes."""
        return f"{self._name} makes a soft snuffling sound!"

    def get_diet(self) -> str:
        """Return the echidna's diet type."""
        return "insects"

    def get_habitat_type(self) -> str:
        """Return the required habitat type for echidnas."""
        return "outback_savanna"

    def curl_up(self) -> str:
        """
        Echidnas curl into a spiny ball for defence.

        Returns:
            A string describing the defensive curling behaviour.
        """
        return (
            f"{self._name} curls into a spiky ball, "
            f"presenting {self._spine_count} sharp spines!"
        )

    def to_dict(self) -> dict:
        """
        Serialise to dictionary for JSON save.

        Returns:
            A dictionary containing all echidna attributes for persistence.
        """
        data = super().to_dict()
        data["class"] = "Echidna"
        data["spine_count"] = self._spine_count
        return data
