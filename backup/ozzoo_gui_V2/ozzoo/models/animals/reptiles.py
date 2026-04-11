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
        super().__init__(name, age, species="SaltwaterCroc", is_venomous=False, gender=gender)
        self._length_metres = 4.5  # Average adult size
        self._bite_force = 3700  # PSI - strongest bite of any animal!

    @property
    def length_metres(self) -> float:
        return self._length_metres

    @property
    def bite_force(self) -> int:
        return self._bite_force

    def make_sound(self) -> str:
        return f"{self._name} lets out a deep, rumbling bellow!"

    def get_diet(self) -> str:
        return "meat"

    def get_habitat_type(self) -> str:
        return "billabong"

    def death_roll(self) -> str:
        """Crocodiles use the death roll to subdue prey."""
        return f"{self._name} performs a terrifying death roll with {self._bite_force} PSI bite force!"

    def submerge(self) -> str:
        """Crocs can stay submerged for long periods."""
        return f"{self._name} silently sinks beneath the water, only eyes visible..."

    def to_dict(self) -> dict:
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
        super().__init__(name, age, species="FrilledLizard", is_venomous=False, gender=gender)
        self._frill_diameter_cm = 30  # When extended

    @property
    def frill_diameter_cm(self) -> int:
        return self._frill_diameter_cm

    def make_sound(self) -> str:
        return f"{self._name} hisses menacingly!"

    def get_diet(self) -> str:
        return "insects"

    def get_habitat_type(self) -> str:
        return "reptile_house"

    def display_frill(self) -> str:
        """Frilled lizards extend their frill when threatened or displaying."""
        self._happiness = min(self.MAX_HAPPINESS, self._happiness + 5)
        return f"{self._name} dramatically extends its {self._frill_diameter_cm}cm frill and opens its mouth wide!"

    def run_bipedally(self) -> str:
        """Frilled lizards can run on two legs."""
        return f"{self._name} runs comically on its hind legs with frill bouncing!"

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["class"] = "FrilledLizard"
        data["frill_diameter_cm"] = self._frill_diameter_cm
        return data
