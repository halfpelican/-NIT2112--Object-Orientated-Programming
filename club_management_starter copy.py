"""
NIT2112 Practical Test: UniClub Student Club Management System
Student Name: [Your Name]
Student ID: [Your ID]
Date: [Date]
AI Copilot Used: [Yes/No - Name of tool]

A comprehensive OOP system for managing university student clubs,
including member roles, event approval workflows, budget management,
and resource coordination.

OOP Concepts Demonstrated:
- Class hierarchies with ABC (Member, Event, Resource)
- State Pattern for event approval workflow
- Factory Pattern for club creation
- Observer Pattern for attendance tracking
- Singleton Pattern for club registry
- Custom exception hierarchy
- Encapsulation with properties
- Polymorphism through method overriding
"""

from abc import ABC, abstractmethod
from enum import Enum, auto
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Set, Any, Tuple
from dataclasses import dataclass, field


# =============================================================================
# ENUMS
# =============================================================================

class EventStatus(Enum):
    """Status values for event lifecycle."""
    PROPOSED = auto()
    BUDGET_REVIEW = auto()
    RESOURCE_CHECK = auto()
    APPROVED = auto()
    SCHEDULED = auto()
    COMPLETED = auto()
    REJECTED = auto()
    CANCELLED = auto()


class Permission(Enum):
    """Permissions that can be assigned to members."""
    VIEW_CLUB_INFO = auto()
    PROPOSE_EVENT = auto()
    ATTEND_EVENT = auto()
    APPROVE_BUDGET = auto()
    APPROVE_RESOURCES = auto()
    FINAL_APPROVAL = auto()
    MANAGE_MEMBERS = auto()
    MANAGE_FINANCES = auto()
    VETO_DECISION = auto()
    RECORD_MINUTES = auto()


class TransactionType(Enum):
    """Types of financial transactions."""
    ALLOCATION = auto()
    EXPENSE = auto()
    REVENUE = auto()
    REFUND = auto()
    RESERVATION = auto()
    CANCELLATION_FEE = auto()


class ClubType(Enum):
    """Types of student clubs."""
    ACADEMIC = auto()
    SOCIAL = auto()
    SPORTS = auto()
    CULTURAL = auto()


class ResourceType(Enum):
    """Types of bookable resources."""
    VENUE = auto()
    EQUIPMENT = auto()


# =============================================================================
# CUSTOM EXCEPTIONS
# =============================================================================

class ClubManagementError(Exception):
    """Base exception for all club management errors."""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now()


# --- Member Exceptions ---

class MemberError(ClubManagementError):
    """Base exception for member-related errors."""
    pass


class MemberNotFoundError(MemberError):
    """Raised when a member cannot be found."""
    
    def __init__(self, member_id: str):
        super().__init__(
            f"Member '{member_id}' not found",
            {"member_id": member_id}
        )


class DuplicateMemberError(MemberError):
    """Raised when attempting to add a duplicate member."""
    
    def __init__(self, member_id: str, club_name: str):
        super().__init__(
            f"Member '{member_id}' already exists in club '{club_name}'",
            {"member_id": member_id, "club_name": club_name}
        )


class PermissionDeniedError(MemberError):
    """Raised when a member lacks required permission."""
    
    def __init__(self, member_id: str, permission: Permission, action: str):
        super().__init__(
            f"Permission denied: '{member_id}' lacks {permission.name} for action '{action}'",
            {"member_id": member_id, "permission": permission.name, "action": action}
        )


# --- Event Exceptions ---

class EventError(ClubManagementError):
    """Base exception for event-related errors."""
    pass


class EventNotFoundError(EventError):
    """Raised when an event cannot be found."""
    
    def __init__(self, event_id: str):
        super().__init__(
            f"Event '{event_id}' not found",
            {"event_id": event_id}
        )


class InvalidEventStateError(EventError):
    """Raised when an event operation is invalid for current state."""
    
    def __init__(self, event_id: str, current_state: EventStatus, attempted_action: str):
        super().__init__(
            f"Cannot {attempted_action} event '{event_id}' in state {current_state.name}",
            {"event_id": event_id, "current_state": current_state.name, "action": attempted_action}
        )


class EventCapacityExceededError(EventError):
    """Raised when event capacity is exceeded."""
    
    def __init__(self, event_id: str, capacity: int, current: int):
        super().__init__(
            f"Event '{event_id}' is at capacity ({current}/{capacity})",
            {"event_id": event_id, "capacity": capacity, "current": current}
        )


# --- Financial Exceptions ---

class FinancialError(ClubManagementError):
    """Base exception for financial errors."""
    pass


class InsufficientFundsError(FinancialError):
    """Raised when there are insufficient funds for an operation."""
    
    def __init__(self, required: float, available: float, operation: str):
        super().__init__(
            f"Insufficient funds for {operation}: required ${required:.2f}, available ${available:.2f}",
            {"required": required, "available": available, "operation": operation}
        )


class BudgetExceededError(FinancialError):
    """Raised when an operation would exceed the budget."""
    
    def __init__(self, budget_limit: float, attempted: float):
        super().__init__(
            f"Budget exceeded: limit ${budget_limit:.2f}, attempted ${attempted:.2f}",
            {"budget_limit": budget_limit, "attempted": attempted}
        )


class InvalidTransactionError(FinancialError):
    """Raised when a transaction is invalid."""
    
    def __init__(self, reason: str):
        super().__init__(f"Invalid transaction: {reason}", {"reason": reason})


# --- Resource Exceptions ---

class ResourceError(ClubManagementError):
    """Base exception for resource-related errors."""
    pass


class ResourceNotAvailableError(ResourceError):
    """Raised when a resource is not available."""
    
    def __init__(self, resource_id: str, date: date, reason: str = "already booked"):
        super().__init__(
            f"Resource '{resource_id}' not available on {date}: {reason}",
            {"resource_id": resource_id, "date": str(date), "reason": reason}
        )


class ResourceConflictError(ResourceError):
    """Raised when there is a resource booking conflict."""
    
    def __init__(self, resource_id: str, date: date, existing_event: str):
        super().__init__(
            f"Conflict: Resource '{resource_id}' already booked on {date} for '{existing_event}'",
            {"resource_id": resource_id, "date": str(date), "existing_event": existing_event}
        )


class ResourceNotFoundError(ResourceError):
    """Raised when a resource cannot be found."""
    
    def __init__(self, resource_id: str):
        super().__init__(
            f"Resource '{resource_id}' not found",
            {"resource_id": resource_id}
        )


# --- Approval Exceptions ---

class ApprovalError(ClubManagementError):
    """Base exception for approval-related errors."""
    pass


class ApprovalRequiredError(ApprovalError):
    """Raised when approval is required but not obtained."""
    
    def __init__(self, event_id: str, required_stage: str):
        super().__init__(
            f"Event '{event_id}' requires {required_stage} approval",
            {"event_id": event_id, "required_stage": required_stage}
        )


class UnauthorizedApproverError(ApprovalError):
    """Raised when approver lacks authority for the stage."""
    
    def __init__(self, approver_id: str, stage: str, required_role: str):
        super().__init__(
            f"'{approver_id}' cannot approve {stage} stage (requires {required_role})",
            {"approver_id": approver_id, "stage": stage, "required_role": required_role}
        )


class ApprovalAlreadyProcessedError(ApprovalError):
    """Raised when trying to approve an already processed item."""
    
    def __init__(self, event_id: str, stage: str):
        super().__init__(
            f"Event '{event_id}' has already been processed at {stage} stage",
            {"event_id": event_id, "stage": stage}
        )


