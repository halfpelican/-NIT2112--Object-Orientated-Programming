"""Factory helpers for creating clubs with default configuration by type."""

from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
# =============================================================================
# FACTORY PATTERN
# =============================================================================


class ClubFactory:
    """Factory for creating clubs with predefined configurations."""
    
    _club_counter = 0
    
    @classmethod
    def _generate_club_id(cls) -> str:
        """Generate club id."""
        cls._club_counter += 1
        return f"CLUB{cls._club_counter:04d}"
    
    @classmethod
    def create_club(
        cls,
        club_type: str,
        name: str,
        budget: float,
        **kwargs
    ) -> Club:
        """
        Create a club of the specified type with default configuration.
        
        Args:
            club_type: Type of club ('academic', 'social', 'sports', 'cultural')
            name: Name of the club
            budget: Initial budget allocation
            **kwargs: Additional configuration (e.g., equipment_budget for sports)
        
        Returns:
            Configured Club instance
        """
        club_id = cls._generate_club_id()
        
        type_mapping = {
            "academic": ClubType._ACADEMIC,
            "social": ClubType._SOCIAL,
            "sports": ClubType._SPORTS,
            "cultural": ClubType._CULTURAL
        }
        
        if club_type.lower() not in type_mapping:
            raise ValueError(f"Unknown club type: {club_type}")
        
        club = Club(club_id, name, type_mapping[club_type.lower()], budget)
        
        # Add default resources based on type
        if club_type.lower() == "academic":
            club.add_resource(Venue("VEN-LEC", "Lecture Hall", 100, has_av_equipment=True))
        elif club_type.lower() == "sports":
            equipment_budget = kwargs.get("equipment_budget", 0)
            if equipment_budget > 0:
                club._budget.add_allocation(equipment_budget, "Equipment budget")
            club.add_resource(Venue("VEN-GYM", "Sports Hall", 200))
            club.add_resource(Equipment("EQ-BALLS", "Sports Balls", 20))
        elif club_type.lower() == "social":
            club.add_resource(Venue("VEN-COMMON", "Common Room", 50))
        elif club_type.lower() == "cultural":
            club.add_resource(Venue("VEN-THEATER", "Theater", 150, has_av_equipment=True))
            club.add_resource(Equipment("EQ-COSTUMES", "Costume Sets", 10))
        
        return club

