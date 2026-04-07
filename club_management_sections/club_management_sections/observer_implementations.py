"""Concrete observers for attendance tracking, analytics, and notifications."""

from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Set, Any, Tuple
from dataclasses import dataclass, field

from observer_pattern import Observer
# =============================================================================
# OBSERVER IMPLEMENTATIONS
# =============================================================================


class AttendanceTracker(Observer):
    """Tracks attendance across all events."""
    
    def __init__(self):
        """Initialise a new AttendanceTracker instance."""
        self._attendance_records: List[Dict[str, Any]] = []
        self._member_attendance: Dict[str, int] = {}
    
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """Execute update."""
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
            print(f"  [ATTENDANCE] {data.get('member_id')} checked in to {data.get('event_id')}")
    
    def get_member_attendance_count(self, member_id: str) -> int:
        """Return the member attendance count."""
        return self._member_attendance.get(member_id, 0)
    
    def get_attendance_report(self) -> str:
        """Return the attendance report."""
        lines = ["ATTENDANCE REPORT", "-" * 40]
        for member_id, count in sorted(self._member_attendance.items(), key=lambda x: -x[1]):
            lines.append(f"  {member_id}: {count} events")
        return "\n".join(lines)


class EngagementAnalytics(Observer):
    """Analyzes member engagement patterns."""
    
    def __init__(self):
        """Initialise a new EngagementAnalytics instance."""
        self._events_log: List[Dict[str, Any]] = []
    
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """Execute update."""
        self._events_log.append({
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            **data
        })
        
        if event_type == "event_completed":
            print(f"  [ANALYTICS] Event {data.get('event_id')} completed with "
                  f"{data.get('attendance_count', 0)} attendees")
    
    def get_event_count_by_type(self) -> Dict[str, int]:
        """Return the event count by type."""
        counts = {}
        for log in self._events_log:
            event_type = log.get("event_type", "unknown")
            counts[event_type] = counts.get(event_type, 0) + 1
        return counts


class NotificationService(Observer):
    """Sends notifications for club activities."""
    
    def __init__(self):
        """Initialise a new NotificationService instance."""
        self._notifications: List[Dict[str, Any]] = []
    
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """Execute update."""
        notification = {
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self._notifications.append(notification)
        
        # Print notifications
        club_name = data.get("club_name", "Unknown Club")
        
        if event_type == "event_proposed":
            print(f"  [NOTIFICATION] New event proposed in {club_name}: {data.get('title')}")
        elif event_type == "event_approved":
            print(f"  [NOTIFICATION] Event {data.get('event_id')} approved at {data.get('stage')}")
        elif event_type == "event_rejected":
            print(f"  [NOTIFICATION] Event {data.get('event_id')} rejected: {data.get('reason')}")
        elif event_type == "event_completed":
            print(f"  [NOTIFICATION] Event {data.get('event_id')} completed!")
        elif event_type == "member_added":
            print(f"  [NOTIFICATION] {data.get('name')} joined {club_name} as {data.get('role')}")
    
    def get_notifications(self) -> List[Dict[str, Any]]:
        """Return the notifications."""
        return self._notifications.copy()