# =============================================================================
# INTERFACES
# =============================================================================

class Approvable(ABC):
    """Interface for items that require approval."""
    
    @abstractmethod
    def submit_for_approval(self) -> None:
        """Submit the item for approval workflow."""
        pass
    
    @abstractmethod
    def approve(self, approver: 'ExecutiveMember') -> bool:
        """Approve the item at current stage."""
        pass
    
    @abstractmethod
    def reject(self, approver: 'ExecutiveMember', reason: str) -> None:
        """Reject the item with a reason."""
        pass
    
    @abstractmethod
    def get_approval_status(self) -> Dict[str, Any]:
        """Get current approval status and history."""
        pass


class Trackable(ABC):
    """Interface for items that track attendance/participation."""
    
    @abstractmethod
    def record_attendance(self, member_id: str, role: str = "attendee") -> None:
        """Record a member's attendance."""
        pass
    
    @abstractmethod
    def get_attendance_list(self) -> List[Dict[str, Any]]:
        """Get list of attendees with details."""
        pass
    
    @abstractmethod
    def get_attendance_count(self) -> int:
        """Get total attendance count."""
        pass


# =============================================================================
# OBSERVER PATTERN
# =============================================================================

class Observer(ABC):
    """Observer interface for the Observer pattern."""
    
    @abstractmethod
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """Receive notification of an event."""
        pass


class Observable(ABC):
    """Interface for observable objects."""
    
    @abstractmethod
    def add_observer(self, observer: Observer) -> None:
        """Add an observer."""
        pass
    
    @abstractmethod
    def remove_observer(self, observer: Observer) -> None:
        """Remove an observer."""
        pass
    
    @abstractmethod
    def notify_observers(self, event_type: str, data: Dict[str, Any]) -> None:
        """Notify all observers of an event."""
        pass


# =============================================================================
# STATE PATTERN - Event Approval States
# =============================================================================

class EventState(ABC):
    """Abstract base class for event states."""
    
    @abstractmethod
    def get_status(self) -> EventStatus:
        """Return the status enum for this state."""
        pass
    
    @abstractmethod
    def get_required_approver_role(self) -> Optional[str]:
        """Return the role required to approve this state, or None if no approval needed."""
        pass
    
    @abstractmethod
    def can_transition_to(self, new_status: EventStatus) -> bool:
        """Check if transition to new status is allowed."""
        pass
    
    @abstractmethod
    def process_approval(self, event: 'Event', approver: 'ExecutiveMember') -> 'EventState':
        """Process approval and return new state."""
        pass
    
    @abstractmethod
    def process_rejection(self, event: 'Event', approver: 'ExecutiveMember', reason: str) -> 'EventState':
        """Process rejection and return new state."""
        pass


class ProposedState(EventState):
    """Initial state when event is proposed."""
    
    def get_status(self) -> EventStatus:
        return EventStatus.PROPOSED
    
    def get_required_approver_role(self) -> Optional[str]:
        return None  # Any executive can submit for review
    
    def can_transition_to(self, new_status: EventStatus) -> bool:
        return new_status in [EventStatus.BUDGET_REVIEW, EventStatus.CANCELLED]
    
    def process_approval(self, event: 'Event', approver: 'ExecutiveMember') -> 'EventState':
        # Move to budget review
        return BudgetReviewState()
    
    def process_rejection(self, event: 'Event', approver: 'ExecutiveMember', reason: str) -> 'EventState':
        return RejectedState(reason)


class BudgetReviewState(EventState):
    """State when event is under budget review."""
    
    def get_status(self) -> EventStatus:
        return EventStatus.BUDGET_REVIEW
    
    def get_required_approver_role(self) -> Optional[str]:
        return "Treasurer"
    
    def can_transition_to(self, new_status: EventStatus) -> bool:
        return new_status in [EventStatus.RESOURCE_CHECK, EventStatus.REJECTED]
    
    def process_approval(self, event: 'Event', approver: 'ExecutiveMember') -> 'EventState':
        if approver.role != "Treasurer":
            raise UnauthorizedApproverError(approver.member_id, "BUDGET_REVIEW", "Treasurer")
        return ResourceCheckState()
    
    def process_rejection(self, event: 'Event', approver: 'ExecutiveMember', reason: str) -> 'EventState':
        if approver.role != "Treasurer":
            raise UnauthorizedApproverError(approver.member_id, "BUDGET_REVIEW", "Treasurer")
        return RejectedState(reason)


class ResourceCheckState(EventState):
    """State when event resources are being verified."""
    
    def get_status(self) -> EventStatus:
        return EventStatus.RESOURCE_CHECK
    
    def get_required_approver_role(self) -> Optional[str]:
        return "EventCoordinator"
    
    def can_transition_to(self, new_status: EventStatus) -> bool:
        return new_status in [EventStatus.APPROVED, EventStatus.REJECTED]
    
    def process_approval(self, event: 'Event', approver: 'ExecutiveMember') -> 'EventState':
        if approver.role != "EventCoordinator":
            raise UnauthorizedApproverError(approver.member_id, "RESOURCE_CHECK", "EventCoordinator")
        return ApprovedState()
    
    def process_rejection(self, event: 'Event', approver: 'ExecutiveMember', reason: str) -> 'EventState':
        if approver.role != "EventCoordinator":
            raise UnauthorizedApproverError(approver.member_id, "RESOURCE_CHECK", "EventCoordinator")
        return RejectedState(reason)


class ApprovedState(EventState):
    """State when event has final approval."""
    
    def get_status(self) -> EventStatus:
        return EventStatus.APPROVED
    
    def get_required_approver_role(self) -> Optional[str]:
        return "President"
    
    def can_transition_to(self, new_status: EventStatus) -> bool:
        return new_status in [EventStatus.SCHEDULED, EventStatus.CANCELLED]
    
    def process_approval(self, event: 'Event', approver: 'ExecutiveMember') -> 'EventState':
        if approver.role != "President":
            raise UnauthorizedApproverError(approver.member_id, "FINAL_APPROVAL", "President")
        return ScheduledState()
    
    def process_rejection(self, event: 'Event', approver: 'ExecutiveMember', reason: str) -> 'EventState':
        if approver.role != "President":
            raise UnauthorizedApproverError(approver.member_id, "FINAL_APPROVAL", "President")
        return RejectedState(reason)


class ScheduledState(EventState):
    """State when event is scheduled and confirmed."""
    
    def get_status(self) -> EventStatus:
        return EventStatus.SCHEDULED
    
    def get_required_approver_role(self) -> Optional[str]:
        return None
    
    def can_transition_to(self, new_status: EventStatus) -> bool:
        return new_status in [EventStatus.COMPLETED, EventStatus.CANCELLED]
    
    def process_approval(self, event: 'Event', approver: 'ExecutiveMember') -> 'EventState':
        # Mark as completed
        return CompletedState()
    
    def process_rejection(self, event: 'Event', approver: 'ExecutiveMember', reason: str) -> 'EventState':
        # Cannot reject scheduled event, only cancel
        raise InvalidEventStateError(event.event_id, self.get_status(), "reject")


