"""State pattern implementation for event approval and lifecycle transitions."""

from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
# =============================================================================
# STATE PATTERN - Event Approval States
# =============================================================================


class EventState(ABC):
    """Abstract base class for event states."""
    
    @abstractmethod
    def get_status(self) -> str:
        """Return the status string for this state."""
        pass
    
    @abstractmethod
    def get_required_approver_role(self) -> Optional[str]:
        """Return the role required to approve this state, or None if no approval needed."""
        pass
    
    @abstractmethod
    def can_transition_to(self, new_status: str) -> bool:
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
    
    def get_status(self) -> str:
        """Return the status."""
        return EventStatus._PROPOSED
    
    def get_required_approver_role(self) -> Optional[str]:
        """Return the required approver role."""
        return None  # Any executive can submit for review
    
    def can_transition_to(self, new_status: str) -> bool:
        """Check whether this ProposedState can transition to."""
        return new_status in [EventStatus._BUDGET_REVIEW, EventStatus._CANCELLED]
    
    def process_approval(self, event: 'Event', approver: 'ExecutiveMember') -> 'EventState':
        # Move to budget review
        """Process approval."""
        return BudgetReviewState()
    
    def process_rejection(self, event: 'Event', approver: 'ExecutiveMember', reason: str) -> 'EventState':
        """Process rejection."""
        return RejectedState(reason)


class BudgetReviewState(EventState):
    """State when event is under budget review."""
    
    def get_status(self) -> str:
        """Return the status."""
        return EventStatus._BUDGET_REVIEW
    
    def get_required_approver_role(self) -> Optional[str]:
        """Return the required approver role."""
        return "Treasurer"
    
    def can_transition_to(self, new_status: str) -> bool:
        """Check whether this BudgetReviewState can transition to."""
        return new_status in [EventStatus._RESOURCE_CHECK, EventStatus._REJECTED]
    
    def process_approval(self, event: 'Event', approver: 'ExecutiveMember') -> 'EventState':
        """Process approval."""
        if approver.role != "Treasurer":
            raise UnauthorizedApproverError(approver.member_id, "BUDGET_REVIEW", "Treasurer")
        return ResourceCheckState()
    
    def process_rejection(self, event: 'Event', approver: 'ExecutiveMember', reason: str) -> 'EventState':
        """Process rejection."""
        if approver.role != "Treasurer":
            raise UnauthorizedApproverError(approver.member_id, "BUDGET_REVIEW", "Treasurer")
        return RejectedState(reason)


class ResourceCheckState(EventState):
    """State when event resources are being verified."""
    
    def get_status(self) -> str:
        """Return the status."""
        return EventStatus._RESOURCE_CHECK
    
    def get_required_approver_role(self) -> Optional[str]:
        """Return the required approver role."""
        return "EventCoordinator"
    
    def can_transition_to(self, new_status: str) -> bool:
        """Check whether this ResourceCheckState can transition to."""
        return new_status in [EventStatus._APPROVED, EventStatus._REJECTED]
    
    def process_approval(self, event: 'Event', approver: 'ExecutiveMember') -> 'EventState':
        """Process approval."""
        if approver.role != "EventCoordinator":
            raise UnauthorizedApproverError(approver.member_id, "RESOURCE_CHECK", "EventCoordinator")
        return ApprovedState()
    
    def process_rejection(self, event: 'Event', approver: 'ExecutiveMember', reason: str) -> 'EventState':
        """Process rejection."""
        if approver.role != "EventCoordinator":
            raise UnauthorizedApproverError(approver.member_id, "RESOURCE_CHECK", "EventCoordinator")
        return RejectedState(reason)


class ApprovedState(EventState):
    """State when event has final approval."""
    
    def get_status(self) -> str:
        """Return the status."""
        return EventStatus._APPROVED
    
    def get_required_approver_role(self) -> Optional[str]:
        """Return the required approver role."""
        return "President"
    
    def can_transition_to(self, new_status: str) -> bool:
        """Check whether this ApprovedState can transition to."""
        return new_status in [EventStatus._SCHEDULED, EventStatus._CANCELLED]
    
    def process_approval(self, event: 'Event', approver: 'ExecutiveMember') -> 'EventState':
        """Process approval."""
        if approver.role != "President":
            raise UnauthorizedApproverError(approver.member_id, "FINAL_APPROVAL", "President")
        return ScheduledState()
    
    def process_rejection(self, event: 'Event', approver: 'ExecutiveMember', reason: str) -> 'EventState':
        """Process rejection."""
        if approver.role != "President":
            raise UnauthorizedApproverError(approver.member_id, "FINAL_APPROVAL", "President")
        return RejectedState(reason)


