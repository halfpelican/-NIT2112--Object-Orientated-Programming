"""
OzZoo Bird Species Module
Contains all concrete bird implementations.
"""

from __future__ import annotations
from ..animal import Bird


class Kookaburra(Bird):
    """
    Australian Kookaburra - the laughing kingfisher.

    Inheritance: Animal -> Bird -> Kookaburra (3 levels)

    Kookaburras are terrestrial tree kingfishers native to Australia and
    New Guinea. They are famous for their loud, distinctive "laughing" call
    that sounds like human laughter and often signals the start of dawn.
    """

    def __init__(self, name: str, age: int, gender: str = "unknown") -> None:
        """
        Initialise a new Kookaburra.

        Args:
            name: The kookaburra's given name.
            age: Age in years (must be >= 0).
            gender: "male", "female", or "unknown".
        """
        super().__init__(name, age, species="Kookaburra", wingspan=0.65, can_fly=True, gender=gender)
        self._laugh_volume = 90  # They're loud!

    @property
    def laugh_volume(self) -> int:
        """Return the kookaburra's laugh volume in decibels."""
        return self._laugh_volume

    def make_sound(self) -> str:
        """Return the iconic laughing call of the kookaburra."""
        return f"{self._name} lets out a loud, cackling laugh: 'Kook-kook-kook-ka-ka-ka!'"

    def get_diet(self) -> str:
        """Return the kookaburra's diet type."""
        return "meat"  # They eat insects, small reptiles, and mice

    def get_habitat_type(self) -> str:
        """Return the required habitat type for kookaburras."""
        return "rainforest_aviary"

    def laugh(self) -> str:
        """
        Kookaburras are famous for their laughing call.

        Increases happiness by 10 (they enjoy making noise!).

        Returns:
            A string describing the laughing behaviour.
        """
        self._happiness = min(self.MAX_HAPPINESS, self._happiness + 10)
        return (
            f"{self._name} throws back their head and laughs loudly at "
            f"{self._laugh_volume} decibels! The whole zoo can hear it!"
        )

    def hunt_snakes(self) -> str:
        """
        Kookaburras are skilled snake hunters.

        Returns:
            A string describing the hunting behaviour.
        """
        return f"{self._name} spots a snake and swoops down to grab it!"

    def to_dict(self) -> dict:
        """
        Serialise to dictionary for JSON save.

        Returns:
            A dictionary containing all kookaburra attributes for persistence.
        """
        data = super().to_dict()
        data["class"] = "Kookaburra"
        data["laugh_volume"] = self._laugh_volume
        return data


class Emu(Bird):
    """
    Australian Emu - large flightless bird.
    Inheritance: Animal -> Bird -> Emu (3 levels)
    """
    
    def __init__(self, name: str, age: int, gender: str = "unknown"):
        """
        Initialise a new Emu.

        Args:
            name: The emu's given name.
            age: Age in years.
            gender: "male", "female", or "unknown".
        """
        super().__init__(name, age, species="Emu", wingspan=0.5, can_fly=False, gender=gender)
        self._running_speed = 50  # km/h - they're fast!
    
    @property
    def running_speed(self) -> int:
        """Return the emu's top running speed in km/h."""
        return self._running_speed
    
    def make_sound(self) -> str:
        """Return the emu's characteristic vocalisation."""
        return f"{self._name} makes a deep booming drum-like sound!"
    
    def get_diet(self) -> str:
        """Return the emu's primary diet category."""
        return "grass"  # Actually omnivorous but primarily plants
    
    def get_habitat_type(self) -> str:
        """Return the required habitat type for emus."""
        return "rainforest_aviary"  # Large aviary space
    
    def run(self) -> str:
        """Emus are excellent runners."""
        return f"{self._name} sprints across the enclosure at {self._running_speed} km/h!"
    
    def to_dict(self) -> dict:
        """
        Serialise the emu for persistence.

        Returns:
            Dictionary representation used in save files.
        """
        data = super().to_dict()
        data["class"] = "Emu"
        data["running_speed"] = self._running_speed
        return data


class WedgeTailedEagle(Bird):
    """
    Australian Wedge-Tailed Eagle - largest bird of prey in Australia.
    """
    
    def __init__(self, name: str, age: int, gender: str = "unknown"):
        """
        Initialise a new Wedge-Tailed Eagle.

        Args:
            name: The eagle's given name.
            age: Age in years.
            gender: "male", "female", or "unknown".
        """
        super().__init__(name, age, species="WedgeTailedEagle", wingspan=2.8, can_fly=True, gender=gender)
        self._hunting_skill = 85  # Percentage
    
    @property
    def hunting_skill(self) -> int:
        """Return hunting proficiency as a percentage score."""
        return self._hunting_skill
    
    def make_sound(self) -> str:
        """Return the eagle's call."""
        return f"{self._name} lets out a high-pitched whistling call!"
    
    def get_diet(self) -> str:
        """Return the eagle's diet category."""
        return "meat"
    
    def get_habitat_type(self) -> str:
        """Return the required habitat type for wedge-tailed eagles."""
        return "rainforest_aviary"
    
    def hunt(self) -> str:
        """Wedge-tailed eagles are skilled hunters."""
        return f"{self._name} spots prey from high above with {self._hunting_skill}% accuracy!"
    
    def soar(self) -> str:
        """Eagles can soar for hours on thermal currents."""
        return f"{self._name} soars majestically on thermals, {self._wingspan}m wingspan fully extended!"
    
    def to_dict(self) -> dict:
        """
        Serialise the eagle for persistence.

        Returns:
            Dictionary representation used in save files.
        """
        data = super().to_dict()
        data["class"] = "WedgeTailedEagle"
        data["hunting_skill"] = self._hunting_skill
        return data