class CompletedState(EventState):
    """Final state when event is completed."""
    
    def get_status(self) -> EventStatus:
        return EventStatus.COMPLETED
    
    def get_required_approver_role(self) -> Optional[str]:
        return None
    
    def can_transition_to(self, new_status: EventStatus) -> bool:
        return False  # Terminal state
    
    def process_approval(self, event: 'Event', approver: 'ExecutiveMember') -> 'EventState':
        raise InvalidEventStateError(event.event_id, self.get_status(), "approve")
    
    def process_rejection(self, event: 'Event', approver: 'ExecutiveMember', reason: str) -> 'EventState':
        raise InvalidEventStateError(event.event_id, self.get_status(), "reject")


class RejectedState(EventState):
    """State when event is rejected."""
    
    def __init__(self, reason: str = ""):
        self._reason = reason
    
    @property
    def rejection_reason(self) -> str:
        return self._reason
    
    def get_status(self) -> EventStatus:
        return EventStatus.REJECTED
    
    def get_required_approver_role(self) -> Optional[str]:
        return None
    
    def can_transition_to(self, new_status: EventStatus) -> bool:
        return False  # Terminal state
    
    def process_approval(self, event: 'Event', approver: 'ExecutiveMember') -> 'EventState':
        raise InvalidEventStateError(event.event_id, self.get_status(), "approve")
    
    def process_rejection(self, event: 'Event', approver: 'ExecutiveMember', reason: str) -> 'EventState':
        raise InvalidEventStateError(event.event_id, self.get_status(), "reject")


class CancelledState(EventState):
    """State when event is cancelled."""
    
    def __init__(self, reason: str = "", cancellation_fee: float = 0.0):
        self._reason = reason
        self._cancellation_fee = cancellation_fee
    
    @property
    def cancellation_reason(self) -> str:
        return self._reason
    
    @property
    def cancellation_fee(self) -> float:
        return self._cancellation_fee
    
    def get_status(self) -> EventStatus:
        return EventStatus.CANCELLED
    
    def get_required_approver_role(self) -> Optional[str]:
        return None
    
    def can_transition_to(self, new_status: EventStatus) -> bool:
        return False  # Terminal state
    
    def process_approval(self, event: 'Event', approver: 'ExecutiveMember') -> 'EventState':
        raise InvalidEventStateError(event.event_id, self.get_status(), "approve")
    
    def process_rejection(self, event: 'Event', approver: 'ExecutiveMember', reason: str) -> 'EventState':
        raise InvalidEventStateError(event.event_id, self.get_status(), "reject")


# =============================================================================
# MEMBER HIERARCHY
# =============================================================================

class Member(ABC):
    """Abstract base class for all club members."""
    
    def __init__(self, member_id: str, name: str, email: str):
        self._member_id = member_id
        self._name = name
        self._email = email
        self._join_date = date.today()
        self._clubs: List[str] = []  # Club names this member belongs to
    
    @property
    def member_id(self) -> str:
        return self._member_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def email(self) -> str:
        return self._email
    
    @property
    def join_date(self) -> date:
        return self._join_date
    
    @property
    def clubs(self) -> List[str]:
        return self._clubs.copy()
    
    @property
    @abstractmethod
    def role(self) -> str:
        """Return the role name of this member."""
        pass
    
    @abstractmethod
    def get_permissions(self) -> Set[Permission]:
        """Return the set of permissions for this member."""
        pass
    
    def has_permission(self, permission: Permission) -> bool:
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
        return f"{self.role}: {self._name} ({self._member_id})"


class StandardMember(Member):
    """Regular club member with basic permissions."""
    
    def __init__(self, member_id: str, name: str, email: str):
        super().__init__(member_id, name, email)
        self._attendance_count = 0
        self._contributions: List[str] = []  # Event IDs proposed
    
    @property
    def role(self) -> str:
        return "StandardMember"
    
    @property
    def attendance_count(self) -> int:
        return self._attendance_count
    
    def increment_attendance(self) -> None:
        """Increment attendance count."""
        self._attendance_count += 1
    
    def add_contribution(self, event_id: str) -> None:
        """Record an event contribution."""
        self._contributions.append(event_id)
    
    def get_permissions(self) -> Set[Permission]:
        return {
            Permission.VIEW_CLUB_INFO,
            Permission.PROPOSE_EVENT,
            Permission.ATTEND_EVENT
        }
    
    def display_info(self) -> str:
        return (f"Standard Member: {self._name}\n"
                f"  ID: {self._member_id}\n"
                f"  Email: {self._email}\n"
                f"  Joined: {self._join_date}\n"
                f"  Events Attended: {self._attendance_count}\n"
                f"  Contributions: {len(self._contributions)}")


class ExecutiveMember(Member):
    """Abstract base class for executive committee members."""
    
    def __init__(
        self,
        member_id: str,
        name: str,
        email: str,
        term_start: date = None,
        term_end: date = None
    ):
        super().__init__(member_id, name, email)
        self._term_start = term_start or date.today()
        self._term_end = term_end or (date.today() + timedelta(days=365))
        self._is_active = True
    
    @property
    def term_start(self) -> date:
        return self._term_start
    
    @property
    def term_end(self) -> date:
        return self._term_end
    
    @property
    def is_active(self) -> bool:
        return self._is_active and date.today() <= self._term_end
    
    def deactivate(self) -> None:
        """Deactivate the executive role."""
        self._is_active = False
    
    def get_permissions(self) -> Set[Permission]:
        """Base executive permissions."""
        return {
            Permission.VIEW_CLUB_INFO,
            Permission.PROPOSE_EVENT,
            Permission.ATTEND_EVENT,
            Permission.MANAGE_MEMBERS
        }


class President(ExecutiveMember):
    """Club President with final approval authority."""
    
    def __init__(
        self,
        member_id: str,
        name: str,
        email: str,
        term_start: date = None,
        term_end: date = None
    ):
        super().__init__(member_id, name, email, term_start, term_end)
        self._veto_count = 0
        self._final_approvals: List[str] = []
    
    @property
    def role(self) -> str:
        return "President"
    
    @property
    def veto_count(self) -> int:
        return self._veto_count
    
    def record_veto(self) -> None:
        """Record a veto action."""
        self._veto_count += 1
    
    def record_approval(self, event_id: str) -> None:
        """Record a final approval."""
        self._final_approvals.append(event_id)
    
    def get_permissions(self) -> Set[Permission]:
        perms = super().get_permissions()
        perms.update({
            Permission.FINAL_APPROVAL,
            Permission.VETO_DECISION,
            Permission.MANAGE_FINANCES
        })
        return perms
    
    def display_info(self) -> str:
        return (f"President: {self._name}\n"
                f"  ID: {self._member_id}\n"
                f"  Email: {self._email}\n"
                f"  Term: {self._term_start} to {self._term_end}\n"
                f"  Active: {self.is_active}\n"
                f"  Vetoes: {self._veto_count}\n"
                f"  Approvals: {len(self._final_approvals)}")


