"""Member class hierarchy including standard and executive member roles."""

from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
# =============================================================================
# MEMBER HIERARCHY
# =============================================================================


class Member(ABC):
    """Abstract base class for all club members."""
    
    def __init__(self, member_id: str, name: str, email: str):
        """Initialise a new Member instance."""
        self._member_id = member_id
        self._name = name
        self._email = email
        self._join_date = date.today()
        self._clubs: List[str] = []  # Club names this member belongs to
    
    @property
    def member_id(self) -> str:
        """Execute member id."""
        return self._member_id
    
    @property
    def name(self) -> str:
        """Execute name."""
        return self._name
    
    @property
    def email(self) -> str:
        """Execute email."""
        return self._email
    
    @property
    def join_date(self) -> date:
        """Execute join date."""
        return self._join_date
    
    @property
    def clubs(self) -> List[str]:
        """Execute clubs."""
        return self._clubs.copy()
    
    @property
    @abstractmethod
    def role(self) -> str:
        """Return the role name of this member."""
        pass
    
    @abstractmethod
    def get_permissions(self) -> Set[str]:
        """Return the set of permissions for this member."""
        pass
    
    def has_permission(self, permission: str) -> bool:
        """Check if member has a specific permission."""
        return permission in self.get_permissions()
    
    def join_club(self, club_name: str) -> None:
        """Add member to a club."""
        if club_name not in self._clubs:
            self._clubs.append(club_name)
    
    def leave_club(self, club_name: str) -> None:
        """Remove member from a club."""
        if club_name in self._clubs:
            self._clubs.remove(club_name)
    
    @abstractmethod
    def display_info(self) -> str:
        """Return formatted member information."""
        pass
    
    def __str__(self) -> str:
        """Execute str."""
        return f"{self.role}: {self._name} ({self._member_id})"


class StandardMember(Member):
    """Regular club member with basic permissions."""
    
    def __init__(self, member_id: str, name: str, email: str):
        """Initialise a new StandardMember instance."""
        super().__init__(member_id, name, email)
        self._attendance_count = 0
        self._contributions: List[str] = []  # Event IDs proposed
    
    @property
    def role(self) -> str:
        """Execute role."""
        return "StandardMember"
    
    @property
    def attendance_count(self) -> int:
        """Execute attendance count."""
        return self._attendance_count
    
    def increment_attendance(self) -> None:
        """Increment attendance count."""
        self._attendance_count += 1
    
    def add_contribution(self, event_id: str) -> None:
        """Record an event contribution."""
        self._contributions.append(event_id)
    
    def get_permissions(self) -> Set[str]:
        """Return the permissions."""
        return {
            Permission._VIEW_CLUB_INFO,
            Permission._PROPOSE_EVENT,
            Permission._ATTEND_EVENT
        }
    
    def display_info(self) -> str:
        """Display info."""
        return (f"Standard Member: {self._name}\n"
                f"  ID: {self._member_id}\n"
                f"  Email: {self._email}\n"
                f"  Joined: {self._join_date}\n"
                f"  Events Attended: {self._attendance_count}\n"
                f"  Contributions: {len(self._contributions)}")


class ExecutiveCommitteeMember(Member):
    """Abstract base class for executive committee members."""
    
    def __init__(
        self,
        member_id: str,
        name: str,
        email: str,
        term_start: date = None,
        term_end: date = None
    ):
        """Initialise a new ExecutiveCommitteeMember instance."""
        super().__init__(member_id, name, email)
        self._term_start = term_start or date.today()
        self._term_end = term_end or (date.today() + timedelta(days=365))
        self._is_active = True
    
    @property
    def term_start(self) -> date:
        """Execute term start."""
        return self._term_start
    
    @property
    def term_end(self) -> date:
        """Execute term end."""
        return self._term_end
    
    @property
    def is_active(self) -> bool:
        """Execute is active."""
        return self._is_active and date.today() <= self._term_end
    
    def deactivate(self) -> None:
        """Deactivate the executive role."""
        self._is_active = False
    
    def get_permissions(self) -> Set[str]:
        """Base executive permissions."""
        return {
            Permission._VIEW_CLUB_INFO,
            Permission._PROPOSE_EVENT,
            Permission._ATTEND_EVENT,
            Permission._MANAGE_MEMBERS
        }


