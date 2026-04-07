"""Event hierarchy with attendance tracking and approval workflow integration."""

from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Set, Any, Tuple
from dataclasses import dataclass, field

from constants import EventStatus, Permission
from event_states import (
    EventState, ProposedState, BudgetReviewState, ResourceCheckState,
    ApprovedState, ScheduledState, CompletedState, RejectedState, CancelledState
)
from exceptions import InvalidEventStateError, EventCapacityExceededError, PermissionDeniedError
from interfaces import Approvable, Trackable
from observer_pattern import Observable, Observer
# =============================================================================
# EVENT HIERARCHY
# =============================================================================


@dataclass
class ApprovalRecord:
    """Record of an approval action."""
    stage: str
    approver_id: str
    approver_role: str
    action: str  # "approved" or "rejected"
    timestamp: datetime
    notes: str = ""


@dataclass
class AttendanceRecord:
    """Record of attendance at an event."""
    member_id: str
    check_in_time: datetime
    participation_type: str  # "attendee", "volunteer", "organizer"


class Event(Approvable, Trackable, Observable):
    """Abstract base class for all events."""
    
    def __init__(
        self,
        event_id: str,
        title: str,
        description: str,
        proposed_by: str,
        estimated_cost: float,
        event_date: date = None
    ):
        """Initialise a new Event instance."""
        self._event_id = event_id
        self._title = title
        self._description = description
        self._proposed_by = proposed_by
        self._estimated_cost = estimated_cost
        self._event_date = event_date or (date.today() + timedelta(days=30))
        self._state: EventState = ProposedState()
        self._approval_history: List[ApprovalRecord] = []
        self._attendance: List[AttendanceRecord] = []
        self._observers: List[Observer] = []
        self._required_resources: List[str] = []
        self._created_at = datetime.now()
    
    @property
    def event_id(self) -> str:
        """Execute event id."""
        return self._event_id
    
    @property
    def title(self) -> str:
        """Execute title."""
        return self._title
    
    @property
    def description(self) -> str:
        """Execute description."""
        return self._description
    
    @property
    def proposed_by(self) -> str:
        """Execute proposed by."""
        return self._proposed_by
    
    @property
    def estimated_cost(self) -> float:
        """Execute estimated cost."""
        return self._estimated_cost
    
    @property
    def event_date(self) -> date:
        """Execute event date."""
        return self._event_date
    
    @property
    def status(self) -> str:
        """Execute status."""
        return self._state.get_status()
    
    @property
    def approval_history(self) -> List[ApprovalRecord]:
        """Execute approval history."""
        return self._approval_history.copy()
    
    @property
    @abstractmethod
    def event_type(self) -> str:
        """Return the type of event."""
        pass
    
    @abstractmethod
    def calculate_total_cost(self) -> float:
        """Calculate the total cost including all factors."""
        pass
    
    @abstractmethod
    def get_required_resources(self) -> List[str]:
        """Return list of required resource IDs."""
        pass
    
    def add_required_resource(self, resource_id: str) -> None:
        """Add a required resource."""
        if resource_id not in self._required_resources:
            self._required_resources.append(resource_id)
    
    # Approvable interface implementation
    def submit_for_approval(self) -> None:
        """Submit event for approval workflow."""
        if self._state.get_status() != EventStatus._PROPOSED:
            raise InvalidEventStateError(self._event_id, self.status, "submit for approval")
        self._state = BudgetReviewState()
        self.notify_observers("event_submitted", {
            "event_id": self._event_id,
            "title": self._title,
            "estimated_cost": self._estimated_cost
        })
    
    def approve(self, approver: 'ExecutiveCommitteeMember') -> bool:
        """Approve the event at current stage."""
        if not approver.is_active:
            raise PermissionDeniedError(approver.member_id, Permission._FINAL_APPROVAL, "approve event")
        
        old_status = self._state.get_status()
        self._state = self._state.process_approval(self, approver)
        
        # Record approval
        self._approval_history.append(ApprovalRecord(
            stage=old_status,
            approver_id=approver.member_id,
            approver_role=approver.role,
            action="approved",
            timestamp=datetime.now()
        ))
        
        self.notify_observers("event_approved", {
            "event_id": self._event_id,
            "stage": old_status,
            "approver": approver.member_id,
            "new_status": self._state.get_status()
        })
        
        return True
    
    def reject(self, approver: 'ExecutiveCommitteeMember', reason: str) -> None:
        """Reject the event with a reason."""
        if not approver.is_active:
            raise PermissionDeniedError(approver.member_id, Permission._FINAL_APPROVAL, "reject event")
        
        old_status = self._state.get_status()
        self._state = self._state.process_rejection(self, approver, reason)
        
        # Record rejection
        self._approval_history.append(ApprovalRecord(
            stage=old_status,
            approver_id=approver.member_id,
            approver_role=approver.role,
            action="rejected",
            timestamp=datetime.now(),
            notes=reason
        ))
        
        self.notify_observers("event_rejected", {
            "event_id": self._event_id,
            "stage": old_status,
            "approver": approver.member_id,
            "reason": reason
        })
    
    def cancel(self, reason: str) -> float:
        """Cancel the event. Returns cancellation fee if applicable."""
        if self.status in [EventStatus._COMPLETED, EventStatus._REJECTED, EventStatus._CANCELLED]:
            raise InvalidEventStateError(self._event_id, self.status, "cancel")
        
        # Calculate cancellation fee (10% if approved or scheduled)
        fee = 0.0
        if self.status in [EventStatus._APPROVED, EventStatus._SCHEDULED]:
            fee = self._estimated_cost * 0.10
        
        self._state = CancelledState(reason, fee)
        
        self.notify_observers("event_cancelled", {
            "event_id": self._event_id,
            "reason": reason,
            "cancellation_fee": fee
        })
        
        return fee
    
    def complete(self) -> None:
        """Mark event as completed."""
        if self.status != EventStatus._SCHEDULED:
            raise InvalidEventStateError(self._event_id, self.status, "complete")
        
        self._state = CompletedState()
        
        self.notify_observers("event_completed", {
            "event_id": self._event_id,
            "attendance_count": self.get_attendance_count()
        })
    
    def get_approval_status(self) -> Dict[str, Any]:
        """Get current approval status and history."""
        return {
            "event_id": self._event_id,
            "current_status": self.status,
            "required_approver": self._state.get_required_approver_role(),
            "history": [
                {
                    "stage": r.stage,
                    "approver": r.approver_id,
                    "action": r.action,
                    "timestamp": r.timestamp.isoformat(),
                    "notes": r.notes
                }
                for r in self._approval_history
            ]
        }
    
    # Trackable interface implementation
    def record_attendance(self, member_id: str, role: str = "attendee") -> None:
        """Record a member's attendance."""
        if self.status not in [EventStatus._SCHEDULED, EventStatus._COMPLETED]:
            raise InvalidEventStateError(self._event_id, self.status, "record attendance")
        
        # Check for duplicate
        if any(r.member_id == member_id for r in self._attendance):
            return  # Already recorded
        
        record = AttendanceRecord(
            member_id=member_id,
            check_in_time=datetime.now(),
            participation_type=role
        )
        self._attendance.append(record)
        
        self.notify_observers("attendance_recorded", {
            "event_id": self._event_id,
            "member_id": member_id,
            "role": role
        })
    
    def get_attendance_list(self) -> List[Dict[str, Any]]:
        """Get list of attendees with details."""
        return [
            {
                "member_id": r.member_id,
                "check_in_time": r.check_in_time.isoformat(),
                "role": r.participation_type
            }
            for r in self._attendance
        ]
    
    def get_attendance_count(self) -> int:
        """Get total attendance count."""
        return len(self._attendance)
    
    # Observable interface implementation
    def add_observer(self, observer: Observer) -> None:
        """Add an observer."""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def remove_observer(self, observer: Observer) -> None:
        """Remove an observer."""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify_observers(self, event_type: str, data: Dict[str, Any]) -> None:
        """Notify all observers of an event."""
        for observer in self._observers:
            observer.update(event_type, data)
    
    def display_info(self) -> str:
        """Display event information."""
        return (f"{self.event_type}: {self._title}\n"
                f"  ID: {self._event_id}\n"
                f"  Status: {self.status}\n"
                f"  Date: {self._event_date}\n"
                f"  Cost: ${self.calculate_total_cost():.2f}\n"
                f"  Proposed by: {self._proposed_by}\n"
                f"  Attendance: {self.get_attendance_count()}")
    
    def __str__(self) -> str:
        """Execute str."""
        return f"{self.event_type}({self._event_id}): {self._title} [{self.status}]"