class Treasurer(ExecutiveMember):
    """Club Treasurer with budget approval authority."""
    
    def __init__(
        self,
        member_id: str,
        name: str,
        email: str,
        term_start: date = None,
        term_end: date = None
    ):
        super().__init__(member_id, name, email, term_start, term_end)
        self._approved_expenses: List[Tuple[str, float]] = []
        self._overdraft_allowance = 0.0
    
    @property
    def role(self) -> str:
        return "Treasurer"
    
    @property
    def total_approved_expenses(self) -> float:
        return sum(amount for _, amount in self._approved_expenses)
    
    def set_overdraft_allowance(self, amount: float) -> None:
        """Set emergency overdraft allowance."""
        self._overdraft_allowance = amount
    
    def record_expense_approval(self, event_id: str, amount: float) -> None:
        """Record an approved expense."""
        self._approved_expenses.append((event_id, amount))
    
    def get_permissions(self) -> Set[Permission]:
        perms = super().get_permissions()
        perms.update({
            Permission.APPROVE_BUDGET,
            Permission.MANAGE_FINANCES
        })
        return perms
    
    def display_info(self) -> str:
        return (f"Treasurer: {self._name}\n"
                f"  ID: {self._member_id}\n"
                f"  Email: {self._email}\n"
                f"  Term: {self._term_start} to {self._term_end}\n"
                f"  Active: {self.is_active}\n"
                f"  Approved Expenses: ${self.total_approved_expenses:.2f}")


class Secretary(ExecutiveMember):
    """Club Secretary managing records and communications."""
    
    def __init__(
        self,
        member_id: str,
        name: str,
        email: str,
        term_start: date = None,
        term_end: date = None
    ):
        super().__init__(member_id, name, email, term_start, term_end)
        self._meetings_recorded = 0
        self._communications_sent = 0
    
    @property
    def role(self) -> str:
        return "Secretary"
    
    @property
    def meetings_recorded(self) -> int:
        return self._meetings_recorded
    
    def record_meeting(self) -> None:
        """Record a meeting."""
        self._meetings_recorded += 1
    
    def record_communication(self) -> None:
        """Record a communication sent."""
        self._communications_sent += 1
    
    def get_permissions(self) -> Set[Permission]:
        perms = super().get_permissions()
        perms.add(Permission.RECORD_MINUTES)
        return perms
    
    def display_info(self) -> str:
        return (f"Secretary: {self._name}\n"
                f"  ID: {self._member_id}\n"
                f"  Email: {self._email}\n"
                f"  Term: {self._term_start} to {self._term_end}\n"
                f"  Active: {self.is_active}\n"
                f"  Meetings Recorded: {self._meetings_recorded}")


class EventCoordinator(ExecutiveMember):
    """Event Coordinator managing logistics and resources."""
    
    def __init__(
        self,
        member_id: str,
        name: str,
        email: str,
        term_start: date = None,
        term_end: date = None
    ):
        super().__init__(member_id, name, email, term_start, term_end)
        self._events_managed: List[str] = []
    
    @property
    def role(self) -> str:
        return "EventCoordinator"
    
    @property
    def events_managed_count(self) -> int:
        return len(self._events_managed)
    
    def add_managed_event(self, event_id: str) -> None:
        """Add an event to managed list."""
        self._events_managed.append(event_id)
    
    def get_permissions(self) -> Set[Permission]:
        perms = super().get_permissions()
        perms.add(Permission.APPROVE_RESOURCES)
        return perms
    
    def display_info(self) -> str:
        return (f"Event Coordinator: {self._name}\n"
                f"  ID: {self._member_id}\n"
                f"  Email: {self._email}\n"
                f"  Term: {self._term_start} to {self._term_end}\n"
                f"  Active: {self.is_active}\n"
                f"  Events Managed: {self.events_managed_count}")


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
        return self._event_id
    
    @property
    def title(self) -> str:
        return self._title
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def proposed_by(self) -> str:
        return self._proposed_by
    
    @property
    def estimated_cost(self) -> float:
        return self._estimated_cost
    
    @property
    def event_date(self) -> date:
        return self._event_date
    
    @property
    def status(self) -> EventStatus:
        return self._state.get_status()
    
    @property
    def approval_history(self) -> List[ApprovalRecord]:
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
        if self._state.get_status() != EventStatus.PROPOSED:
            raise InvalidEventStateError(self._event_id, self.status, "submit for approval")
        self._state = BudgetReviewState()
        self.notify_observers("event_submitted", {
            "event_id": self._event_id,
            "title": self._title,
            "estimated_cost": self._estimated_cost
        })
    
    def approve(self, approver: ExecutiveMember) -> bool:
        """Approve the event at current stage."""
        if not approver.is_active:
            raise PermissionDeniedError(approver.member_id, Permission.FINAL_APPROVAL, "approve event")
        
        old_status = self._state.get_status()
        self._state = self._state.process_approval(self, approver)
        
        # Record approval
        self._approval_history.append(ApprovalRecord(
            stage=old_status.name,
            approver_id=approver.member_id,
            approver_role=approver.role,
            action="approved",
            timestamp=datetime.now()
        ))
        
        self.notify_observers("event_approved", {
            "event_id": self._event_id,
            "stage": old_status.name,
            "approver": approver.member_id,
            "new_status": self._state.get_status().name
        })
        
        return True
    
    def reject(self, approver: ExecutiveMember, reason: str) -> None:
        """Reject the event with a reason."""
        if not approver.is_active:
            raise PermissionDeniedError(approver.member_id, Permission.FINAL_APPROVAL, "reject event")
        
        old_status = self._state.get_status()
        self._state = self._state.process_rejection(self, approver, reason)
        
        # Record rejection
        self._approval_history.append(ApprovalRecord(
            stage=old_status.name,
            approver_id=approver.member_id,
            approver_role=approver.role,
            action="rejected",
            timestamp=datetime.now(),
            notes=reason
        ))
        
        self.notify_observers("event_rejected", {
            "event_id": self._event_id,
            "stage": old_status.name,
            "approver": approver.member_id,
            "reason": reason
        })
    
    def cancel(self, reason: str) -> float:
        """Cancel the event. Returns cancellation fee if applicable."""
        if self.status in [EventStatus.COMPLETED, EventStatus.REJECTED, EventStatus.CANCELLED]:
            raise InvalidEventStateError(self._event_id, self.status, "cancel")
        
        # Calculate cancellation fee (10% if approved or scheduled)
        fee = 0.0
        if self.status in [EventStatus.APPROVED, EventStatus.SCHEDULED]:
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
        if self.status != EventStatus.SCHEDULED:
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
            "current_status": self.status.name,
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
        if self.status not in [EventStatus.SCHEDULED, EventStatus.COMPLETED]:
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
                f"  Status: {self.status.name}\n"
                f"  Date: {self._event_date}\n"
                f"  Cost: ${self.calculate_total_cost():.2f}\n"
                f"  Proposed by: {self._proposed_by}\n"
                f"  Attendance: {self.get_attendance_count()}")
    
    def __str__(self) -> str:
        return f"{self.event_type}({self._event_id}): {self._title} [{self.status.name}]"


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
        super().__init__(event_id, title, description, proposed_by, estimated_cost, event_date)
        self._topic = topic
        self._instructor = instructor
        self._max_participants = max_participants
        self._materials_needed: List[str] = []
    
    @property
    def event_type(self) -> str:
        return "Workshop"
    
    @property
    def topic(self) -> str:
        return self._topic
    
    @property
    def max_participants(self) -> int:
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
        super().__init__(event_id, title, description, proposed_by, estimated_cost, event_date)
        self._theme = theme
        self._expected_attendance = expected_attendance
        self._catering_required = catering_required
        self._catering_cost_per_person = 15.0
    
    @property
    def event_type(self) -> str:
        return "SocialGathering"
    
    @property
    def theme(self) -> str:
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
        super().__init__(event_id, title, description, proposed_by, estimated_cost, event_date)
        self._target_amount = target_amount
        self._actual_raised = 0.0
        self._fundraising_method = fundraising_method
    
    @property
    def event_type(self) -> str:
        return "Fundraiser"
    
    @property
    def target_amount(self) -> float:
        return self._target_amount
    
    @property
    def actual_raised(self) -> float:
        return self._actual_raised
    
    @property
    def net_revenue(self) -> float:
        return self._actual_raised - self._estimated_cost
    
    def record_donation(self, amount: float) -> None:
        """Record a donation."""
        self._actual_raised += amount
    
    def calculate_total_cost(self) -> float:
        """Fundraiser has minimal setup cost."""
        return self._estimated_cost
    
    def get_required_resources(self) -> List[str]:
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
        super().__init__(event_id, title, description, proposed_by, estimated_cost, event_date)
        self._competition_type = competition_type
        self._prize_pool = prize_pool
        self._registration_fee = registration_fee
        self._registrations = 0
    
    @property
    def event_type(self) -> str:
        return "Competition"
    
    @property
    def competition_type(self) -> str:
        return self._competition_type
    
    @property
    def prize_pool(self) -> float:
        return self._prize_pool
    
    @property
    def registration_revenue(self) -> float:
        return self._registrations * self._registration_fee
    
    @property
    def net_cost(self) -> float:
        return self.calculate_total_cost() - self.registration_revenue
    
    def register_participant(self, member_id: str) -> None:
        """Register a participant."""
        self._registrations += 1
        self.record_attendance(member_id, "participant")
    
    def calculate_total_cost(self) -> float:
        """Competition cost = base + prizes."""
        return self._estimated_cost + self._prize_pool
    
    def get_required_resources(self) -> List[str]:
        return self._required_resources + ["venue"]


