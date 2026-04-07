"""Custom exception hierarchy used across the club management system."""

from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
# =============================================================================
# CUSTOM EXCEPTIONS
# =============================================================================


class ClubManagementError(Exception):
    """Base exception for all club management errors."""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        """Initialise a new ClubManagementError instance."""
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
        """Initialise a new MemberNotFoundError instance."""
        super().__init__(
            f"Member '{member_id}' not found",
            {"member_id": member_id}
        )


class DuplicateMemberError(MemberError):
    """Raised when attempting to add a duplicate member."""
    
    def __init__(self, member_id: str, club_name: str):
        """Initialise a new DuplicateMemberError instance."""
        super().__init__(
            f"Member '{member_id}' already exists in club '{club_name}'",
            {"member_id": member_id, "club_name": club_name}
        )


class PermissionDeniedError(MemberError):
    """Raised when a member lacks required permission."""
    
    def __init__(self, member_id: str, permission: str, action: str):
        """Initialise a new PermissionDeniedError instance."""
        super().__init__(
            f"Permission denied: '{member_id}' lacks {permission} for action '{action}'",
            {"member_id": member_id, "permission": permission, "action": action}
        )


# --- Event Exceptions ---

class EventError(ClubManagementError):
    """Base exception for event-related errors."""
    pass


class EventNotFoundError(EventError):
    """Raised when an event cannot be found."""
    
    def __init__(self, event_id: str):
        """Initialise a new EventNotFoundError instance."""
        super().__init__(
            f"Event '{event_id}' not found",
            {"event_id": event_id}
        )


class InvalidEventStateError(EventError):
    """Raised when an event operation is invalid for current state."""
    
    def __init__(self, event_id: str, current_state: str, attempted_action: str):
        """Initialise a new InvalidEventStateError instance."""
        super().__init__(
            f"Cannot {attempted_action} event '{event_id}' in state {current_state}",
            {"event_id": event_id, "current_state": current_state, "action": attempted_action}
        )


class EventCapacityExceededError(EventError):
    """Raised when event capacity is exceeded."""
    
    def __init__(self, event_id: str, capacity: int, current: int):
        """Initialise a new EventCapacityExceededError instance."""
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
        """Initialise a new InsufficientFundsError instance."""
        super().__init__(
            f"Insufficient funds for {operation}: required ${required:.2f}, available ${available:.2f}",
            {"required": required, "available": available, "operation": operation}
        )


class BudgetExceededError(FinancialError):
    """Raised when an operation would exceed the budget."""
    
    def __init__(self, budget_limit: float, attempted: float):
        """Initialise a new BudgetExceededError instance."""
        super().__init__(
            f"Budget exceeded: limit ${budget_limit:.2f}, attempted ${attempted:.2f}",
            {"budget_limit": budget_limit, "attempted": attempted}
        )


class InvalidTransactionError(FinancialError):
    """Raised when a transaction is invalid."""
    
    def __init__(self, reason: str):
        """Initialise a new InvalidTransactionError instance."""
        super().__init__(f"Invalid transaction: {reason}", {"reason": reason})


# --- Resource Exceptions ---

class ResourceError(ClubManagementError):
    """Base exception for resource-related errors."""
    pass


class ResourceNotAvailableError(ResourceError):
    """Raised when a resource is not available."""
    
    def __init__(self, resource_id: str, date: date, reason: str = "already booked"):
        """Initialise a new ResourceNotAvailableError instance."""
        super().__init__(
            f"Resource '{resource_id}' not available on {date}: {reason}",
            {"resource_id": resource_id, "date": str(date), "reason": reason}
        )


class ResourceConflictError(ResourceError):
    """Raised when there is a resource booking conflict."""
    
    def __init__(self, resource_id: str, date: date, existing_event: str):
        """Initialise a new ResourceConflictError instance."""
        super().__init__(
            f"Conflict: Resource '{resource_id}' already booked on {date} for '{existing_event}'",
            {"resource_id": resource_id, "date": str(date), "existing_event": existing_event}
        )


class ResourceNotFoundError(ResourceError):
    """Raised when a resource cannot be found."""
    
    def __init__(self, resource_id: str):
        """Initialise a new ResourceNotFoundError instance."""
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
        """Initialise a new ApprovalRequiredError instance."""
        super().__init__(
            f"Event '{event_id}' requires {required_stage} approval",
            {"event_id": event_id, "required_stage": required_stage}
        )


class UnauthorizedApproverError(ApprovalError):
    """Raised when approver lacks authority for the stage."""
    
    def __init__(self, approver_id: str, stage: str, required_role: str):
        """Initialise a new UnauthorizedApproverError instance."""
        super().__init__(
            f"'{approver_id}' cannot approve {stage} stage (requires {required_role})",
            {"approver_id": approver_id, "stage": stage, "required_role": required_role}
        )


class ApprovalAlreadyProcessedError(ApprovalError):
    """Raised when trying to approve an already processed item."""
    
    def __init__(self, event_id: str, stage: str):
        """Initialise a new ApprovalAlreadyProcessedError instance."""
        super().__init__(
            f"Event '{event_id}' has already been processed at {stage} stage",
            {"event_id": event_id, "stage": stage}
        )