class Workshop(Event):
    """Educational workshop event."""
    
    def __init__(
        self,
        event_id: str,
        title: str,
        description: str,
        proposed_by: str,
        estimated_cost: float,
        topic: str,
        instructor: str,
        max_participants: int = 30,
        event_date: date = None
    ):
        """Initialise a new Workshop instance."""
        super().__init__(event_id, title, description, proposed_by, estimated_cost, event_date)
        self._topic = topic
        self._instructor = instructor
        self._max_participants = max_participants
        self._materials_needed: List[str] = []
    
    @property
    def event_type(self) -> str:
        """Execute event type."""
        return "Workshop"
    
    @property
    def topic(self) -> str:
        """Execute topic."""
        return self._topic
    
    @property
    def max_participants(self) -> int:
        """Execute max participants."""
        return self._max_participants
    
    def add_material(self, material: str) -> None:
        """Add required material."""
        self._materials_needed.append(material)
    
    def calculate_total_cost(self) -> float:
        """Workshop cost = base + materials."""
        material_cost = len(self._materials_needed) * 10  # $10 per material type
        return self._estimated_cost + material_cost
    
    def get_required_resources(self) -> List[str]:
        """Workshop requires a venue."""
        return self._required_resources + ["venue"]
    
    def record_attendance(self, member_id: str, role: str = "attendee") -> None:
        """Record attendance with capacity check."""
        if self.get_attendance_count() >= self._max_participants and role == "attendee":
            raise EventCapacityExceededError(
                self._event_id, 
                self._max_participants, 
                self.get_attendance_count()
            )
        super().record_attendance(member_id, role)