# =============================================================================
# FINANCIAL MANAGEMENT
# =============================================================================

@dataclass
class Transaction:
    """Represents a financial transaction."""
    transaction_id: str
    transaction_type: TransactionType
    amount: float
    description: str
    timestamp: datetime
    related_event: Optional[str] = None
    balance_after: float = 0.0


class Budget:
    """Manages club budget and transactions."""
    
    def __init__(self, initial_allocation: float = 0.0, overdraft_limit: float = 0.0):
        self._balance = initial_allocation
        self._overdraft_limit = overdraft_limit
        self._transactions: List[Transaction] = []
        self._reserved: Dict[str, float] = {}  # event_id -> reserved amount
        self._transaction_counter = 0
        
        if initial_allocation > 0:
            self._record_transaction(
                TransactionType.ALLOCATION,
                initial_allocation,
                "Initial budget allocation"
            )
    
    @property
    def balance(self) -> float:
        return self._balance
    
    @property
    def available_balance(self) -> float:
        """Balance minus reservations."""
        return self._balance - sum(self._reserved.values())
    
    @property
    def total_reserved(self) -> float:
        return sum(self._reserved.values())
    
    @property
    def transactions(self) -> List[Transaction]:
        return self._transactions.copy()
    
    def _generate_transaction_id(self) -> str:
        self._transaction_counter += 1
        return f"TXN{self._transaction_counter:05d}"
    
    def _record_transaction(
        self,
        txn_type: TransactionType,
        amount: float,
        description: str,
        event_id: str = None
    ) -> Transaction:
        txn = Transaction(
            transaction_id=self._generate_transaction_id(),
            transaction_type=txn_type,
            amount=amount,
            description=description,
            timestamp=datetime.now(),
            related_event=event_id,
            balance_after=self._balance
        )
        self._transactions.append(txn)
        return txn
    
    def can_afford(self, amount: float) -> bool:
        """Check if amount can be afforded."""
        return amount <= self.available_balance + self._overdraft_limit
    
    def reserve_funds(self, event_id: str, amount: float) -> None:
        """Reserve funds for an event."""
        if not self.can_afford(amount):
            raise InsufficientFundsError(amount, self.available_balance, f"reserve for event {event_id}")
        
        self._reserved[event_id] = amount
        self._record_transaction(
            TransactionType.RESERVATION,
            amount,
            f"Funds reserved for event",
            event_id
        )
    
    def release_reservation(self, event_id: str) -> float:
        """Release reserved funds. Returns amount released."""
        amount = self._reserved.pop(event_id, 0.0)
        if amount > 0:
            self._record_transaction(
                TransactionType.REFUND,
                amount,
                f"Reservation released",
                event_id
            )
        return amount
    
    def spend(self, event_id: str, amount: float, description: str = "") -> None:
        """Spend reserved funds."""
        if event_id in self._reserved:
            # Use reservation
            reserved = self._reserved.pop(event_id)
            self._balance -= amount
            if amount < reserved:
                # Refund difference
                self._balance += (reserved - amount)
        else:
            if amount > self.available_balance + self._overdraft_limit:
                raise InsufficientFundsError(amount, self.available_balance, description)
            self._balance -= amount
        
        self._record_transaction(
            TransactionType.EXPENSE,
            amount,
            description or f"Expense for event",
            event_id
        )
    
    def add_revenue(self, amount: float, description: str, event_id: str = None) -> None:
        """Add revenue to budget."""
        self._balance += amount
        self._record_transaction(
            TransactionType.REVENUE,
            amount,
            description,
            event_id
        )
    
    def add_allocation(self, amount: float, description: str = "Budget allocation") -> None:
        """Add budget allocation."""
        self._balance += amount
        self._record_transaction(
            TransactionType.ALLOCATION,
            amount,
            description
        )
    
    def apply_cancellation_fee(self, event_id: str, fee: float) -> None:
        """Apply cancellation fee."""
        self.release_reservation(event_id)
        if fee > 0:
            self._balance -= fee
            self._record_transaction(
                TransactionType.CANCELLATION_FEE,
                fee,
                f"Cancellation fee",
                event_id
            )
    
    def get_financial_report(self) -> str:
        """Generate a financial report."""
        lines = [
            "=" * 50,
            "FINANCIAL REPORT",
            "=" * 50,
            f"Current Balance: ${self._balance:.2f}",
            f"Reserved Funds: ${self.total_reserved:.2f}",
            f"Available: ${self.available_balance:.2f}",
            f"Overdraft Limit: ${self._overdraft_limit:.2f}",
            "",
            "Recent Transactions:",
            "-" * 50
        ]
        
        for txn in self._transactions[-10:]:
            lines.append(
                f"  {txn.timestamp.strftime('%Y-%m-%d %H:%M')} | "
                f"{txn.transaction_type.name:15} | "
                f"${txn.amount:>10.2f} | {txn.description[:20]}"
            )
        
        return "\n".join(lines)


# =============================================================================
# RESOURCE MANAGEMENT
# =============================================================================

@dataclass
class Booking:
    """Represents a resource booking."""
    booking_id: str
    resource_id: str
    event_id: str
    booking_date: date
    booked_by: str
    created_at: datetime = field(default_factory=datetime.now)


class Resource(ABC):
    """Abstract base class for bookable resources."""
    
    def __init__(self, resource_id: str, name: str):
        self._resource_id = resource_id
        self._name = name
        self._bookings: Dict[date, Booking] = {}
    
    @property
    def resource_id(self) -> str:
        return self._resource_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    @abstractmethod
    def resource_type(self) -> ResourceType:
        pass
    
    def is_available(self, booking_date: date) -> bool:
        """Check if resource is available on date."""
        return booking_date not in self._bookings
    
    def book(self, event_id: str, booking_date: date, booked_by: str) -> Booking:
        """Book the resource for an event."""
        if not self.is_available(booking_date):
            existing = self._bookings[booking_date]
            raise ResourceConflictError(self._resource_id, booking_date, existing.event_id)
        
        booking = Booking(
            booking_id=f"BK{len(self._bookings)+1:04d}",
            resource_id=self._resource_id,
            event_id=event_id,
            booking_date=booking_date,
            booked_by=booked_by
        )
        self._bookings[booking_date] = booking
        return booking
    
    def cancel_booking(self, booking_date: date) -> None:
        """Cancel a booking."""
        if booking_date in self._bookings:
            del self._bookings[booking_date]
    
    def get_bookings(self) -> List[Booking]:
        """Get all bookings."""
        return list(self._bookings.values())