class ScheduledState(EventState):
    """State when event is scheduled and confirmed."""
    
    def get_status(self) -> str:
        """Return the status."""
        return EventStatus._SCHEDULED
    
    def get_required_approver_role(self) -> Optional[str]:
        """Return the required approver role."""
        return None
    
    def can_transition_to(self, new_status: str) -> bool:
        """Check whether this ScheduledState can transition to."""
        return new_status in [EventStatus._COMPLETED, EventStatus._CANCELLED]
    
    def process_approval(self, event: 'Event', approver: 'ExecutiveMember') -> 'EventState':
        # Mark as completed
        """Process approval."""
        return CompletedState()
    
    def process_rejection(self, event: 'Event', approver: 'ExecutiveMember', reason: str) -> 'EventState':
        # Cannot reject scheduled event, only cancel
        """Process rejection."""
        raise InvalidEventStateError(event.event_id, self.get_status(), "reject")


class CompletedState(EventState):
    """Final state when event is completed."""
    
    def get_status(self) -> str:
        """Return the status."""
        return EventStatus._COMPLETED
    
    def get_required_approver_role(self) -> Optional[str]:
        """Return the required approver role."""
        return None
    
    def can_transition_to(self, new_status: str) -> bool:
        """Check whether this CompletedState can transition to."""
        return False  # Terminal state
    
    def process_approval(self, event: 'Event', approver: 'ExecutiveMember') -> 'EventState':
        """Process approval."""
        raise InvalidEventStateError(event.event_id, self.get_status(), "approve")
    
    def process_rejection(self, event: 'Event', approver: 'ExecutiveMember', reason: str) -> 'EventState':
        """Process rejection."""
        raise InvalidEventStateError(event.event_id, self.get_status(), "reject")


class RejectedState(EventState):
    """State when event is rejected."""
    
    def __init__(self, reason: str = ""):
        """Initialise a new RejectedState instance."""
        self._reason = reason
    
    @property
    def rejection_reason(self) -> str:
        """Execute rejection reason."""
        return self._reason
    
    def get_status(self) -> str:
        """Return the status."""
        return EventStatus._REJECTED
    
    def get_required_approver_role(self) -> Optional[str]:
        """Return the required approver role."""
        return None
    
    def can_transition_to(self, new_status: str) -> bool:
        """Check whether this RejectedState can transition to."""
        return False  # Terminal state
    
    def process_approval(self, event: 'Event', approver: 'ExecutiveMember') -> 'EventState':
        """Process approval."""
        raise InvalidEventStateError(event.event_id, self.get_status(), "approve")
    
    def process_rejection(self, event: 'Event', approver: 'ExecutiveMember', reason: str) -> 'EventState':
        """Process rejection."""
        raise InvalidEventStateError(event.event_id, self.get_status(), "reject")


class CancelledState(EventState):
    """State when event is cancelled."""
    
    def __init__(self, reason: str = "", cancellation_fee: float = 0.0):
        """Initialise a new CancelledState instance."""
        self._reason = reason
        self._cancellation_fee = cancellation_fee
    
    @property
    def cancellation_reason(self) -> str:
        """Execute cancellation reason."""
        return self._reason
    
    @property
    def cancellation_fee(self) -> float:
        """Execute cancellation fee."""
        return self._cancellation_fee
    
    def get_status(self) -> str:
        """Return the status."""
        return EventStatus._CANCELLED
    
    def get_required_approver_role(self) -> Optional[str]:
        """Return the required approver role."""
        return None
    
    def can_transition_to(self, new_status: str) -> bool:
        """Check whether this CancelledState can transition to."""
        return False  # Terminal state
    
    def process_approval(self, event: 'Event', approver: 'ExecutiveMember') -> 'EventState':
        """Process approval."""
        raise InvalidEventStateError(event.event_id, self.get_status(), "approve")
    
    def process_rejection(self, event: 'Event', approver: 'ExecutiveMember', reason: str) -> 'EventState':
        """Process rejection."""
        raise InvalidEventStateError(event.event_id, self.get_status(), "reject")

