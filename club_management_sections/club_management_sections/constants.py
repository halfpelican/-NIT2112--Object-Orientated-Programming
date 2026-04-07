"""Shared constants for statuses, permissions, transaction types, club types, and resources."""

from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
# =============================================================================
# STATUS AND ATTRIBUTE CONSTANTS
# =============================================================================


class EventStatus:
    """Status values for event lifecycle."""
    _PROPOSED = "PROPOSED"
    _BUDGET_REVIEW = "BUDGET_REVIEW"
    _RESOURCE_CHECK = "RESOURCE_CHECK"
    _APPROVED = "APPROVED"
    _SCHEDULED = "SCHEDULED"
    _COMPLETED = "COMPLETED"
    _REJECTED = "REJECTED"
    _CANCELLED = "CANCELLED"


class Permission:
    """Permissions that can be assigned to members."""
    _VIEW_CLUB_INFO = "VIEW_CLUB_INFO"
    _PROPOSE_EVENT = "PROPOSE_EVENT"
    _ATTEND_EVENT = "ATTEND_EVENT"
    _APPROVE_BUDGET = "APPROVE_BUDGET"
    _APPROVE_RESOURCES = "APPROVE_RESOURCES"
    _FINAL_APPROVAL = "FINAL_APPROVAL"
    _MANAGE_MEMBERS = "MANAGE_MEMBERS"
    _MANAGE_FINANCES = "MANAGE_FINANCES"
    _VETO_DECISION = "VETO_DECISION"
    _RECORD_MINUTES = "RECORD_MINUTES"


class TransactionType:
    """Types of financial transactions."""
    _ALLOCATION = "ALLOCATION"
    _EXPENSE = "EXPENSE"
    _REVENUE = "REVENUE"
    _REFUND = "REFUND"
    _RESERVATION = "RESERVATION"
    _CANCELLATION_FEE = "CANCELLATION_FEE"


class ClubType:
    """Types of student clubs."""
    _ACADEMIC = "ACADEMIC"
    _SOCIAL = "SOCIAL"
    _SPORTS = "SPORTS"
    _CULTURAL = "CULTURAL"


class ResourceType:
    """Types of bookable resources."""
    _VENUE = "VENUE"
    _EQUIPMENT = "EQUIPMENT"