class Venue(Resource):
    """A bookable venue/room."""
    
    def __init__(
        self,
        resource_id: str,
        name: str,
        capacity: int,
        has_av_equipment: bool = False
    ):
        super().__init__(resource_id, name)
        self._capacity = capacity
        self._has_av_equipment = has_av_equipment
    
    @property
    def resource_type(self) -> ResourceType:
        return ResourceType.VENUE
    
    @property
    def capacity(self) -> int:
        return self._capacity
    
    @property
    def has_av_equipment(self) -> bool:
        return self._has_av_equipment
    
    def __str__(self) -> str:
        av = "with AV" if self._has_av_equipment else "no AV"
        return f"Venue: {self._name} (capacity: {self._capacity}, {av})"


class Equipment(Resource):
    """Bookable equipment with quantity tracking."""
    
    def __init__(
        self,
        resource_id: str,
        name: str,
        total_quantity: int
    ):
        super().__init__(resource_id, name)
        self._total_quantity = total_quantity
        self._quantity_bookings: Dict[date, int] = {}
    
    @property
    def resource_type(self) -> ResourceType:
        return ResourceType.EQUIPMENT
    
    @property
    def total_quantity(self) -> int:
        return self._total_quantity
    
    def available_quantity(self, booking_date: date) -> int:
        """Get available quantity for a date."""
        booked = self._quantity_bookings.get(booking_date, 0)
        return self._total_quantity - booked
    
    def is_available(self, booking_date: date, quantity: int = 1) -> bool:
        """Check if required quantity is available."""
        return self.available_quantity(booking_date) >= quantity
    
    def book_quantity(
        self,
        event_id: str,
        booking_date: date,
        booked_by: str,
        quantity: int
    ) -> Booking:
        """Book a quantity of equipment."""
        if not self.is_available(booking_date, quantity):
            raise ResourceNotAvailableError(
                self._resource_id,
                booking_date,
                f"only {self.available_quantity(booking_date)} available, requested {quantity}"
            )
        
        self._quantity_bookings[booking_date] = (
            self._quantity_bookings.get(booking_date, 0) + quantity
        )
        
        return super().book(event_id, booking_date, booked_by)
    
    def __str__(self) -> str:
        return f"Equipment: {self._name} (total: {self._total_quantity})"


