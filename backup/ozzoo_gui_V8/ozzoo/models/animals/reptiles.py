"""
OzZoo Reptile Species Module
Contains all concrete reptile implementations.
"""

from __future__ import annotations
from ..animal import Reptile


class SaltwaterCroc(Reptile):
    """
    Australian Saltwater Crocodile - largest living reptile.
    Inheritance: Animal -> Reptile -> SaltwaterCroc (3 levels)
    """

    def __init__(self, name: str, age: int, gender: str = "unknown"):
        """
        Initialise a new Saltwater Crocodile.

        Args:
            name: The crocodile's given name.
            age: Age in years.
            gender: "male", "female", or "unknown".
        """
        super().__init__(name, age, species="SaltwaterCroc", is_venomous=False, gender=gender)
        self._length_metres = 4.5  # Average adult size
        self._bite_force = 3700  # PSI - strongest bite of any animal!

    @property
    def length_metres(self) -> float:
        """Return crocodile body length in metres."""
        return self._length_metres

    @property
    def bite_force(self) -> int:
        """Return estimated bite force in PSI."""
        return self._bite_force

    def make_sound(self) -> str:
        """Return the crocodile's vocalisation."""
        return f"{self._name} lets out a deep, rumbling bellow!"

    def get_diet(self) -> str:
        """Return the crocodile's diet category."""
        return "meat"

    def get_habitat_type(self) -> str:
        """Return the required habitat type for saltwater crocodiles."""
        return "billabong"

    def death_roll(self) -> str:
        """Crocodiles use the death roll to subdue prey."""
        return f"{self._name} performs a terrifying death roll with {self._bite_force} PSI bite force!"

    def submerge(self) -> str:
        """Crocs can stay submerged for long periods."""
        return f"{self._name} silently sinks beneath the water, only eyes visible..."

    def to_dict(self) -> dict:
        """
        Serialise the crocodile for persistence.

        Returns:
            Dictionary representation used in save files.
        """
        data = super().to_dict()
        data["class"] = "SaltwaterCroc"
        data["length_metres"] = self._length_metres
        data["bite_force"] = self._bite_force
        return data


class FrilledLizard(Reptile):
    """
    Australian Frilled Lizard - known for its spectacular neck frill.
    """

    def __init__(self, name: str, age: int, gender: str = "unknown"):
        """
        Initialise a new Frilled Lizard.

        Args:
            name: The lizard's given name.
            age: Age in years.
            gender: "male", "female", or "unknown".
        """
        super().__init__(name, age, species="FrilledLizard", is_venomous=False, gender=gender)
        self._frill_diameter_cm = 30  # When extended

    @property
    def frill_diameter_cm(self) -> int:
        """Return maximum frill diameter in centimetres."""
        return self._frill_diameter_cm

    def make_sound(self) -> str:
        """Return the frilled lizard's defensive vocalisation."""
        return f"{self._name} hisses menacingly!"

    def get_diet(self) -> str:
        """Return the lizard's diet category."""
        return "insects"

    def get_habitat_type(self) -> str:
        """Return the required habitat type for frilled lizards."""
        return "reptile_house"

    def display_frill(self) -> str:
        """Frilled lizards extend their frill when threatened or displaying."""
        self._happiness = min(self.MAX_HAPPINESS, self._happiness + 5)
        return f"{self._name} dramatically extends its {self._frill_diameter_cm}cm frill and opens its mouth wide!"

    def run_bipedally(self) -> str:
        """Frilled lizards can run on two legs."""
        return f"{self._name} runs comically on its hind legs with frill bouncing!"

    def to_dict(self) -> dict:
        """
        Serialise the frilled lizard for persistence.

        Returns:
            Dictionary representation used in save files.
        """
        data = super().to_dict()
        data["class"] = "FrilledLizard"
        data["frill_diameter_cm"] = self._frill_diameter_cm
        return data


class Goanna(Reptile):
    """
    Australian Goanna - agile monitor lizard and opportunistic predator.
    """

    def __init__(self, name: str, age: int, gender: str = "unknown"):
        """
        Initialise a new Goanna.

        Args:
            name: The goanna's given name.
            age: Age in years.
            gender: "male", "female", or "unknown".
        """
        super().__init__(name, age, species="Goanna", is_venomous=False, gender=gender)
        self._climb_speed = 65

    @property
    def climb_speed(self) -> int:
        """Return climbing agility rating (0-100)."""
        return self._climb_speed

    def make_sound(self) -> str:
        """Return the goanna's vocal/behaviour cue."""
        return f"{self._name} lets out a low hiss and flicks its tongue."

    def get_diet(self) -> str:
        """Return the goanna's diet category."""
        return "meat"

    def get_habitat_type(self) -> str:
        """Return the goanna's primary habitat type."""
        # Primary habitat remains Eucalyptus Grove; Reptile House support is handled
        # by enclosure compatibility rules.
        return "eucalyptus_grove"

    def bask(self) -> str:
        """Goannas thermoregulate by basking in warm sunlight."""
        return f"{self._name} sprawls on a warm log to bask."

    def to_dict(self) -> dict:
        """
        Serialise the goanna for persistence.

        Returns:
            Dictionary representation used in save files.
        """
        data = super().to_dict()
        data["class"] = "Goanna"
        data["climb_speed"] = self._climb_speed
        return data


