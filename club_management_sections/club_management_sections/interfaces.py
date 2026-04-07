"""Abstract interfaces that define approvable, trackable, and observable behaviour."""

from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
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