class ResourceManager:
    """Manages resource availability and bookings."""
    
    def __init__(self):
        self._resources: Dict[str, Resource] = {}
    
    def add_resource(self, resource: Resource) -> None:
        """Add a resource to manage."""
        self._resources[resource.resource_id] = resource
    
    def get_resource(self, resource_id: str) -> Resource:
        """Get a resource by ID."""
        if resource_id not in self._resources:
            raise ResourceNotFoundError(resource_id)
        return self._resources[resource_id]
    
    def check_availability(
        self,
        resource_ids: List[str],
        booking_date: date
    ) -> Dict[str, bool]:
        """Check availability of multiple resources."""
        return {
            rid: self._resources[rid].is_available(booking_date)
            for rid in resource_ids
            if rid in self._resources
        }
    
    def book_resources(
        self,
        resource_ids: List[str],
        event_id: str,
        booking_date: date,
        booked_by: str
    ) -> List[Booking]:
        """Book multiple resources for an event."""
        bookings = []
        for rid in resource_ids:
            resource = self.get_resource(rid)
            booking = resource.book(event_id, booking_date, booked_by)
            bookings.append(booking)
        return bookings
    
    def cancel_bookings(self, event_id: str) -> None:
        """Cancel all bookings for an event."""
        for resource in self._resources.values():
            for booking_date, booking in list(resource._bookings.items()):
                if booking.event_id == event_id:
                    resource.cancel_booking(booking_date)
    
    def get_all_venues(self) -> List[Venue]:
        """Get all venues."""
        return [r for r in self._resources.values() if isinstance(r, Venue)]
    
    def get_all_equipment(self) -> List[Equipment]:
        """Get all equipment."""
        return [r for r in self._resources.values() if isinstance(r, Equipment)]


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
        self._club_id = club_id
        self._name = name
        self._club_type = club_type
        self._budget = Budget(initial_budget)
        self._members: Dict[str, Member] = {}
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
        return self._club_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def club_type(self) -> ClubType:
        return self._club_type
    
    @property
    def budget(self) -> Budget:
        return self._budget
    
    @property
    def member_count(self) -> int:
        return len(self._members)
    
    @property
    def president(self) -> Optional[President]:
        return self._president
    
    @property
    def treasurer(self) -> Optional[Treasurer]:
        return self._treasurer
    
    # Observable implementation
    def add_observer(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)
    
    def remove_observer(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify_observers(self, event_type: str, data: Dict[str, Any]) -> None:
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
        elif isinstance(member, Treasurer):
            self._treasurer = member
        elif isinstance(member, Secretary):
            self._secretary = member
        elif isinstance(member, EventCoordinator):
            self._event_coordinator = member
        
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
        
        self.notify_observers("member_removed", {
            "member_id": member_id,
            "name": member.name
        })
    
    def get_all_members(self) -> List[Member]:
        """Get all members."""
        return list(self._members.values())
    
    def get_executives(self) -> List[ExecutiveMember]:
        """Get all executive members."""
        return [m for m in self._members.values() if isinstance(m, ExecutiveMember)]
    
    # Event management
    def propose_event(self, event: Event, proposer_id: str) -> None:
        """Add a proposed event."""
        member = self.get_member(proposer_id)
        
        if not member.has_permission(Permission.PROPOSE_EVENT):
            raise PermissionDeniedError(proposer_id, Permission.PROPOSE_EVENT, "propose event")
        
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
        
        if not isinstance(approver, ExecutiveMember):
            raise PermissionDeniedError(approver_id, Permission.FINAL_APPROVAL, "approve event")
        
        if approve:
            # Budget check if in budget review
            if event.status == EventStatus.BUDGET_REVIEW:
                cost = event.calculate_total_cost()
                if not self._budget.can_afford(cost):
                    raise InsufficientFundsError(cost, self._budget.available_balance, "event approval")
                # Reserve funds
                self._budget.reserve_funds(event_id, cost)
            
            # Resource check if in resource check
            if event.status == EventStatus.RESOURCE_CHECK:
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
        
        if event.status not in [EventStatus.APPROVED, EventStatus.SCHEDULED]:
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
            f"Type: {self._club_type.name}",
            f"Members: {self.member_count}",
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
        
        for status in EventStatus:
            events = self.get_events_by_status(status)
            if events:
                lines.append(f"  {status.name}: {len(events)}")
        
        return "\n".join(lines)
    
    def __str__(self) -> str:
        return f"Club: {self._name} ({self._club_type.name}) - {self.member_count} members"


# =============================================================================
# FACTORY PATTERN
# =============================================================================

class ClubFactory:
    """Factory for creating clubs with predefined configurations."""
    
    _club_counter = 0
    
    @classmethod
    def _generate_club_id(cls) -> str:
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
            "academic": ClubType.ACADEMIC,
            "social": ClubType.SOCIAL,
            "sports": ClubType.SPORTS,
            "cultural": ClubType.CULTURAL
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


# =============================================================================
# SINGLETON PATTERN - Club Registry
# =============================================================================

class SingletonMeta(type):
    """Metaclass for implementing Singleton pattern."""
    
    _instances: Dict[type, Any] = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class ClubRegistry(metaclass=SingletonMeta):
    """
    Singleton registry for all clubs.
    Ensures single source of truth for club data.
    """
    
    def __init__(self):
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
        counts = {}
        for club in self._clubs.values():
            type_name = club.club_type.name
            counts[type_name] = counts.get(type_name, 0) + 1
        return counts


# =============================================================================
# OBSERVER IMPLEMENTATIONS
# =============================================================================

class AttendanceTracker(Observer):
    """Tracks attendance across all events."""
    
    def __init__(self):
        self._attendance_records: List[Dict[str, Any]] = []
        self._member_attendance: Dict[str, int] = {}
    
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        if event_type == "attendance_recorded":
            self._attendance_records.append({
                "timestamp": datetime.now().isoformat(),
                **data
            })
            member_id = data.get("member_id")
            if member_id:
                self._member_attendance[member_id] = (
                    self._member_attendance.get(member_id, 0) + 1
                )
            print(f"  📋 ATTENDANCE: {data.get('member_id')} checked in to {data.get('event_id')}")
    
    def get_member_attendance_count(self, member_id: str) -> int:
        return self._member_attendance.get(member_id, 0)
    
    def get_attendance_report(self) -> str:
        lines = ["ATTENDANCE REPORT", "-" * 40]
        for member_id, count in sorted(self._member_attendance.items(), key=lambda x: -x[1]):
            lines.append(f"  {member_id}: {count} events")
        return "\n".join(lines)


class EngagementAnalytics(Observer):
    """Analyzes member engagement patterns."""
    
    def __init__(self):
        self._events_log: List[Dict[str, Any]] = []
    
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        self._events_log.append({
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            **data
        })
        
        if event_type == "event_completed":
            print(f"  📊 ANALYTICS: Event {data.get('event_id')} completed with "
                  f"{data.get('attendance_count', 0)} attendees")
    
    def get_event_count_by_type(self) -> Dict[str, int]:
        counts = {}
        for log in self._events_log:
            event_type = log.get("event_type", "unknown")
            counts[event_type] = counts.get(event_type, 0) + 1
        return counts


class NotificationService(Observer):
    """Sends notifications for club activities."""
    
    def __init__(self):
        self._notifications: List[Dict[str, Any]] = []
    
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        notification = {
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self._notifications.append(notification)
        
        # Print notifications
        club_name = data.get("club_name", "Unknown Club")
        
        if event_type == "event_proposed":
            print(f"  📧 NOTIFICATION: New event proposed in {club_name}: {data.get('title')}")
        elif event_type == "event_approved":
            print(f"  ✅ NOTIFICATION: Event {data.get('event_id')} approved at {data.get('stage')}")
        elif event_type == "event_rejected":
            print(f"  ❌ NOTIFICATION: Event {data.get('event_id')} rejected: {data.get('reason')}")
        elif event_type == "event_completed":
            print(f"  🎉 NOTIFICATION: Event {data.get('event_id')} completed!")
        elif event_type == "member_added":
            print(f"  👋 NOTIFICATION: {data.get('name')} joined {club_name} as {data.get('role')}")
    
    def get_notifications(self) -> List[Dict[str, Any]]:
        return self._notifications.copy()


# =============================================================================
# MAIN DEMONSTRATION
# =============================================================================

def main():
    """Demonstrate the Club Management System functionality."""
    
    print("=" * 70)
    print("   UNICLUB STUDENT CLUB MANAGEMENT SYSTEM - DEMONSTRATION")
    print("=" * 70)
    
    # =========================================================================
    # 1. SINGLETON PATTERN - Club Registry
    # =========================================================================
    print("\n" + "=" * 60)
    print("1. SINGLETON PATTERN - Club Registry")
    print("=" * 60)
    
    registry1 = ClubRegistry()
    registry2 = ClubRegistry()
    
    print(f"Registry 1 ID: {id(registry1)}")
    print(f"Registry 2 ID: {id(registry2)}")
    print(f"Same instance: {registry1 is registry2}")
    
    # Add global observers
    attendance_tracker = AttendanceTracker()
    analytics = EngagementAnalytics()
    notifications = NotificationService()
    
    registry1.add_global_observer(attendance_tracker)
    registry1.add_global_observer(analytics)
    registry1.add_global_observer(notifications)
    
    # =========================================================================
    # 2. FACTORY PATTERN - Club Creation
    # =========================================================================
    print("\n" + "=" * 60)
    print("2. FACTORY PATTERN - Club Creation")
    print("=" * 60)
    
    ai_club = ClubFactory.create_club("academic", "AI Research Society", 5000.0)
    sports_club = ClubFactory.create_club("sports", "Tennis Club", 4000.0, equipment_budget=1500.0)
    
    registry1.register_club(ai_club)
    registry1.register_club(sports_club)
    
    print(f"Created: {ai_club}")
    print(f"Created: {sports_club}")
    print(f"Sports Club Budget: ${sports_club.budget.balance:.2f}")
    
    # =========================================================================
    # 3. MEMBER HIERARCHY - Polymorphism
    # =========================================================================
    print("\n" + "=" * 60)
    print("3. MEMBER HIERARCHY - Inheritance & Polymorphism")
    print("=" * 60)
    
    # Create members for AI Club
    president = President("P001", "Alice Chen", "alice@uni.edu")
    treasurer = Treasurer("T001", "Bob Smith", "bob@uni.edu")
    secretary = Secretary("S001", "Carol White", "carol@uni.edu")
    coordinator = EventCoordinator("E001", "David Lee", "david@uni.edu")
    member1 = StandardMember("M001", "Eve Johnson", "eve@uni.edu")
    member2 = StandardMember("M002", "Frank Brown", "frank@uni.edu")
    
    # Add to club
    for member in [president, treasurer, secretary, coordinator, member1, member2]:
        ai_club.add_member(member)
    
    print("\nMembers Added (with Observer notifications):")
    print(f"\nExecutives: {len(ai_club.get_executives())}")
    
    # Demonstrate polymorphism
    print("\nRole Permissions (Polymorphism):")
    print("-" * 50)
    for member in [president, treasurer, member1]:
        perms = [p.name for p in member.get_permissions()]
        print(f"  {member.role}: {', '.join(perms[:4])}...")
    
    # =========================================================================
    # 4. EVENT HIERARCHY & STATE PATTERN
    # =========================================================================
    print("\n" + "=" * 60)
    print("4. EVENT HIERARCHY & STATE PATTERN - Approval Workflow")
    print("=" * 60)
    
    # Create a workshop event
    workshop = Workshop(
        event_id="EVT001",
        title="Introduction to Machine Learning",
        description="Hands-on ML workshop for beginners",
        proposed_by="M001",
        estimated_cost=200.0,
        topic="Machine Learning",
        instructor="Dr. Smith",
        max_participants=25
    )
    
    print(f"\n--- Proposing Event ---")
    ai_club.propose_event(workshop, "M001")
    print(f"Event Status: {workshop.status.name}")
    
    print(f"\n--- Submitting for Approval ---")
    workshop.submit_for_approval()
    print(f"Event Status: {workshop.status.name}")
    print(f"Required Approver: {workshop._state.get_required_approver_role()}")
    
    print(f"\n--- Budget Review (Treasurer) ---")
    ai_club.process_event_approval("EVT001", "T001", approve=True)
    print(f"Event Status: {workshop.status.name}")
    print(f"Required Approver: {workshop._state.get_required_approver_role()}")
    
    print(f"\n--- Resource Check (Coordinator) ---")
    ai_club.process_event_approval("EVT001", "E001", approve=True)
    print(f"Event Status: {workshop.status.name}")
    print(f"Required Approver: {workshop._state.get_required_approver_role()}")
    
    print(f"\n--- Final Approval (President) ---")
    ai_club.process_event_approval("EVT001", "P001", approve=True)
    print(f"Event Status: {workshop.status.name}")
    
    # =========================================================================
    # 5. FINANCIAL MANAGEMENT
    # =========================================================================
    print("\n" + "=" * 60)
    print("5. FINANCIAL MANAGEMENT - Budget Tracking")
    print("=" * 60)
    
    print(f"\nBudget before event completion:")
    print(f"  Balance: ${ai_club.budget.balance:.2f}")
    print(f"  Reserved: ${ai_club.budget.total_reserved:.2f}")
    print(f"  Available: ${ai_club.budget.available_balance:.2f}")
    
    # Schedule and complete the event
    workshop.record_attendance("M001", "organizer")
    workshop.record_attendance("M002", "attendee")
    
    ai_club.complete_event("EVT001", actual_cost=180.0)
    
    print(f"\nBudget after event completion:")
    print(f"  Balance: ${ai_club.budget.balance:.2f}")
    
    # =========================================================================
    # 6. CUSTOM EXCEPTIONS
    # =========================================================================
    print("\n" + "=" * 60)
    print("6. CUSTOM EXCEPTION HANDLING")
    print("=" * 60)
    
    print("\n--- Insufficient Funds ---")
    expensive_event = SocialGathering(
        event_id="EVT002",
        title="Grand Gala",
        description="Annual celebration",
        proposed_by="M001",
        estimated_cost=10000.0,
        theme="Masquerade",
        expected_attendance=200
    )
    ai_club.propose_event(expensive_event, "M001")
    expensive_event.submit_for_approval()
    
    try:
        ai_club.process_event_approval("EVT002", "T001", approve=True)
    except InsufficientFundsError as e:
        print(f"  Caught: {e.message}")
    
    print("\n--- Permission Denied ---")
    try:
        # Standard member tries to approve
        workshop2 = Workshop(
            event_id="EVT003",
            title="Python Workshop",
            description="Learn Python",
            proposed_by="M002",
            estimated_cost=50.0,
            topic="Python",
            instructor="John",
            max_participants=20
        )
        ai_club.propose_event(workshop2, "M002")
        workshop2.submit_for_approval()
        workshop2.approve(member1)  # Standard member trying to approve
    except (PermissionDeniedError, AttributeError) as e:
        print(f"  Caught: StandardMember cannot approve events")
    
    print("\n--- Invalid State Transition ---")
    try:
        # Try to approve already completed event
        workshop.approve(president)
    except InvalidEventStateError as e:
        print(f"  Caught: {e.message}")
    
    print("\n--- Unauthorized Approver ---")
    try:
        # Secretary tries to approve budget
        workshop3 = Workshop(
            event_id="EVT004",
            title="Writing Workshop",
            description="Learn writing",
            proposed_by="M001",
            estimated_cost=75.0,
            topic="Writing",
            instructor="Jane",
            max_participants=15
        )
        ai_club.propose_event(workshop3, "M001")
        workshop3.submit_for_approval()
        workshop3.approve(secretary)  # Secretary trying to approve budget
    except UnauthorizedApproverError as e:
        print(f"  Caught: {e.message}")
    
    # =========================================================================
    # 7. OBSERVER PATTERN - Attendance & Notifications
    # =========================================================================
    print("\n" + "=" * 60)
    print("7. OBSERVER PATTERN - Attendance Tracking")
    print("=" * 60)
    
    # Create and complete another event
    competition = Competition(
        event_id="EVT005",
        title="Coding Competition",
        description="Annual coding challenge",
        proposed_by="E001",
        estimated_cost=100.0,
        competition_type="Hackathon",
        prize_pool=500.0,
        registration_fee=10.0
    )
    
    ai_club.propose_event(competition, "E001")
    competition.submit_for_approval()
    ai_club.process_event_approval("EVT005", "T001", approve=True)
    ai_club.process_event_approval("EVT005", "E001", approve=True)
    ai_club.process_event_approval("EVT005", "P001", approve=True)
    
    # Record attendance (observers will be notified)
    print("\n--- Recording Attendance ---")
    competition.register_participant("M001")
    competition.register_participant("M002")
    
    ai_club.complete_event("EVT005")
    
    # =========================================================================
    # 8. REGISTRY STATISTICS
    # =========================================================================
    print("\n" + "=" * 60)
    print("8. REGISTRY STATISTICS")
    print("=" * 60)
    
    stats = registry1.get_statistics()
    print(f"\nClub Registry Summary:")
    print(f"  Total Clubs: {stats['total_clubs']}")
    print(f"  Total Members: {stats['total_members']}")
    print(f"  Total Events: {stats['total_events']}")
    print(f"  Total Budget: ${stats['total_budget']:.2f}")
    
    # =========================================================================
    # 9. CLUB REPORT
    # =========================================================================
    print("\n" + "=" * 60)
    print("9. CLUB REPORT")
    print("=" * 60)
    
    print(ai_club.get_club_report())
    
    # =========================================================================
    # 10. FINANCIAL REPORT
    # =========================================================================
    print("\n" + "=" * 60)
    print("10. FINANCIAL REPORT")
    print("=" * 60)
    
    print(ai_club.budget.get_financial_report())
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 60)
    print("   OOP CONCEPTS DEMONSTRATED")
    print("=" * 60)
    print("""
    ✓ Encapsulation
      - Private attributes (_member_id, _balance)
      - Properties with validation
      - Protected data access
    
    ✓ Inheritance
      - Member hierarchy (StandardMember, ExecutiveMember → President, Treasurer)
      - Event hierarchy (Workshop, SocialGathering, Fundraiser, Competition)
      - Resource hierarchy (Venue, Equipment)
    
    ✓ Polymorphism
      - get_permissions() varies by member type
      - calculate_total_cost() varies by event type
      - process_approval() varies by state
    
    ✓ Abstraction
      - Approvable interface (submit_for_approval, approve, reject)
      - Trackable interface (record_attendance, get_attendance_list)
      - Observable interface (add_observer, notify_observers)
    
    ✓ State Pattern
      - EventState classes manage approval workflow
      - Transitions: PROPOSED → BUDGET_REVIEW → RESOURCE_CHECK → APPROVED
    
    ✓ Factory Pattern
      - ClubFactory.create_club() with type-specific configuration
    
    ✓ Observer Pattern
      - AttendanceTracker, EngagementAnalytics, NotificationService
    
    ✓ Singleton Pattern
      - ClubRegistry using SingletonMeta metaclass
    
    ✓ Custom Exceptions
      - Full hierarchy from ClubManagementError
      - Specific exceptions with context data
    """)
    
    print("=" * 60)
    print("   DEMONSTRATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
