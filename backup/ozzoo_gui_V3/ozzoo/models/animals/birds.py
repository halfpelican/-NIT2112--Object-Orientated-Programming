"""
OzZoo Bird Species Module
Contains all concrete bird implementations.
"""

from __future__ import annotations
from ..animal import Bird


class Emu(Bird):
    """
    Australian Emu - large flightless bird.
    Inheritance: Animal -> Bird -> Emu (3 levels)
    """
    
    def __init__(self, name: str, age: int, gender: str = "unknown"):
        super().__init__(name, age, species="Emu", wingspan=0.5, can_fly=False, gender=gender)
        self._running_speed = 50  # km/h - they're fast!
    
    @property
    def running_speed(self) -> int:
        return self._running_speed
    
    def make_sound(self) -> str:
        return f"{self._name} makes a deep booming drum-like sound!"
    
    def get_diet(self) -> str:
        return "grass"  # Actually omnivorous but primarily plants
    
    def get_habitat_type(self) -> str:
        return "rainforest_aviary"  # Large aviary space
    
    def run(self) -> str:
        """Emus are excellent runners."""
        return f"{self._name} sprints across the enclosure at {self._running_speed} km/h!"
    
    def to_dict(self) -> dict:
        data = super().to_dict()
        data["class"] = "Emu"
        data["running_speed"] = self._running_speed
        return data


class WedgeTailedEagle(Bird):
    """
    Australian Wedge-Tailed Eagle - largest bird of prey in Australia.
    """
    
    def __init__(self, name: str, age: int, gender: str = "unknown"):
        super().__init__(name, age, species="WedgeTailedEagle", wingspan=2.8, can_fly=True, gender=gender)
        self._hunting_skill = 85  # Percentage
    
    @property
    def hunting_skill(self) -> int:
        return self._hunting_skill
    
    def make_sound(self) -> str:
        return f"{self._name} lets out a high-pitched whistling call!"
    
    def get_diet(self) -> str:
        return "meat"
    
    def get_habitat_type(self) -> str:
        return "rainforest_aviary"
    
    def hunt(self) -> str:
        """Wedge-tailed eagles are skilled hunters."""
        return f"{self._name} spots prey from high above with {self._hunting_skill}% accuracy!"
    
    def soar(self) -> str:
        """Eagles can soar for hours on thermal currents."""
        return f"{self._name} soars majestically on thermals, {self._wingspan}m wingspan fully extended!"
    
    def to_dict(self) -> dict:
        data = super().to_dict()
        data["class"] = "WedgeTailedEagle"
        data["hunting_skill"] = self._hunting_skill
        return data
