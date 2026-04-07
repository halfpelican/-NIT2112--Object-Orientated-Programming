"""Resource booking models and managers for venues and equipment."""

from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Set, Any, Tuple
from dataclasses import dataclass, field

from constants import ResourceType
from exceptions import ResourceConflictError, ResourceNotAvailableError, ResourceNotFoundError
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
        """Initialise a new Resource instance."""
        self._resource_id = resource_id
        self._name = name
        self._bookings: Dict[date, Booking] = {}
    
    @property
    def resource_id(self) -> str:
        """Execute resource id."""
        return self._resource_id
    
    @property
    def name(self) -> str:
        """Execute name."""
        return self._name
    
    @property
    @abstractmethod
    def resource_type(self) -> ResourceType:
        """Execute resource type."""
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
        """Initialise a new Venue instance."""
        super().__init__(resource_id, name)
        self._capacity = capacity
        self._has_av_equipment = has_av_equipment
    
    @property
    def resource_type(self) -> str:
        """Execute resource type."""
        return ResourceType._VENUE
    
    @property
    def capacity(self) -> int:
        """Execute capacity."""
        return self._capacity
    
    @property
    def has_av_equipment(self) -> bool:
        """Execute has av equipment."""
        return self._has_av_equipment
    
    def __str__(self) -> str:
        """Execute str."""
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
        """Initialise a new Equipment instance."""
        super().__init__(resource_id, name)
        self._total_quantity = total_quantity
        self._quantity_bookings: Dict[date, int] = {}
    
    @property
    def resource_type(self) -> str:
        """Execute resource type."""
        return ResourceType._EQUIPMENT
    
    @property
    def total_quantity(self) -> int:
        """Execute total quantity."""
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
        """Execute str."""
        return f"Equipment: {self._name} (total: {self._total_quantity})"


class ResourceManager:
    """Manages resource availability and bookings."""
    
    def __init__(self):
        """Initialise a new ResourceManager instance."""
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

