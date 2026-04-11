"""
OzZoo Visitor Module

Contains the Visitor class representing zoo guests.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from enum import Enum
import random

if TYPE_CHECKING:
    from ozzoo.models.animals import Animal


class TicketType(Enum):
    """Ticket types with their base prices."""
    CHILD = ("Child", 15.0)
    ADULT = ("Adult", 30.0)
    SENIOR = ("Senior", 20.0)
    FAMILY = ("Family (2+2)", 80.0)
    VIP = ("VIP Experience", 100.0)
    
    def __init__(self, display_name: str, base_price: float):
        """
        Store display metadata for each ticket type enum member.

        Args:
            display_name: Human-readable ticket name.
            base_price: Base ticket price in dollars.
        """
        self.display_name = display_name
        self.base_price = base_price


class Visitor:
    """
    Represents a visitor to the zoo.
    
    Visitors have satisfaction levels that affect donations and return likelihood.
    
    Attributes:
        _visitor_id (str): Unique identifier for the visitor.
        _name (str): The visitor's name.
        _ticket_type (TicketType): The type of ticket purchased.
        _satisfaction (int): Satisfaction level (0-100).
        _animals_viewed (list[str]): List of animal names viewed.
        _money_spent (float): Total money spent at the zoo.
        _has_donated (bool): Whether the visitor has made a donation.
    """
    
    def __init__(
        self,
        visitor_id: str,
        name: str,
        ticket_type: TicketType = TicketType.ADULT
    ):
        """
        Initialise a new Visitor.
        
        Args:
            visitor_id: Unique identifier for the visitor.
            name: The visitor's name.
            ticket_type: The type of ticket purchased (default: ADULT).
        """
        self._visitor_id = visitor_id
        self._name = name
        self._ticket_type = ticket_type
        self._satisfaction = 70  # Start moderately satisfied (0-100)
        self._animals_viewed: list[str] = []  # List of animal names viewed
        self._money_spent = ticket_type.base_price  # Track total spending
        self._has_donated = False
    
    # Properties
    @property
    def visitor_id(self) -> str:
        """Get the visitor's unique identifier."""
        return self._visitor_id
    
    @property
    def name(self) -> str:
        """Get the visitor's name."""
        return self._name
    
    @property
    def ticket_type(self) -> TicketType:
        """Get the visitor's ticket type."""
        return self._ticket_type
    
    @property
    def satisfaction(self) -> int:
        """Get the visitor's current satisfaction level (0-100)."""
        return self._satisfaction
    
    @property
    def money_spent(self) -> float:
        """Get the total amount of money the visitor has spent."""
        return self._money_spent
    
    @property
    def is_happy(self) -> bool:
        """Check if satisfaction > 70."""
        return self._satisfaction > 70
    
    @property
    def is_unhappy(self) -> bool:
        """Check if satisfaction < 30."""
        return self._satisfaction < 30
    
    @property
    def animals_viewed(self) -> list[str]:
        """Get a copy of the list of animal names viewed."""
        return self._animals_viewed.copy()
    
    @property
    def has_donated(self) -> bool:
        """Check if the visitor has made a donation."""
        return self._has_donated
    
    def view_animal(self, animal: Animal) -> str:
        """
        View an animal, affecting satisfaction based on animal's condition.
        
        Satisfaction changes:
        - Healthy, happy animal: +5
        - Sick animal: -10
        - Stressed/unhappy animal: -5
        - Already viewed this animal: +1 (slight bonus for revisiting favourites)
        
        Args:
            animal: The Animal object to view.
            
        Returns:
            A string describing the viewing experience.
        """
        animal_name = animal.name
        already_viewed = animal_name in self._animals_viewed
        
        # Check animal condition and adjust satisfaction accordingly
        if animal.is_sick:
            self._satisfaction = max(0, self._satisfaction - 10)
            message = (
                f"{self._name} is concerned about {animal_name} - "
                f"the poor thing looks unwell! 😟"
            )
        elif hasattr(animal, 'happiness') and animal.happiness < 30:
            # Animal is stressed/unhappy
            self._satisfaction = max(0, self._satisfaction - 5)
            message = (
                f"{self._name} notices {animal_name} seems stressed "
                f"and unhappy. 😕"
            )
        elif already_viewed:
            # Revisiting a favourite - small bonus
            self._satisfaction = min(100, self._satisfaction + 1)
            message = (
                f"{self._name} enjoys seeing {animal_name} again - "
                f"one of their favourites! 🥰"
            )
        else:
            # Healthy, happy animal - good experience
            self._satisfaction = min(100, self._satisfaction + 5)
            message = (
                f"{self._name} loves watching {animal_name}! "
                f"What a beautiful creature! 😊"
            )
        
        # Track viewed animal if not already tracked
        if not already_viewed:
            self._animals_viewed.append(animal_name)
        
        return message
    
    def buy_snack(self, cost: float) -> bool:
        """
        Buy a snack. Increases satisfaction by 3.
        
        Args:
            cost: The cost of the snack.
            
        Returns:
            True if purchase successful.
        """
        self._money_spent += cost
        self._satisfaction = min(100, self._satisfaction + 3)
        return True
    
    def donate(self, amount: float) -> float:
        """
        Make a donation. Only happy visitors donate.
        
        Args:
            amount: The desired donation amount.
            
        Returns:
            The actual donation amount (0 if not happy enough).
            VIP visitors donate 50% more.
        """
        if self._satisfaction < 60:
            return 0.0
        
        actual_amount = amount
        if self._ticket_type == TicketType.VIP:
            actual_amount *= 1.5
        
        self._has_donated = True
        self._satisfaction = min(100, self._satisfaction + 5)  # Donating feels good
        return actual_amount
    
    def calculate_donation_chance(self) -> float:
        """
        Calculate the probability that this visitor will donate.
        
        Based on satisfaction level.
        
        Returns:
            A float between 0.0 and 0.5 representing donation probability.
        """
        if self._satisfaction < 50:
            return 0.0
        return min(0.5, (self._satisfaction - 50) / 100)  # Max 50% chance
    
    def random_donation(self, max_amount: float = 50.0) -> float:
        """
        Randomly decide whether to donate based on satisfaction.
        
        Args:
            max_amount: The maximum donation amount (default: 50.0).
            
        Returns:
            The donation amount (0 if no donation).
        """
        if random.random() < self.calculate_donation_chance():
            amount = random.uniform(5.0, max_amount) * (self._satisfaction / 100)
            return self.donate(amount)
        return 0.0
    
    def adjust_satisfaction(self, amount: int, reason: str = "") -> None:
        """
        Adjust satisfaction by the given amount (positive or negative).
        
        Args:
            amount: The amount to adjust satisfaction by.
            reason: Optional reason for the adjustment (for logging).
        """
        self._satisfaction = max(0, min(100, self._satisfaction + amount))
    
    def get_status(self) -> dict:
        """
        Return current status as dictionary.
        
        Returns:
            A dictionary containing the visitor's current status.
        """
        return {
            "id": self._visitor_id,
            "name": self._name,
            "ticket_type": self._ticket_type.name,
            "satisfaction": self._satisfaction,
            "animals_viewed": len(self._animals_viewed),
            "money_spent": self._money_spent,
            "is_happy": self.is_happy,
            "has_donated": self._has_donated
        }
    
    def to_dict(self) -> dict:
        """
        Serialise to dictionary for JSON save.
        
        Returns:
            A dictionary representation of the visitor for serialisation.
        """
        return {
            "visitor_id": self._visitor_id,
            "name": self._name,
            "ticket_type": self._ticket_type.name,
            "satisfaction": self._satisfaction,
            "animals_viewed": self._animals_viewed,
            "money_spent": self._money_spent,
            "has_donated": self._has_donated
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> Visitor:
        """
        Deserialise from dictionary.
        
        Args:
            data: A dictionary containing visitor data.
            
        Returns:
            A new Visitor instance created from the dictionary data.
        """
        visitor = cls(
            visitor_id=data["visitor_id"],
            name=data["name"],
            ticket_type=TicketType[data["ticket_type"]]
        )
        visitor._satisfaction = data["satisfaction"]
        visitor._animals_viewed = data["animals_viewed"]
        visitor._money_spent = data["money_spent"]
        visitor._has_donated = data["has_donated"]
        return visitor
    
    def __str__(self) -> str:
        """Return a string representation of the visitor."""
        if self.is_happy:
            mood = "😊"
        elif self._satisfaction > 40:
            mood = "😐"
        else:
            mood = "😞"
        return (
            f"{mood} {self._name} ({self._ticket_type.display_name}) - "
            f"Satisfaction: {self._satisfaction}%"
        )
    
    def __repr__(self) -> str:
        """Return a detailed string representation of the visitor."""
        return (
            f"Visitor(visitor_id={self._visitor_id!r}, name={self._name!r}, "
            f"ticket_type={self._ticket_type.name}, satisfaction={self._satisfaction})"
        )


# Visitor name generator for random visitors
FIRST_NAMES = [
    "Emma", "Liam", "Olivia", "Noah", "Ava", "Oliver", "Isabella", "William",
    "Sophia", "James", "Mia", "Benjamin", "Charlotte", "Lucas", "Amelia",
    "Bruce", "Sheila", "Barry", "Karen", "Dazza", "Shazza", "Bazza", "Narelle"
]

LAST_NAMES = [
    "Smith", "Jones", "Williams", "Brown", "Wilson", "Taylor", "Anderson",
    "Thompson", "White", "Martin", "Clark", "Lewis", "Walker", "Hall",
    "Kelly", "Murphy", "O'Brien", "Ryan", "Chen", "Singh", "Nguyen"
]


def generate_random_visitor(visitor_id: str) -> Visitor:
    """
    Generate a visitor with random name and ticket type.
    
    Args:
        visitor_id: The unique identifier for the new visitor.
        
    Returns:
        A new Visitor instance with a random name and ticket type.
    """
    name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
    # Weight ticket types (more adults and families)
    ticket_weights = [0.15, 0.40, 0.15, 0.25, 0.05]  # child, adult, senior, family, vip
    ticket_type = random.choices(list(TicketType), weights=ticket_weights)[0]
    return Visitor(visitor_id, name, ticket_type)