class SocialGathering(Event):
    """Social event for member engagement."""
    
    def __init__(
        self,
        event_id: str,
        title: str,
        description: str,
        proposed_by: str,
        estimated_cost: float,
        theme: str,
        expected_attendance: int = 50,
        catering_required: bool = True,
        event_date: date = None
    ):
        """Initialise a new SocialGathering instance."""
        super().__init__(event_id, title, description, proposed_by, estimated_cost, event_date)
        self._theme = theme
        self._expected_attendance = expected_attendance
        self._catering_required = catering_required
        self._catering_cost_per_person = 15.0
    
    @property
    def event_type(self) -> str:
        """Execute event type."""
        return "SocialGathering"
    
    @property
    def theme(self) -> str:
        """Execute theme."""
        return self._theme
    
    def calculate_total_cost(self) -> float:
        """Social cost = base + catering if required."""
        total = self._estimated_cost
        if self._catering_required:
            total += self._expected_attendance * self._catering_cost_per_person
        return total
    
    def get_required_resources(self) -> List[str]:
        """Social events require venue."""
        return self._required_resources + ["venue"]


class Fundraiser(Event):
    """Fundraising event that generates revenue."""
    
    def __init__(
        self,
        event_id: str,
        title: str,
        description: str,
        proposed_by: str,
        estimated_cost: float,
        target_amount: float,
        fundraising_method: str,
        event_date: date = None
    ):
        """Initialise a new Fundraiser instance."""
        super().__init__(event_id, title, description, proposed_by, estimated_cost, event_date)
        self._target_amount = target_amount
        self._actual_raised = 0.0
        self._fundraising_method = fundraising_method
    
    @property
    def event_type(self) -> str:
        """Execute event type."""
        return "Fundraiser"
    
    @property
    def target_amount(self) -> float:
        """Execute target amount."""
        return self._target_amount
    
    @property
    def actual_raised(self) -> float:
        """Execute actual raised."""
        return self._actual_raised
    
    @property
    def net_revenue(self) -> float:
        """Execute net revenue."""
        return self._actual_raised - self._estimated_cost
    
    def record_donation(self, amount: float) -> None:
        """Record a donation."""
        self._actual_raised += amount
    
    def calculate_total_cost(self) -> float:
        """Fundraiser has minimal setup cost."""
        return self._estimated_cost
    
    def get_required_resources(self) -> List[str]:
        """Return the required resources."""
        return self._required_resources


class Competition(Event):
    """Competition event with prizes and registration fees."""
    
    def __init__(
        self,
        event_id: str,
        title: str,
        description: str,
        proposed_by: str,
        estimated_cost: float,
        competition_type: str,
        prize_pool: float,
        registration_fee: float,
        event_date: date = None
    ):
        """Initialise a new Competition instance."""
        super().__init__(event_id, title, description, proposed_by, estimated_cost, event_date)
        self._competition_type = competition_type
        self._prize_pool = prize_pool
        self._registration_fee = registration_fee
        self._registrations = 0
    
    @property
    def event_type(self) -> str:
        """Execute event type."""
        return "Competition"
    
    @property
    def competition_type(self) -> str:
        """Execute competition type."""
        return self._competition_type
    
    @property
    def prize_pool(self) -> float:
        """Execute prize pool."""
        return self._prize_pool
    
    @property
    def registration_revenue(self) -> float:
        """Execute registration revenue."""
        return self._registrations * self._registration_fee
    
    @property
    def net_cost(self) -> float:
        """Execute net cost."""
        return self.calculate_total_cost() - self.registration_revenue
    
    def register_participant(self, member_id: str) -> None:
        """Register a participant."""
        self._registrations += 1
        self.record_attendance(member_id, "participant")
    
    def calculate_total_cost(self) -> float:
        """Competition cost = base + prizes."""
        return self._estimated_cost + self._prize_pool
    
    def get_required_resources(self) -> List[str]:
        """Return the required resources."""
        return self._required_resources + ["venue"]