class President(ExecutiveCommitteeMember):
    """Club President with final approval authority."""
    
    def __init__(
        self,
        member_id: str,
        name: str,
        email: str,
        term_start: date = None,
        term_end: date = None
    ):
        """Initialise a new President instance."""
        super().__init__(member_id, name, email, term_start, term_end)
        self._veto_count = 0
        self._final_approvals: List[str] = []
    
    @property
    def role(self) -> str:
        """Execute role."""
        return "President"
    
    @property
    def veto_count(self) -> int:
        """Execute veto count."""
        return self._veto_count
    
    def record_veto(self) -> None:
        """Record a veto action."""
        self._veto_count += 1
    
    def record_approval(self, event_id: str) -> None:
        """Record a final approval."""
        self._final_approvals.append(event_id)
    
    def get_permissions(self) -> Set[str]:
        """Return the permissions."""
        perms = super().get_permissions()
        perms.update({
            Permission._FINAL_APPROVAL,
            Permission._VETO_DECISION,
            Permission._MANAGE_FINANCES
        })
        return perms
    
    def display_info(self) -> str:
        """Display info."""
        return (f"President: {self._name}\n"
                f"  ID: {self._member_id}\n"
                f"  Email: {self._email}\n"
                f"  Term: {self._term_start} to {self._term_end}\n"
                f"  Active: {self.is_active}\n"
                f"  Vetoes: {self._veto_count}\n"
                f"  Approvals: {len(self._final_approvals)}")


class Treasurer(ExecutiveCommitteeMember):
    """Club Treasurer with budget approval authority."""
    
    def __init__(
        self,
        member_id: str,
        name: str,
        email: str,
        term_start: date = None,
        term_end: date = None
    ):
        """Initialise a new Treasurer instance."""
        super().__init__(member_id, name, email, term_start, term_end)
        self._approved_expenses: List[Tuple[str, float]] = []
        self._overdraft_allowance = 0.0
    
    @property
    def role(self) -> str:
        """Execute role."""
        return "Treasurer"
    
    @property
    def total_approved_expenses(self) -> float:
        """Execute total approved expenses."""
        return sum(amount for _, amount in self._approved_expenses)
    
    def set_overdraft_allowance(self, amount: float) -> None:
        """Set emergency overdraft allowance."""
        self._overdraft_allowance = amount
    
    def record_expense_approval(self, event_id: str, amount: float) -> None:
        """Record an approved expense."""
        self._approved_expenses.append((event_id, amount))
    
    def get_permissions(self) -> Set[str]:
        """Return the permissions."""
        perms = super().get_permissions()
        perms.update({
            Permission._APPROVE_BUDGET,
            Permission._MANAGE_FINANCES
        })
        return perms
    
    def display_info(self) -> str:
        """Display info."""
        return (f"Treasurer: {self._name}\n"
                f"  ID: {self._member_id}\n"
                f"  Email: {self._email}\n"
                f"  Term: {self._term_start} to {self._term_end}\n"
                f"  Active: {self.is_active}\n"
                f"  Approved Expenses: ${self.total_approved_expenses:.2f}")


class Secretary(ExecutiveCommitteeMember):
    """Club Secretary managing records and communications."""
    
    def __init__(
        self,
        member_id: str,
        name: str,
        email: str,
        term_start: date = None,
        term_end: date = None
    ):
        """Initialise a new Secretary instance."""
        super().__init__(member_id, name, email, term_start, term_end)
        self._meetings_recorded = 0
        self._communications_sent = 0
    
    @property
    def role(self) -> str:
        """Execute role."""
        return "Secretary"
    
    @property
    def meetings_recorded(self) -> int:
        """Execute meetings recorded."""
        return self._meetings_recorded
    
    def record_meeting(self) -> None:
        """Record a meeting."""
        self._meetings_recorded += 1
    
    def record_communication(self) -> None:
        """Record a communication sent."""
        self._communications_sent += 1
    
    def get_permissions(self) -> Set[str]:
        """Return the permissions."""
        perms = super().get_permissions()
        perms.add(Permission._RECORD_MINUTES)
        return perms
    
    def display_info(self) -> str:
        """Display info."""
        return (f"Secretary: {self._name}\n"
                f"  ID: {self._member_id}\n"
                f"  Email: {self._email}\n"
                f"  Term: {self._term_start} to {self._term_end}\n"
                f"  Active: {self.is_active}\n"
                f"  Meetings Recorded: {self._meetings_recorded}")


class EventCoordinator(ExecutiveCommitteeMember):
    """Event Coordinator managing logistics and resources."""
    
    def __init__(
        self,
        member_id: str,
        name: str,
        email: str,
        term_start: date = None,
        term_end: date = None
    ):
        """Initialise a new EventCoordinator instance."""
        super().__init__(member_id, name, email, term_start, term_end)
        self._events_managed: List[str] = []
    
    @property
    def role(self) -> str:
        """Execute role."""
        return "EventCoordinator"
    
    @property
    def events_managed_count(self) -> int:
        """Execute events managed count."""
        return len(self._events_managed)
    
    def add_managed_event(self, event_id: str) -> None:
        """Add an event to managed list."""
        self._events_managed.append(event_id)
    
    def get_permissions(self) -> Set[str]:
        """Return the permissions."""
        perms = super().get_permissions()
        perms.add(Permission._APPROVE_RESOURCES)
        return perms
    
    def display_info(self) -> str:
        """Display info."""
        return (f"Event Coordinator: {self._name}\n"
                f"  ID: {self._member_id}\n"
                f"  Email: {self._email}\n"
                f"  Term: {self._term_start} to {self._term_end}\n"
                f"  Active: {self.is_active}\n"
                f"  Events Managed: {self.events_managed_count}")

