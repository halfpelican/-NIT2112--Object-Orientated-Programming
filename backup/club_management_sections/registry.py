"""Singleton registry for storing and querying clubs globally."""

from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
# =============================================================================
# SINGLETON PATTERN - Club Registry
# =============================================================================


class SingletonMeta(type):
    """Metaclass for implementing Singleton pattern."""
    
    _instances: Dict[type, Any] = {}
    
    def __call__(cls, *args, **kwargs):
        """Execute call."""
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class ClubRegistry(metaclass=SingletonMeta):
    """
    Singleton registry for all clubs.
    Ensures single source of truth for club data.
    """
    
    def __init__(self):
        """Initialise a new ClubRegistry instance."""
        self._clubs: Dict[str, Club] = {}
        self._members: Dict[str, List[str]] = {}  # member_id -> list of club names
        self._observers: List[Observer] = []
    
    def register_club(self, club: Club) -> None:
        """Register a new club."""
        if club.name in self._clubs:
            raise ClubManagementError(f"Club '{club.name}' already registered")
        
        self._clubs[club.name] = club
        
        # Attach global observers to club
        for observer in self._observers:
            club.add_observer(observer)
    
    def get_club(self, name: str) -> Club:
        """Get a club by name."""
        if name not in self._clubs:
            raise ClubManagementError(f"Club '{name}' not found")
        return self._clubs[name]
    
    def get_all_clubs(self) -> List[Club]:
        """Get all registered clubs."""
        return list(self._clubs.values())
    
    def get_member_across_clubs(self, member_id: str) -> Dict[str, Member]:
        """Get a member's records across all clubs."""
        result = {}
        for club_name, club in self._clubs.items():
            try:
                member = club.get_member(member_id)
                result[club_name] = member
            except MemberNotFoundError:
                pass
        return result
    
    def add_global_observer(self, observer: Observer) -> None:
        """Add an observer to all clubs."""
        self._observers.append(observer)
        for club in self._clubs.values():
            club.add_observer(observer)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""
        total_members = sum(club.member_count for club in self._clubs.values())
        total_events = sum(len(club.get_all_events()) for club in self._clubs.values())
        total_budget = sum(club.budget.balance for club in self._clubs.values())
        
        return {
            "total_clubs": len(self._clubs),
            "total_members": total_members,
            "total_events": total_events,
            "total_budget": total_budget,
            "clubs_by_type": self._count_clubs_by_type()
        }
    
    def _count_clubs_by_type(self) -> Dict[str, int]:
        """Count clubs by type."""
        counts = {}
        for club in self._clubs.values():
            type_name = club.club_type
            counts[type_name] = counts.get(type_name, 0) + 1
        return counts

