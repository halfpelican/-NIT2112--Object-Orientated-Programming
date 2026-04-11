"""
OzZoo Factory Pattern Module
Implements the Factory design pattern for creating animals.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Type, List, Any

if TYPE_CHECKING:
    from ..models.animal import Animal

# Import all animal classes
from ..models.animals.mammals import (
    Koala, Kangaroo, Wombat, Platypus, TasmanianDevil, Echidna
)
from ..models.animals.birds import Kookaburra, Emu, WedgeTailedEagle
from ..models.animals.reptiles import SaltwaterCroc, FrilledLizard


class AnimalFactory:
    """
    Factory for creating different types of Australian animals.
    
    Usage:
        factory = AnimalFactory()
        koala = factory.create_animal("koala", name="Blinky", age=3)
        kangaroo = factory.create_animal("kangaroo", name="Skippy", age=5)
    """
    
    # Animal type to class mapping
    _animal_types: Dict[str, Type[Animal]] = {
        "koala": Koala,
        "kangaroo": Kangaroo,
        "wombat": Wombat,
        "platypus": Platypus,
        "tasmanian_devil": TasmanianDevil,
        "tasmaniandevil": TasmanianDevil,  # Alternative spelling
        "echidna": Echidna,
        "kookaburra": Kookaburra,
        "emu": Emu,
        "wedge_tailed_eagle": WedgeTailedEagle,
        "wedgetailedeagle": WedgeTailedEagle,  # Alternative spelling
        "saltwater_croc": SaltwaterCroc,
        "saltwatercroc": SaltwaterCroc,  # Alternative spelling
        "frilled_lizard": FrilledLizard,
        "frilledlizard": FrilledLizard,  # Alternative spelling
    }
    
    # Animal info for UI display
    _animal_info: Dict[str, Dict[str, Any]] = {
        "koala": {"display_name": "Koala", "category": "mammal", "habitat": "eucalyptus_grove", "diet": "eucalyptus", "cost": 500},
        "kangaroo": {"display_name": "Kangaroo", "category": "mammal", "habitat": "outback_savanna", "diet": "grass", "cost": 400},
        "wombat": {"display_name": "Wombat", "category": "mammal", "habitat": "outback_savanna", "diet": "grass", "cost": 350},
        "platypus": {"display_name": "Platypus", "category": "mammal", "habitat": "billabong", "diet": "insects", "cost": 600},
        "tasmanian_devil": {"display_name": "Tasmanian Devil", "category": "mammal", "habitat": "outback_savanna", "diet": "meat", "cost": 450},
        "echidna": {"display_name": "Echidna", "category": "mammal", "habitat": "outback_savanna", "diet": "insects", "cost": 380},
        "kookaburra": {"display_name": "Kookaburra", "category": "bird", "habitat": "rainforest_aviary", "diet": "meat", "cost": 350},
        "emu": {"display_name": "Emu", "category": "bird", "habitat": "rainforest_aviary", "diet": "grass", "cost": 300},
        "wedge_tailed_eagle": {"display_name": "Wedge-Tailed Eagle", "category": "bird", "habitat": "rainforest_aviary", "diet": "meat", "cost": 550},
        "saltwater_croc": {"display_name": "Saltwater Crocodile", "category": "reptile", "habitat": "billabong", "diet": "meat", "cost": 700},
        "frilled_lizard": {"display_name": "Frilled Lizard", "category": "reptile", "habitat": "reptile_house", "diet": "insects", "cost": 250},
    }
    
    @classmethod
    def create_animal(cls, animal_type: str, **kwargs) -> Animal:
        """
        Create an animal of the specified type.
        
        Args:
            animal_type: Type of animal (e.g., "koala", "kangaroo")
            **kwargs: Animal-specific attributes (name, age, gender, etc.)
            
        Returns:
            Animal: The created animal instance
            
        Raises:
            ValueError: If animal_type is unknown
            TypeError: If required kwargs are missing
        """
        normalised_type = animal_type.lower().replace(" ", "_").replace("-", "_")
        
        if normalised_type not in cls._animal_types:
            available = ", ".join(cls.get_available_types())
            raise ValueError(f"Unknown animal type: '{animal_type}'. Available: {available}")
        
        animal_class = cls._animal_types[normalised_type]
        
        try:
            return animal_class(**kwargs)
        except TypeError as e:
            raise TypeError(f"Missing required parameter for {animal_type}: {e}")
    
    @classmethod
    def get_available_types(cls) -> List[str]:
        """Return list of canonical animal type names (no duplicates)."""
        # Return only the canonical names (with underscores)
        canonical = set()
        for key in cls._animal_types.keys():
            if "_" in key or key in ["koala", "kangaroo", "wombat", "platypus", "echidna", "emu"]:
                canonical.add(key.replace("_", " ").title().replace(" ", "_").lower())
        return sorted(list(canonical))
    
    @classmethod
    def get_animal_info(cls, animal_type: str) -> Dict[str, Any]:
        """Get info about an animal type for UI display."""
        normalised = animal_type.lower().replace(" ", "_").replace("-", "_")
        # Handle alternative spellings
        if normalised == "tasmaniandevil":
            normalised = "tasmanian_devil"
        elif normalised == "wedgetailedeagle":
            normalised = "wedge_tailed_eagle"
        elif normalised == "saltwatercroc":
            normalised = "saltwater_croc"
        elif normalised == "frilledlizard":
            normalised = "frilled_lizard"
        
        if normalised not in cls._animal_info:
            raise ValueError(f"Unknown animal type: {animal_type}")
        return cls._animal_info[normalised].copy()
    
    @classmethod
    def get_all_animal_info(cls) -> Dict[str, Dict[str, Any]]:
        """Get info for all animal types."""
        return {k: v.copy() for k, v in cls._animal_info.items()}
    
    @classmethod
    def get_animals_by_category(cls, category: str) -> List[str]:
        """Get all animal types in a category (mammal, bird, reptile)."""
        return [k for k, v in cls._animal_info.items() if v["category"] == category]
    
    @classmethod
    def get_animals_by_habitat(cls, habitat: str) -> List[str]:
        """Get all animal types suited for a habitat."""
        return [k for k, v in cls._animal_info.items() if v["habitat"] == habitat]
    
    @classmethod
    def register_type(cls, type_name: str, animal_class: Type[Animal], info: Dict[str, Any]) -> None:
        """
        Register a new animal type (for extensibility).
        
        Args:
            type_name: Canonical name for the animal type
            animal_class: The class to instantiate
            info: Dictionary with display_name, category, habitat, diet, cost
        """
        normalised = type_name.lower().replace(" ", "_")
        cls._animal_types[normalised] = animal_class
        cls._animal_info[normalised] = info


def create_animal(animal_type: str, **kwargs) -> Animal:
    """Convenience function for creating animals."""
    return AnimalFactory.create_animal(animal_type, **kwargs)
