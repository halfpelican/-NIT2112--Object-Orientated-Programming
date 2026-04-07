"""Core Club aggregate handling members, events, finances, and resources."""

from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Set, Any, Tuple
from dataclasses import dataclass, field

from constants import EventStatus, Permission, ClubType
from event_states import EventState
from events import Event, Fundraiser, Competition
from exceptions import (
    DuplicateMemberError, MemberNotFoundError, PermissionDeniedError,
    EventError, EventNotFoundError, InvalidEventStateError,
    InsufficientFundsError, ResourceNotAvailableError
)
from financial import Budget
from observer_pattern import Observer, Observable
from members import Member, StandardMember, ExecutiveCommitteeMember, President, Treasurer, Secretary, EventCoordinator
from resources import Resource, ResourceManager, Venue, Equipment
# =============================================================================
# CLUB CLASS
# =============================================================================


class Club(Observable):
    """Represents a student club with members, events, and budget."""
    
    def __init__(
        self,
        club_id: str,
        name: str,
        club_type: ClubType,
        initial_budget: float = 0.0
    ):
        """Initialise a new Club instance."""
        self._club_id = club_id
        self._name = name
        self._club_type = club_type
        self._budget = Budget(initial_budget)
        self._members: Dict[str, Member] = {}
        self._standard_members: Dict[str, StandardMember] = {}
        self._executive_members: Dict[str, ExecutiveCommitteeMember] = {}
        self._events: Dict[str, Event] = {}
        self._resource_manager = ResourceManager()
        self._observers: List[Observer] = []
        self._created_at = datetime.now()
        
        # Executive positions
        self._president: Optional[President] = None
        self._treasurer: Optional[Treasurer] = None
        self._secretary: Optional[Secretary] = None
        self._event_coordinator: Optional[EventCoordinator] = None
    
    @property
    def club_id(self) -> str:
        """Execute club id."""
        return self._club_id
    
    @property
    def name(self) -> str:
        """Execute name."""
        return self._name
    
    @property
    def club_type(self) -> ClubType:
        """Execute club type."""
        return self._club_type
    
    @property
    def budget(self) -> Budget:
        """Execute budget."""
        return self._budget
    
    @property
    def member_count(self) -> int:
        """Execute member count."""
        return len(self._members)

    @property
    def standard_member_count(self) -> int:
        """Return the number of standard members in the club."""
        return len(self._standard_members)

    @property
    def executive_member_count(self) -> int:
        """Return the number of executive members in the club."""
        return len(self._executive_members)

    @property
    def standard_members(self) -> List[StandardMember]:
        """Return all standard members in insertion order."""
        return list(self._standard_members.values())

    @property
    def executive_members(self) -> List[ExecutiveCommitteeMember]:
        """Return all executive members in insertion order."""
        return list(self._executive_members.values())
    
    @property
    def president(self) -> Optional[President]:
        """Execute president."""
        return self._president
    
    @property
    def treasurer(self) -> Optional[Treasurer]:
        """Execute treasurer."""
        return self._treasurer
    
    # Observable implementation
    def add_observer(self, observer: Observer) -> None:
        """Add observer to this Club."""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def remove_observer(self, observer: Observer) -> None:
        """Remove observer from this Club."""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify_observers(self, event_type: str, data: Dict[str, Any]) -> None:
        """Execute notify observers."""
        data["club_name"] = self._name
        for observer in self._observers:
            observer.update(event_type, data)
    
    # Member management
    def add_member(self, member: Member) -> None:
        """Add a member to the club."""
        if member.member_id in self._members:
            raise DuplicateMemberError(member.member_id, self._name)
        
        self._members[member.member_id] = member
        member.join_club(self._name)
        
        # Assign executive positions
        if isinstance(member, President):
            self._president = member
            self._executive_members[member.member_id] = member
        elif isinstance(member, Treasurer):
            self._treasurer = member
            self._executive_members[member.member_id] = member
        elif isinstance(member, Secretary):
            self._secretary = member
            self._executive_members[member.member_id] = member
        elif isinstance(member, EventCoordinator):
            self._event_coordinator = member
            self._executive_members[member.member_id] = member
        elif isinstance(member, StandardMember):
            self._standard_members[member.member_id] = member
        
        self.notify_observers("member_added", {
            "member_id": member.member_id,
            "name": member.name,
            "role": member.role
        })
    
    def get_member(self, member_id: str) -> Member:
        """Get a member by ID."""
        if member_id not in self._members:
            raise MemberNotFoundError(member_id)
        return self._members[member_id]
    
    def remove_member(self, member_id: str) -> None:
        """Remove a member from the club."""
        member = self.get_member(member_id)
        member.leave_club(self._name)
        del self._members[member_id]
        self._standard_members.pop(member_id, None)
        self._executive_members.pop(member_id, None)

        if self._president and self._president.member_id == member_id:
            self._president = None
        if self._treasurer and self._treasurer.member_id == member_id:
            self._treasurer = None
        if self._secretary and self._secretary.member_id == member_id:
            self._secretary = None
        if self._event_coordinator and self._event_coordinator.member_id == member_id:
            self._event_coordinator = None
        
        self.notify_observers("member_removed", {
            "member_id": member_id,
            "name": member.name
        })
    
    def get_all_members(self) -> List[Member]:
        """Get all members."""
        return list(self._members.values())

    def get_standard_members(self) -> List[StandardMember]:
        """Get all standard members."""
        return list(self._standard_members.values())
    
    def get_executives(self) -> List[ExecutiveCommitteeMember]:
        """Get all executive members."""
        return list(self._executive_members.values())
    
    # Event management
    def propose_event(self, event: Event, proposer_id: str) -> None:
        """Add a proposed event."""
        member = self.get_member(proposer_id)
        
        if not member.has_permission(Permission._PROPOSE_EVENT):
            raise PermissionDeniedError(proposer_id, Permission._PROPOSE_EVENT, "propose event")
        
        if event.event_id in self._events:
            raise EventError(f"Event '{event.event_id}' already exists")
        
        self._events[event.event_id] = event
        
        # Attach club observers to event
        for observer in self._observers:
            event.add_observer(observer)
        
        self.notify_observers("event_proposed", {
            "event_id": event.event_id,
            "title": event.title,
            "proposed_by": proposer_id
        })
    
    def get_event(self, event_id: str) -> Event:
        """Get an event by ID."""
        if event_id not in self._events:
            raise EventNotFoundError(event_id)
        return self._events[event_id]
    
    def get_all_events(self) -> List[Event]:
        """Get all events."""
        return list(self._events.values())
    
    def get_events_by_status(self, status: EventStatus) -> List[Event]:
        """Get events filtered by status."""
        return [e for e in self._events.values() if e.status == status]
    
    def process_event_approval(
        self,
        event_id: str,
        approver_id: str,
        approve: bool,
        reason: str = ""
    ) -> None:
        """Process event approval by an executive."""
        event = self.get_event(event_id)
        approver = self.get_member(approver_id)
        
        if not isinstance(approver, ExecutiveCommitteeMember):
            raise PermissionDeniedError(approver_id, Permission._FINAL_APPROVAL, "approve event")
        
        if approve:
            # Budget check if in budget review
            if event.status == EventStatus._BUDGET_REVIEW:
                cost = event.calculate_total_cost()
                if not self._budget.can_afford(cost):
                    raise InsufficientFundsError(cost, self._budget.available_balance, "event approval")
                # Reserve funds
                self._budget.reserve_funds(event_id, cost)
            
            # Resource check if in resource check
            if event.status == EventStatus._RESOURCE_CHECK:
                resources = event.get_required_resources()
                availability = self._resource_manager.check_availability(
                    [r for r in resources if r in ["venue"]],  # Only check actual resource IDs
                    event.event_date
                )
                if not all(availability.values()):
                    unavailable = [r for r, a in availability.items() if not a]
                    raise ResourceNotAvailableError(
                        unavailable[0] if unavailable else "resource",
                        event.event_date,
                        "already booked"
                    )
            
            event.approve(approver)
        else:
            event.reject(approver, reason)
            # Release any reserved funds
            self._budget.release_reservation(event_id)
    
    def cancel_event(self, event_id: str, reason: str) -> None:
        """Cancel an event."""
        event = self.get_event(event_id)
        fee = event.cancel(reason)
        
        if fee > 0:
            self._budget.apply_cancellation_fee(event_id, fee)
        else:
            self._budget.release_reservation(event_id)
        
        # Cancel resource bookings
        self._resource_manager.cancel_bookings(event_id)
    
    def complete_event(self, event_id: str, actual_cost: float = None) -> None:
        """Complete an event."""
        event = self.get_event(event_id)
        event.complete()
        
        # Process actual expenses
        cost = actual_cost or event.calculate_total_cost()
        self._budget.spend(event_id, cost, f"Event expense: {event.title}")
        
        # Process revenue if applicable
        if isinstance(event, Fundraiser):
            self._budget.add_revenue(
                event.actual_raised,
                f"Fundraiser revenue: {event.title}",
                event_id
            )
        elif isinstance(event, Competition):
            self._budget.add_revenue(
                event.registration_revenue,
                f"Competition registrations: {event.title}",
                event_id
            )
    
    # Resource management
    def add_resource(self, resource: Resource) -> None:
        """Add a resource to the club."""
        self._resource_manager.add_resource(resource)
    
    def book_resources_for_event(self, event_id: str, resource_ids: List[str]) -> None:
        """Book resources for an event."""
        event = self.get_event(event_id)
        
        if event.status not in [EventStatus._APPROVED, EventStatus._SCHEDULED]:
            raise InvalidEventStateError(event_id, event.status, "book resources")
        
        self._resource_manager.book_resources(
            resource_ids,
            event_id,
            event.event_date,
            event.proposed_by
        )
    
    # Reports
    def get_club_report(self) -> str:
        """Generate a comprehensive club report."""
        lines = [
            "=" * 60,
            f"CLUB REPORT: {self._name}",
            "=" * 60,
            f"Type: {self._club_type}",
            f"Members: {self.member_count}",
            f"Standard Members: {self.standard_member_count}",
            f"Executive Members: {self.executive_member_count}",
            f"Budget: ${self._budget.balance:.2f}",
            "",
            "EXECUTIVES:",
            "-" * 40
        ]
        
        for exec_member in self.get_executives():
            lines.append(f"  {exec_member.role}: {exec_member.name}")
        
        lines.extend([
            "",
            "EVENTS BY STATUS:",
            "-" * 40
        ])
        
        statuses = [
            EventStatus._PROPOSED,
            EventStatus._BUDGET_REVIEW,
            EventStatus._RESOURCE_CHECK,
            EventStatus._APPROVED,
            EventStatus._SCHEDULED,
            EventStatus._COMPLETED,
            EventStatus._REJECTED,
            EventStatus._CANCELLED,
        ]
        for status in statuses:
            events = self.get_events_by_status(status)
            if events:
                lines.append(f"  {status}: {len(events)}")
        
        return "\n".join(lines)
    
    def __str__(self) -> str:
        """Execute str."""
        return f"Club: {self._name} ({self._club_type}) - {self.member_count} members"