class CarpetPython(Reptile):
    """
    Australian Carpet Python - medium-sized non-venomous constrictor.
    """

    def __init__(self, name: str, age: int, gender: str = "unknown"):
        """
        Initialise a new Carpet Python.

        Args:
            name: The python's given name.
            age: Age in years.
            gender: "male", "female", or "unknown".
        """
        super().__init__(name, age, species="CarpetPython", is_venomous=False, gender=gender)
        self._length_metres = 2.4

    @property
    def length_metres(self) -> float:
        """Return body length in metres."""
        return self._length_metres

    def make_sound(self) -> str:
        """Return a short behavioural description/sound cue."""
        return f"{self._name} gives a soft hiss and coils tightly."

    def get_diet(self) -> str:
        """Return the python's diet category."""
        return "meat"

    def get_habitat_type(self) -> str:
        """Return the python's primary habitat type."""
        # Primary habitat is Eucalyptus Grove; Reptile House is supported
        # by compatibility rules.
        return "eucalyptus_grove"

    def constrict(self) -> str:
        """Carpet pythons subdue prey by constriction."""
        return f"{self._name} wraps into a powerful constricting coil."

    def to_dict(self) -> dict:
        """
        Serialise the carpet python for persistence.

        Returns:
            Dictionary representation used in save files.
        """
        data = super().to_dict()
        data["class"] = "CarpetPython"
        data["length_metres"] = self._length_metres
        return data


class EasternBrownSnake(Reptile):
    """
    Eastern Brown Snake - highly venomous and fast-moving predator.
    """

    def __init__(self, name: str, age: int, gender: str = "unknown"):
        """
        Initialise a new Eastern Brown Snake.

        Args:
            name: The snake's given name.
            age: Age in years.
            gender: "male", "female", or "unknown".
        """
        super().__init__(name, age, species="EasternBrownSnake", is_venomous=True, gender=gender)
        self._venom_potency = 95

    @property
    def venom_potency(self) -> int:
        """Return venom potency rating (0-100)."""
        return self._venom_potency

    def make_sound(self) -> str:
        """Return a behavioural warning cue."""
        return f"{self._name} flattens its neck and hisses sharply."

    def get_diet(self) -> str:
        """Return the snake's diet category."""
        return "meat"

    def get_habitat_type(self) -> str:
        """Return the snake's primary habitat type."""
        # Primary habitat is Eucalyptus Grove; Reptile House is supported
        # by compatibility rules.
        return "eucalyptus_grove"

    def strike(self) -> str:
        """Eastern browns are known for fast defensive strikes."""
        return f"{self._name} lashes out with a rapid warning strike."

    def to_dict(self) -> dict:
        """
        Serialise the eastern brown snake for persistence.

        Returns:
            Dictionary representation used in save files.
        """
        data = super().to_dict()
        data["class"] = "EasternBrownSnake"
        data["venom_potency"] = self._venom_potency
        return data


class BlueTonguedSkink(Reptile):
    """
    Blue-tongued Skink - small, harmless reptile.
    """

    def __init__(self, name: str, age: int, gender: str = "unknown"):
        """
        Initialise a new Blue-Tongued Skink.

        Args:
            name: The skink's given name.
            age: Age in years.
            gender: "male", "female", or "unknown".
        """
        super().__init__(name, age, species="BlueTonguedSkink", is_venomous=False, gender=gender)
        self._tongue_colour = "blue"

    @property
    def tongue_colour(self) -> str:
        """Return the skink's tongue colour."""
        return self._tongue_colour

    def make_sound(self) -> str:
        """Return a short behavioural description/sound cue."""
        return f"{self._name} puffs up and lets out a tiny hiss."

    def get_diet(self) -> str:
        """Return the skink's diet category."""
        return "insects"

    def get_habitat_type(self) -> str:
        """Return the required habitat type for blue-tongued skinks."""
        return "reptile_house"

    def display_tongue(self) -> str:
        """Blue-tongued skinks flash their tongue as a deterrent."""
        return f"{self._name} sticks out its bright {self._tongue_colour} tongue."

    def to_dict(self) -> dict:
        """
        Serialise the blue-tongued skink for persistence.

        Returns:
            Dictionary representation used in save files.
        """
        data = super().to_dict()
        data["class"] = "BlueTonguedSkink"
        data["tongue_colour"] = self._tongue_colour
        return data
