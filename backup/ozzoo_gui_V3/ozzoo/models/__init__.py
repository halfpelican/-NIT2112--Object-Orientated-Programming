"""
OzZoo models package.

This package contains all domain models for the OzZoo application,
including animals, resources, enclosures, staff, and visitors.
"""
from ozzoo.models.animal import (
    Animal,
    Mammal,
    Bird,
    Reptile,
)
from ozzoo.models.resources import (
    Food,
    Medicine,
    FOOD_TYPES,
    MEDICINE_TYPES,
)
from ozzoo.models.staff import (
    ZooKeeper,
    Specialty,
    generate_random_keeper,
)
from ozzoo.models.enclosure import (
    Enclosure,
    EucalyptusGrove,
    OutbackSavanna,
    Billabong,
    RainforestAviary,
    ReptileHouse,
    ENCLOSURE_TYPES,
    create_enclosure,
)
from ozzoo.models.visitor import (
    Visitor,
    TicketType,
    generate_random_visitor,
    FIRST_NAMES,
    LAST_NAMES,
)
from ozzoo.models.zoo import (
    Zoo,
    save_game,
    load_game,
    create_default_zoo,
)

__all__ = [
    # Animal base classes
    "Animal",
    "Mammal",
    "Bird",
    "Reptile",
    # Resources
    "Food",
    "Medicine",
    "FOOD_TYPES",
    "MEDICINE_TYPES",
    # Staff
    "ZooKeeper",
    "Specialty",
    "generate_random_keeper",
    # Enclosures
    "Enclosure",
    "EucalyptusGrove",
    "OutbackSavanna",
    "Billabong",
    "RainforestAviary",
    "ReptileHouse",
    "ENCLOSURE_TYPES",
    "create_enclosure",
    # Visitors
    "Visitor",
    "TicketType",
    "generate_random_visitor",
    "FIRST_NAMES",
    "LAST_NAMES",
    # Zoo
    "Zoo",
    "save_game",
    "load_game",
    "create_default_zoo",
]
