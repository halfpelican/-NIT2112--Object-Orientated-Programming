"""
Hotel Booking System - Complete OOP Reference Implementation
============================================================

This module demonstrates all major Object-Oriented Programming concepts:
1. Class Hierarchies with Abstract Base Classes (ABC)
2. Interfaces via ABC classes
3. Encapsulation with private attributes and properties
4. Custom Exception hierarchies
5. Design Patterns: Factory, Adapter, Observer, Singleton
6. Enums for type safety
7. Business logic implementation

Author: OOP Teaching Reference
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple, Protocol, Any
import uuid


# =============================================================================
# ENUMS - Type-safe constants for the system
# =============================================================================

class RoomType(Enum):
    """Types of rooms available in the hotel."""
    STANDARD = "standard"
    DELUXE = "deluxe"
    SUITE = "suite"
    PENTHOUSE = "penthouse"


class RoomStatus(Enum):
    """Current status of a room."""
    AVAILABLE = auto()
    OCCUPIED = auto()
    RESERVED = auto()
    MAINTENANCE = auto()
    CLEANING = auto()


class BookingStatus(Enum):
    """Status of a booking throughout its lifecycle."""
    PENDING = auto()
    CONFIRMED = auto()
    CHECKED_IN = auto()
    CHECKED_OUT = auto()
    CANCELLED = auto()
    NO_SHOW = auto()


class GuestType(Enum):
    """Types of guests with different privileges."""
    WALK_IN = "walk_in"
    MEMBER = "member"
    VIP = "vip"
    CORPORATE = "corporate"


class Season(Enum):
    """Seasonal pricing periods."""
    PEAK = "peak"          # Summer, holidays - highest rates
    REGULAR = "regular"    # Normal periods
    OFF_PEAK = "off_peak"  # Low demand - discounted rates


class ServiceType(Enum):
    """Types of services available to guests."""
    ROOM_SERVICE = ("Room Service", Decimal("25.00"))
    LAUNDRY = ("Laundry Service", Decimal("35.00"))
    SPA = ("Spa Treatment", Decimal("150.00"))
    MINIBAR = ("Minibar Charges", Decimal("0.00"))  # Variable
    PARKING = ("Valet Parking", Decimal("30.00"))
    WIFI_PREMIUM = ("Premium WiFi", Decimal("15.00"))

    def __init__(self, display_name: str, base_charge: Decimal):
        self.display_name = display_name
        self.base_charge = base_charge


class NotificationType(Enum):
    """Types of notifications sent by the observer system."""
    BOOKING_CONFIRMED = "booking_confirmed"
    BOOKING_CANCELLED = "booking_cancelled"
    CHECK_IN = "check_in"
    CHECK_OUT = "check_out"
    ROOM_SERVICE_REQUEST = "room_service_request"
    MAINTENANCE_REQUEST = "maintenance_request"
    PAYMENT_RECEIVED = "payment_received"


# =============================================================================
# CUSTOM EXCEPTIONS - Hierarchical exception structure
# =============================================================================

class HotelException(Exception):
    """Base exception for all hotel-related errors."""
    
    def __init__(self, message: str, code: Optional[str] = None):
        self.message = message
        self.code = code or "HOTEL_ERROR"
        super().__init__(self.message)
    
    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


class RoomException(HotelException):
    """Base exception for room-related errors."""
    
    def __init__(self, message: str, room_number: Optional[str] = None):
        self.room_number = room_number
        super().__init__(message, "ROOM_ERROR")


class RoomNotAvailableError(RoomException):
    """Raised when a room is not available for booking."""
    
    def __init__(self, room_number: str, reason: str = "Room is not available"):
        super().__init__(f"{reason}: Room {room_number}", room_number)
        self.code = "ROOM_NOT_AVAILABLE"


class RoomNotFoundError(RoomException):
    """Raised when a room cannot be found."""
    
    def __init__(self, room_number: str):
        super().__init__(f"Room not found: {room_number}", room_number)
        self.code = "ROOM_NOT_FOUND"


class InvalidRoomTypeError(RoomException):
    """Raised when an invalid room type is specified."""
    
    def __init__(self, room_type: str):
        super().__init__(f"Invalid room type: {room_type}")
        self.code = "INVALID_ROOM_TYPE"


class BookingException(HotelException):
    """Base exception for booking-related errors."""
    
    def __init__(self, message: str, booking_id: Optional[str] = None):
        self.booking_id = booking_id
        super().__init__(message, "BOOKING_ERROR")


class BookingNotFoundError(BookingException):
    """Raised when a booking cannot be found."""
    
    def __init__(self, booking_id: str):
        super().__init__(f"Booking not found: {booking_id}", booking_id)
        self.code = "BOOKING_NOT_FOUND"


class InvalidDateRangeError(BookingException):
    """Raised when booking dates are invalid."""
    
    def __init__(self, check_in: datetime, check_out: datetime):
        message = f"Invalid date range: {check_in.date()} to {check_out.date()}"
        super().__init__(message)
        self.code = "INVALID_DATE_RANGE"
        self.check_in = check_in
        self.check_out = check_out


class GuestLimitExceededError(BookingException):
    """Raised when number of guests exceeds room capacity."""
    
    def __init__(self, requested: int, capacity: int, room_number: str):
        message = f"Guest limit exceeded for room {room_number}: {requested} > {capacity}"
        super().__init__(message)
        self.code = "GUEST_LIMIT_EXCEEDED"
        self.requested = requested
        self.capacity = capacity


class CancellationNotAllowedError(BookingException):
    """Raised when a booking cannot be cancelled."""
    
    def __init__(self, booking_id: str, reason: str):
        super().__init__(f"Cannot cancel booking {booking_id}: {reason}", booking_id)
        self.code = "CANCELLATION_NOT_ALLOWED"


class PaymentException(HotelException):
    """Base exception for payment-related errors."""
    
    def __init__(self, message: str, amount: Optional[Decimal] = None):
        self.amount = amount
        super().__init__(message, "PAYMENT_ERROR")


class PaymentFailedError(PaymentException):
    """Raised when a payment fails."""
    
    def __init__(self, amount: Decimal, reason: str = "Payment processing failed"):
        super().__init__(f"{reason}: ${amount}", amount)
        self.code = "PAYMENT_FAILED"


class RefundNotAllowedError(PaymentException):
    """Raised when a refund is not allowed."""
    
    def __init__(self, booking_id: str, reason: str):
        super().__init__(f"Refund not allowed for booking {booking_id}: {reason}")
        self.code = "REFUND_NOT_ALLOWED"
        self.booking_id = booking_id


class ServiceException(HotelException):
    """Base exception for service-related errors."""
    
    def __init__(self, message: str, service_type: Optional[ServiceType] = None):
        self.service_type = service_type
        super().__init__(message, "SERVICE_ERROR")


class ServiceUnavailableError(ServiceException):
    """Raised when a service is not available."""
    
    def __init__(self, service_type: ServiceType, reason: str = "Service unavailable"):
        super().__init__(f"{reason}: {service_type.display_name}", service_type)
        self.code = "SERVICE_UNAVAILABLE"


# =============================================================================
# INTERFACES (Abstract Base Classes)
# =============================================================================

class Bookable(ABC):
    """Interface for objects that can be booked."""
    
    @abstractmethod
    def check_availability(self, check_in: datetime, check_out: datetime) -> bool:
        """Check if the resource is available for the given dates."""
        pass
    
    @abstractmethod
    def reserve(self, check_in: datetime, check_out: datetime) -> str:
        """Reserve the resource, returning a reservation ID."""
        pass
    
    @abstractmethod
    def confirm(self, reservation_id: str) -> bool:
        """Confirm a reservation."""
        pass
    
    @abstractmethod
    def cancel(self, reservation_id: str) -> bool:
        """Cancel a reservation."""
        pass


class Priceable(ABC):
    """Interface for objects that have pricing calculations."""
    
    @abstractmethod
    def calculate_total(self) -> Decimal:
        """Calculate the total price."""
        pass
    
    @abstractmethod
    def apply_discount(self, discount_percent: Decimal) -> Decimal:
        """Apply a discount and return the discounted total."""
        pass
    
    @abstractmethod
    def get_taxes(self) -> Decimal:
        """Get the tax amount."""
        pass


class Observer(ABC):
    """Interface for observer pattern - observers that receive updates."""
    
    @abstractmethod
    def update(self, event_type: NotificationType, data: Dict[str, Any]) -> None:
        """Receive notification of an event."""
        pass


class Observable(ABC):
    """Interface for observer pattern - subjects that notify observers."""
    
    @abstractmethod
    def add_observer(self, observer: Observer) -> None:
        """Add an observer to receive notifications."""
        pass
    
    @abstractmethod
    def remove_observer(self, observer: Observer) -> None:
        """Remove an observer from notifications."""
        pass
    
    @abstractmethod
    def notify_observers(self, event_type: NotificationType, data: Dict[str, Any]) -> None:
        """Notify all observers of an event."""
        pass


class Serviceable(ABC):
    """Interface for objects that can receive services."""
    
    @abstractmethod
    def request_service(self, service_type: ServiceType, details: Dict[str, Any]) -> str:
        """Request a service, returning a service request ID."""
        pass
    
    @abstractmethod
    def get_service_charges(self) -> Decimal:
        """Get total service charges."""
        pass


# =============================================================================
# SINGLETON PATTERN - Hotel Registry using Metaclass
# =============================================================================

class SingletonMeta(type):
    """
    Metaclass that creates a Singleton instance.
    
    This ensures only one instance of the class exists throughout
    the application lifecycle.
    """
    _instances: Dict[type, Any] = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
    
    @classmethod
    def reset_instance(mcs, cls: type) -> None:
        """Reset the singleton instance (useful for testing)."""
        if cls in mcs._instances:
            del mcs._instances[cls]


class HotelRegistry(metaclass=SingletonMeta):
    """
    Central registry for the hotel system.
    
    Implements the Singleton pattern using a metaclass to ensure
    only one registry exists. Stores all rooms, guests, bookings,
    and service records.
    """
    
    def __init__(self):
        self._rooms: Dict[str, 'Room'] = {}
        self._guests: Dict[str, 'Guest'] = {}
        self._bookings: Dict[str, 'Booking'] = {}
        self._services: Dict[str, Dict[str, Any]] = {}
        self._hotel_name: str = "Grand OOP Hotel"
        self._seasonal_rates: Dict[Season, Decimal] = {
            Season.PEAK: Decimal("1.50"),      # 50% increase
            Season.REGULAR: Decimal("1.00"),   # Standard rate
            Season.OFF_PEAK: Decimal("0.75"),  # 25% discount
        }
        print(f"[Registry] {self._hotel_name} Registry initialized")
    
    @property
    def hotel_name(self) -> str:
        return self._hotel_name
    
    def register_room(self, room: 'Room') -> None:
        """Register a room in the hotel."""
        self._rooms[room.room_number] = room
        print(f"[Registry] Room {room.room_number} registered")
    
    def get_room(self, room_number: str) -> 'Room':
        """Get a room by number."""
        if room_number not in self._rooms:
            raise RoomNotFoundError(room_number)
        return self._rooms[room_number]
    
    def get_all_rooms(self) -> List['Room']:
        """Get all registered rooms."""
        return list(self._rooms.values())
    
    def get_available_rooms(self, check_in: datetime, check_out: datetime,
                           room_type: Optional[RoomType] = None) -> List['Room']:
        """Get available rooms for given dates and optional type."""
        available = []
        for room in self._rooms.values():
            if room.check_availability(check_in, check_out):
                if room_type is None or room.room_type == room_type:
                    available.append(room)
        return available
    
    def register_guest(self, guest: 'Guest') -> None:
        """Register a guest in the system."""
        self._guests[guest.guest_id] = guest
        print(f"[Registry] Guest {guest.name} (ID: {guest.guest_id}) registered")
    
    def get_guest(self, guest_id: str) -> 'Guest':
        """Get a guest by ID."""
        if guest_id not in self._guests:
            raise HotelException(f"Guest not found: {guest_id}", "GUEST_NOT_FOUND")
        return self._guests[guest_id]
    
    def get_all_guests(self) -> List['Guest']:
        """Get all registered guests."""
        return list(self._guests.values())
    
    def register_booking(self, booking: 'Booking') -> None:
        """Register a booking in the system."""
        self._bookings[booking.booking_id] = booking
        print(f"[Registry] Booking {booking.booking_id} registered")
    
    def get_booking(self, booking_id: str) -> 'Booking':
        """Get a booking by ID."""
        if booking_id not in self._bookings:
            raise BookingNotFoundError(booking_id)
        return self._bookings[booking_id]
    
    def get_all_bookings(self) -> List['Booking']:
        """Get all bookings."""
        return list(self._bookings.values())
    
    def get_seasonal_multiplier(self, season: Season) -> Decimal:
        """Get the rate multiplier for a season."""
        return self._seasonal_rates[season]
    
    def record_service(self, service_id: str, details: Dict[str, Any]) -> None:
        """Record a service request."""
        self._services[service_id] = details
    
    def get_service(self, service_id: str) -> Dict[str, Any]:
        """Get service details by ID."""
        return self._services.get(service_id, {})


# =============================================================================
# OBSERVER PATTERN - Notification System
# =============================================================================

class GuestNotifier(Observer):
    """Observer that notifies guests of events via email/SMS simulation."""
    
    def __init__(self):
        self.notifications_sent: List[Tuple[NotificationType, str]] = []
    
    def update(self, event_type: NotificationType, data: Dict[str, Any]) -> None:
        guest_name = data.get('guest_name', 'Guest')
        message = f"[Guest Notification] Dear {guest_name}, "
        
        if event_type == NotificationType.BOOKING_CONFIRMED:
            message += f"Your booking {data.get('booking_id')} is confirmed!"
        elif event_type == NotificationType.CHECK_IN:
            message += f"Welcome! Your room {data.get('room_number')} is ready."
        elif event_type == NotificationType.CHECK_OUT:
            message += "Thank you for staying with us!"
        elif event_type == NotificationType.BOOKING_CANCELLED:
            message += f"Your booking {data.get('booking_id')} has been cancelled."
        else:
            message += f"Event: {event_type.value}"
        
        print(message)
        self.notifications_sent.append((event_type, message))


class HousekeepingNotifier(Observer):
    """Observer that notifies housekeeping department."""
    
    def __init__(self):
        self.tasks: List[Dict[str, Any]] = []
    
    def update(self, event_type: NotificationType, data: Dict[str, Any]) -> None:
        room_number = data.get('room_number', 'Unknown')
        
        if event_type == NotificationType.CHECK_OUT:
            task = {
                'type': 'full_cleaning',
                'room': room_number,
                'priority': 'high'
            }
            self.tasks.append(task)
            print(f"[Housekeeping] Full cleaning scheduled for room {room_number}")
        
        elif event_type == NotificationType.CHECK_IN:
            task = {
                'type': 'welcome_amenities',
                'room': room_number,
                'priority': 'immediate'
            }
            self.tasks.append(task)
            print(f"[Housekeeping] Welcome amenities prepared for room {room_number}")
        
        elif event_type == NotificationType.ROOM_SERVICE_REQUEST:
            print(f"[Housekeeping] Service request noted for room {room_number}")


class FrontDeskNotifier(Observer):
    """Observer that notifies front desk staff."""
    
    def __init__(self):
        self.alerts: List[str] = []
    
    def update(self, event_type: NotificationType, data: Dict[str, Any]) -> None:
        alert = f"[Front Desk] {event_type.value.upper()}: "
        
        if event_type == NotificationType.BOOKING_CONFIRMED:
            alert += f"New booking {data.get('booking_id')} - Prepare registration"
        elif event_type == NotificationType.CHECK_IN:
            guest_type = data.get('guest_type', 'Standard')
            alert += f"{guest_type} guest arriving - Room {data.get('room_number')}"
        elif event_type == NotificationType.CHECK_OUT:
            alert += f"Room {data.get('room_number')} checked out - Process billing"
        elif event_type == NotificationType.BOOKING_CANCELLED:
            alert += f"Booking {data.get('booking_id')} cancelled - Update availability"
        else:
            alert += f"Event data: {data}"
        
        print(alert)
        self.alerts.append(alert)


class BillingNotifier(Observer):
    """Observer that notifies billing department."""
    
    def __init__(self):
        self.transactions: List[Dict[str, Any]] = []
    
    def update(self, event_type: NotificationType, data: Dict[str, Any]) -> None:
        if event_type == NotificationType.CHECK_OUT:
            transaction = {
                'booking_id': data.get('booking_id'),
                'total': data.get('total', Decimal("0.00")),
                'status': 'pending_settlement'
            }
            self.transactions.append(transaction)
            print(f"[Billing] Final bill prepared: ${data.get('total', 0):.2f}")
        
        elif event_type == NotificationType.PAYMENT_RECEIVED:
            print(f"[Billing] Payment of ${data.get('amount', 0):.2f} received")
        
        elif event_type == NotificationType.ROOM_SERVICE_REQUEST:
            charge = data.get('charge', Decimal("0.00"))
            print(f"[Billing] Service charge ${charge:.2f} added to room account")


class BookingNotificationSystem(Observable):
    """
    Central notification system implementing the Observer pattern.
    
    Manages observers and distributes notifications to all registered
    observers when events occur in the booking system.
    """
    
    def __init__(self):
        self._observers: List[Observer] = []
        print("[Notification System] Initialized")
    
    def add_observer(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)
            print(f"[Notification System] Observer {observer.__class__.__name__} added")
    
    def remove_observer(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)
            print(f"[Notification System] Observer {observer.__class__.__name__} removed")
    
    def notify_observers(self, event_type: NotificationType, data: Dict[str, Any]) -> None:
        print(f"\n--- Sending {event_type.value} notifications ---")
        for observer in self._observers:
            observer.update(event_type, data)
        print("--- Notifications complete ---\n")


# =============================================================================
# ROOM HIERARCHY - Abstract Base Class and Concrete Implementations
# =============================================================================

class Room(Bookable):
    """
    Abstract base class for all room types.
    
    Demonstrates:
    - Abstract methods that must be implemented
    - Encapsulation with private attributes
    - Properties with getters/setters
    - Template method pattern for pricing
    
    Note: Inherits from Bookable which already inherits from ABC,
    so this class is automatically abstract.
    """
    
    TAX_RATE = Decimal("0.12")  # 12% tax rate
    
    def __init__(self, room_number: str, floor: int, view: str = "Standard"):
        # Private attributes (encapsulation)
        self._room_number = room_number
        self._floor = floor
        self._view = view
        self._status = RoomStatus.AVAILABLE
        self._reservations: List[Tuple[datetime, datetime, str]] = []
        self._current_booking_id: Optional[str] = None
    
    # Properties with validation (encapsulation)
    @property
    def room_number(self) -> str:
        return self._room_number
    
    @property
    def floor(self) -> int:
        return self._floor
    
    @property
    def view(self) -> str:
        return self._view
    
    @property
    def status(self) -> RoomStatus:
        return self._status
    
    @status.setter
    def status(self, value: RoomStatus) -> None:
        if not isinstance(value, RoomStatus):
            raise ValueError("Status must be a RoomStatus enum value")
        old_status = self._status
        self._status = value
        print(f"[Room {self._room_number}] Status: {old_status.name} -> {value.name}")
    
    @property
    def current_booking_id(self) -> Optional[str]:
        return self._current_booking_id
    
    @current_booking_id.setter
    def current_booking_id(self, booking_id: Optional[str]) -> None:
        self._current_booking_id = booking_id
    
    # Abstract properties that subclasses must implement
    @property
    @abstractmethod
    def room_type(self) -> RoomType:
        """The type of room."""
        pass
    
    @property
    @abstractmethod
    def base_rate(self) -> Decimal:
        """Base nightly rate before seasonal adjustments."""
        pass
    
    @property
    @abstractmethod
    def capacity(self) -> int:
        """Maximum number of guests."""
        pass
    
    @property
    @abstractmethod
    def amenities(self) -> List[str]:
        """List of amenities included in the room."""
        pass
    
    @property
    @abstractmethod
    def minimum_stay(self) -> int:
        """Minimum number of nights required."""
        pass
    
    # Bookable interface implementation
    def check_availability(self, check_in: datetime, check_out: datetime) -> bool:
        """Check if room is available for the given date range."""
        if self._status in (RoomStatus.MAINTENANCE, RoomStatus.CLEANING):
            return False
        
        for res_start, res_end, _ in self._reservations:
            # Check for overlap
            if not (check_out <= res_start or check_in >= res_end):
                return False
        return True
    
    def reserve(self, check_in: datetime, check_out: datetime) -> str:
        """Create a reservation for this room."""
        if not self.check_availability(check_in, check_out):
            raise RoomNotAvailableError(
                self._room_number,
                f"Not available from {check_in.date()} to {check_out.date()}"
            )
        
        reservation_id = f"RES-{uuid.uuid4().hex[:8].upper()}"
        self._reservations.append((check_in, check_out, reservation_id))
        self._status = RoomStatus.RESERVED
        return reservation_id
    
    def confirm(self, reservation_id: str) -> bool:
        """Confirm a reservation."""
        for start, end, res_id in self._reservations:
            if res_id == reservation_id:
                print(f"[Room {self._room_number}] Reservation {reservation_id} confirmed")
                return True
        return False
    
    def cancel(self, reservation_id: str) -> bool:
        """Cancel a reservation."""
        for i, (start, end, res_id) in enumerate(self._reservations):
            if res_id == reservation_id:
                self._reservations.pop(i)
                if not self._reservations:
                    self._status = RoomStatus.AVAILABLE
                print(f"[Room {self._room_number}] Reservation {reservation_id} cancelled")
                return True
        return False
    
    def calculate_rate(self, season: Season) -> Decimal:
        """Calculate the nightly rate based on season."""
        registry = HotelRegistry()
        multiplier = registry.get_seasonal_multiplier(season)
        return (self.base_rate * multiplier).quantize(Decimal("0.01"), ROUND_HALF_UP)
    
    def calculate_stay_cost(self, check_in: datetime, check_out: datetime,
                           season: Season) -> Decimal:
        """Calculate total cost for a stay (excluding taxes)."""
        nights = (check_out - check_in).days
        if nights < self.minimum_stay:
            raise BookingException(
                f"Minimum stay for {self.room_type.value} is {self.minimum_stay} nights"
            )
        nightly_rate = self.calculate_rate(season)
        return nightly_rate * nights
    
    def __str__(self) -> str:
        return (f"{self.room_type.value.title()} Room {self._room_number} "
                f"(Floor {self._floor}, {self._view} View)")
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}('{self._room_number}')>"


class StandardRoom(Room):
    """Standard room with basic amenities."""
    
    @property
    def room_type(self) -> RoomType:
        return RoomType.STANDARD
    
    @property
    def base_rate(self) -> Decimal:
        return Decimal("120.00")
    
    @property
    def capacity(self) -> int:
        return 2
    
    @property
    def amenities(self) -> List[str]:
        return ["WiFi", "TV", "Air Conditioning", "Mini Fridge", "Coffee Maker"]
    
    @property
    def minimum_stay(self) -> int:
        return 1


class DeluxeRoom(Room):
    """Deluxe room with enhanced amenities and more space."""
    
    @property
    def room_type(self) -> RoomType:
        return RoomType.DELUXE
    
    @property
    def base_rate(self) -> Decimal:
        return Decimal("200.00")
    
    @property
    def capacity(self) -> int:
        return 3
    
    @property
    def amenities(self) -> List[str]:
        return [
            "WiFi", "Smart TV", "Air Conditioning", "Mini Bar",
            "Coffee Maker", "Bathrobe", "Complimentary Breakfast",
            "Room Service", "Safe"
        ]
    
    @property
    def minimum_stay(self) -> int:
        return 1


class Suite(Room):
    """Suite with separate living area and premium amenities."""
    
    @property
    def room_type(self) -> RoomType:
        return RoomType.SUITE
    
    @property
    def base_rate(self) -> Decimal:
        return Decimal("350.00")
    
    @property
    def capacity(self) -> int:
        return 4
    
    @property
    def amenities(self) -> List[str]:
        return [
            "High-Speed WiFi", "65\" Smart TV", "Climate Control",
            "Full Mini Bar", "Espresso Machine", "Premium Bathrobe",
            "Complimentary Breakfast", "24/7 Room Service", "In-Room Safe",
            "Living Room", "Dining Area", "Jacuzzi Tub", "Turndown Service"
        ]
    
    @property
    def minimum_stay(self) -> int:
        return 2


class PenthouseSuite(Room):
    """Top-floor penthouse with luxury amenities and views."""
    
    @property
    def room_type(self) -> RoomType:
        return RoomType.PENTHOUSE
    
    @property
    def base_rate(self) -> Decimal:
        return Decimal("800.00")
    
    @property
    def capacity(self) -> int:
        return 6
    
    @property
    def amenities(self) -> List[str]:
        return [
            "Premium High-Speed WiFi", "Multiple 75\" Smart TVs",
            "Individual Climate Control", "Fully Stocked Bar",
            "Professional Espresso Machine", "Luxury Bathrobes",
            "Personal Chef Available", "24/7 Butler Service",
            "Multiple Safes", "Grand Living Room", "Private Dining Room",
            "Master Bedroom with Jacuzzi", "Private Terrace",
            "Panoramic City Views", "Private Elevator Access",
            "Complimentary Spa Access", "Airport Transfer Included"
        ]
    
    @property
    def minimum_stay(self) -> int:
        return 3


# =============================================================================
# GUEST HIERARCHY - Different guest types with privileges
# =============================================================================

class Guest(ABC):
    """
    Abstract base class for all guest types.
    
    Demonstrates encapsulation with private attributes and
    abstract properties for guest-specific features.
    """
    
    def __init__(self, name: str, email: str, phone: str):
        self._guest_id = f"G-{uuid.uuid4().hex[:8].upper()}"
        self._name = name
        self._email = email
        self._phone = phone
        self._loyalty_points = 0
        self._booking_history: List[str] = []
        self._created_at = datetime.now()
    
    @property
    def guest_id(self) -> str:
        return self._guest_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def email(self) -> str:
        return self._email
    
    @email.setter
    def email(self, value: str) -> None:
        if '@' not in value:
            raise ValueError("Invalid email format")
        self._email = value
    
    @property
    def phone(self) -> str:
        return self._phone
    
    @property
    def loyalty_points(self) -> int:
        return self._loyalty_points
    
    @property
    def booking_history(self) -> List[str]:
        return self._booking_history.copy()
    
    @property
    @abstractmethod
    def guest_type(self) -> GuestType:
        """The type of guest."""
        pass
    
    @property
    @abstractmethod
    def discount_rate(self) -> Decimal:
        """Discount percentage for this guest type."""
        pass
    
    @property
    @abstractmethod
    def privileges(self) -> List[str]:
        """List of privileges for this guest type."""
        pass
    
    @abstractmethod
    def can_upgrade(self) -> bool:
        """Check if guest is eligible for automatic upgrades."""
        pass
    
    def earn_points(self, amount: Decimal) -> int:
        """Earn loyalty points based on spending (10 points per dollar)."""
        points = int(amount * 10)
        self._loyalty_points += points
        print(f"[{self._name}] Earned {points} loyalty points (Total: {self._loyalty_points})")
        return points
    
    def redeem_points(self, points: int) -> Decimal:
        """Redeem loyalty points for cash value (100 points = $1)."""
        if points > self._loyalty_points:
            raise HotelException(
                f"Insufficient points: {self._loyalty_points} available, {points} requested",
                "INSUFFICIENT_POINTS"
            )
        self._loyalty_points -= points
        value = Decimal(points) / Decimal("100")
        print(f"[{self._name}] Redeemed {points} points for ${value:.2f}")
        return value
    
    def add_booking(self, booking_id: str) -> None:
        """Add a booking to guest's history."""
        self._booking_history.append(booking_id)
    
    def __str__(self) -> str:
        return f"{self._name} ({self.guest_type.value.replace('_', ' ').title()})"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}('{self._guest_id}', '{self._name}')>"


class WalkInGuest(Guest):
    """Walk-in guest with no membership or special privileges."""
    
    @property
    def guest_type(self) -> GuestType:
        return GuestType.WALK_IN
    
    @property
    def discount_rate(self) -> Decimal:
        return Decimal("0.00")  # No discount
    
    @property
    def privileges(self) -> List[str]:
        return ["Standard check-in", "WiFi access"]
    
    def can_upgrade(self) -> bool:
        return False


class MemberGuest(Guest):
    """Member guest with loyalty benefits."""
    
    def __init__(self, name: str, email: str, phone: str,
                 membership_level: str = "Silver"):
        super().__init__(name, email, phone)
        self._membership_level = membership_level
        self._member_since = datetime.now()
    
    @property
    def membership_level(self) -> str:
        return self._membership_level
    
    @property
    def guest_type(self) -> GuestType:
        return GuestType.MEMBER
    
    @property
    def discount_rate(self) -> Decimal:
        levels = {"Silver": Decimal("0.05"), "Gold": Decimal("0.10"),
                  "Platinum": Decimal("0.15")}
        return levels.get(self._membership_level, Decimal("0.05"))
    
    @property
    def privileges(self) -> List[str]:
        base = ["Priority check-in", "WiFi access", "Loyalty points earning"]
        if self._membership_level == "Gold":
            base.extend(["Late checkout (2 PM)", "Welcome drink"])
        elif self._membership_level == "Platinum":
            base.extend(["Late checkout (4 PM)", "Welcome drink", 
                        "Free room upgrade", "Executive lounge access"])
        return base
    
    def can_upgrade(self) -> bool:
        return self._membership_level == "Platinum"


class VIPGuest(Guest):
    """VIP guest with premium privileges and automatic upgrades."""
    
    def __init__(self, name: str, email: str, phone: str,
                 vip_code: str):
        super().__init__(name, email, phone)
        self._vip_code = vip_code
        self._personal_preferences: Dict[str, str] = {}
    
    @property
    def vip_code(self) -> str:
        return self._vip_code
    
    @property
    def guest_type(self) -> GuestType:
        return GuestType.VIP
    
    @property
    def discount_rate(self) -> Decimal:
        return Decimal("0.20")  # 20% VIP discount
    
    @property
    def privileges(self) -> List[str]:
        return [
            "Immediate check-in",
            "Complimentary premium WiFi",
            "Double loyalty points",
            "Automatic room upgrade",
            "24/7 personal concierge",
            "Complimentary breakfast",
            "Late checkout (6 PM)",
            "Airport transfer",
            "Executive lounge access",
            "Spa credit ($100)"
        ]
    
    def can_upgrade(self) -> bool:
        return True
    
    def set_preference(self, key: str, value: str) -> None:
        """Set a personal preference for future stays."""
        self._personal_preferences[key] = value
    
    def get_preferences(self) -> Dict[str, str]:
        """Get all personal preferences."""
        return self._personal_preferences.copy()


class CorporateGuest(Guest):
    """Corporate guest with negotiated rates and billing."""
    
    def __init__(self, name: str, email: str, phone: str,
                 company_name: str, corporate_code: str):
        super().__init__(name, email, phone)
        self._company_name = company_name
        self._corporate_code = corporate_code
        self._negotiated_rate: Optional[Decimal] = None
    
    @property
    def company_name(self) -> str:
        return self._company_name
    
    @property
    def corporate_code(self) -> str:
        return self._corporate_code
    
    @property
    def guest_type(self) -> GuestType:
        return GuestType.CORPORATE
    
    @property
    def discount_rate(self) -> Decimal:
        return Decimal("0.25")  # 25% corporate discount
    
    @property
    def privileges(self) -> List[str]:
        return [
            "Express check-in/out",
            "Complimentary premium WiFi",
            "Corporate billing",
            "Meeting room access",
            "Late checkout (3 PM)",
            "Complimentary breakfast",
            "Loyalty points on company account"
        ]
    
    def can_upgrade(self) -> bool:
        return True
    
    def set_negotiated_rate(self, rate: Decimal) -> None:
        """Set a negotiated rate for this corporate account."""
        self._negotiated_rate = rate
    
    def get_negotiated_rate(self) -> Optional[Decimal]:
        """Get the negotiated rate if available."""
        return self._negotiated_rate


# =============================================================================
# BOOKING HIERARCHY - Different booking types
# =============================================================================

class Booking(Priceable, Serviceable):
    """
    Abstract base class for all booking types.
    
    Demonstrates multiple interface inheritance and
    encapsulation of booking details.
    
    Note: Priceable and Serviceable both inherit from ABC,
    so this class is automatically abstract.
    """
    
    def __init__(self, guest: Guest, room: Room,
                 check_in: datetime, check_out: datetime,
                 season: Season = Season.REGULAR,
                 num_guests: int = 1):
        # Validate dates
        if check_out <= check_in:
            raise InvalidDateRangeError(check_in, check_out)
        
        # Validate guest count
        if num_guests > room.capacity:
            raise GuestLimitExceededError(num_guests, room.capacity, room.room_number)
        
        # Protected booking details
        self._booking_id = f"BK-{uuid.uuid4().hex[:8].upper()}"
        self._guest = guest
        self._room = room
        self._check_in = check_in
        self._check_out = check_out
        self._season = season
        self._num_guests = num_guests
        self._status = BookingStatus.PENDING
        self._created_at = datetime.now()
        self._service_charges: List[Tuple[ServiceType, Decimal, str]] = []
        self._special_requests: List[str] = []
        self._discount_applied = Decimal("0.00")
    
    @property
    def booking_id(self) -> str:
        return self._booking_id
    
    @property
    def guest(self) -> Guest:
        return self._guest
    
    @property
    def room(self) -> Room:
        return self._room
    
    @property
    def check_in(self) -> datetime:
        return self._check_in
    
    @property
    def check_out(self) -> datetime:
        return self._check_out
    
    @property
    def status(self) -> BookingStatus:
        return self._status
    
    @status.setter
    def status(self, value: BookingStatus) -> None:
        old_status = self._status
        self._status = value
        print(f"[Booking {self._booking_id}] Status: {old_status.name} -> {value.name}")
    
    @property
    def nights(self) -> int:
        return (self._check_out - self._check_in).days
    
    @property
    @abstractmethod
    def booking_type(self) -> str:
        """The type of booking."""
        pass
    
    @abstractmethod
    def get_booking_details(self) -> Dict[str, Any]:
        """Get detailed booking information."""
        pass
    
    # Priceable interface implementation
    def calculate_total(self) -> Decimal:
        """Calculate total booking cost including taxes and services."""
        room_cost = self._room.calculate_stay_cost(
            self._check_in, self._check_out, self._season
        )
        services = self.get_service_charges()
        subtotal = room_cost + services - self._discount_applied
        taxes = self.get_taxes()
        return (subtotal + taxes).quantize(Decimal("0.01"), ROUND_HALF_UP)
    
    def apply_discount(self, discount_percent: Decimal) -> Decimal:
        """Apply a percentage discount to the booking."""
        room_cost = self._room.calculate_stay_cost(
            self._check_in, self._check_out, self._season
        )
        discount = (room_cost * discount_percent).quantize(Decimal("0.01"), ROUND_HALF_UP)
        self._discount_applied = discount
        print(f"[Booking {self._booking_id}] Discount applied: ${discount:.2f}")
        return discount
    
    def get_taxes(self) -> Decimal:
        """Calculate taxes on the booking."""
        room_cost = self._room.calculate_stay_cost(
            self._check_in, self._check_out, self._season
        )
        services = self.get_service_charges()
        taxable = room_cost + services - self._discount_applied
        return (taxable * Room.TAX_RATE).quantize(Decimal("0.01"), ROUND_HALF_UP)
    
    # Serviceable interface implementation
    def request_service(self, service_type: ServiceType, 
                       details: Dict[str, Any]) -> str:
        """Request a room service."""
        if self._status != BookingStatus.CHECKED_IN:
            raise ServiceUnavailableError(
                service_type,
                "Services only available when checked in"
            )
        
        service_id = f"SVC-{uuid.uuid4().hex[:8].upper()}"
        charge = service_type.base_charge
        
        # Handle variable charges (e.g., minibar)
        if service_type == ServiceType.MINIBAR:
            charge = Decimal(str(details.get('amount', 0)))
        
        self._service_charges.append((service_type, charge, service_id))
        
        # Record in registry
        registry = HotelRegistry()
        registry.record_service(service_id, {
            'booking_id': self._booking_id,
            'service_type': service_type.value,
            'charge': float(charge),
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        
        print(f"[Booking {self._booking_id}] Service requested: "
              f"{service_type.display_name} - ${charge:.2f}")
        return service_id
    
    def get_service_charges(self) -> Decimal:
        """Get total service charges."""
        return sum(charge for _, charge, _ in self._service_charges)
    
    def add_special_request(self, request: str) -> None:
        """Add a special request to the booking."""
        self._special_requests.append(request)
        print(f"[Booking {self._booking_id}] Special request added: {request}")
    
    def calculate_cancellation_refund(self) -> Tuple[Decimal, str]:
        """
        Calculate refund based on cancellation policy.
        
        - Full refund: 48+ hours before check-in
        - 50% refund: 24-48 hours before check-in
        - No refund: < 24 hours before check-in
        """
        hours_until_checkin = (self._check_in - datetime.now()).total_seconds() / 3600
        room_cost = self._room.calculate_stay_cost(
            self._check_in, self._check_out, self._season
        )
        
        if hours_until_checkin >= 48:
            return room_cost, "Full refund - cancelled 48+ hours in advance"
        elif hours_until_checkin >= 24:
            return (room_cost * Decimal("0.50")).quantize(Decimal("0.01")), \
                   "50% refund - cancelled 24-48 hours in advance"
        else:
            return Decimal("0.00"), "No refund - cancelled less than 24 hours in advance"
    
    def __str__(self) -> str:
        return (f"Booking {self._booking_id}: {self._guest.name} in "
                f"Room {self._room.room_number} ({self._check_in.date()} to "
                f"{self._check_out.date()})")


class StandardBooking(Booking):
    """Standard individual booking."""
    
    @property
    def booking_type(self) -> str:
        return "Standard"
    
    def get_booking_details(self) -> Dict[str, Any]:
        return {
            'booking_id': self._booking_id,
            'type': self.booking_type,
            'guest': self._guest.name,
            'guest_type': self._guest.guest_type.value,
            'room': self._room.room_number,
            'room_type': self._room.room_type.value,
            'check_in': self._check_in.isoformat(),
            'check_out': self._check_out.isoformat(),
            'nights': self.nights,
            'num_guests': self._num_guests,
            'status': self._status.value,
            'total': float(self.calculate_total())
        }


class PackageBooking(Booking):
    """Booking with included package (e.g., breakfast, spa)."""
    
    def __init__(self, guest: Guest, room: Room,
                 check_in: datetime, check_out: datetime,
                 package_name: str,
                 package_inclusions: List[str],
                 package_price: Decimal,
                 season: Season = Season.REGULAR,
                 num_guests: int = 1):
        super().__init__(guest, room, check_in, check_out, season, num_guests)
        self._package_name = package_name
        self._package_inclusions = package_inclusions
        self._package_price = package_price
    
    @property
    def package_name(self) -> str:
        return self._package_name
    
    @property
    def booking_type(self) -> str:
        return f"Package ({self._package_name})"
    
    def calculate_total(self) -> Decimal:
        """Calculate total including package price."""
        base_total = super().calculate_total()
        return (base_total + self._package_price).quantize(Decimal("0.01"), ROUND_HALF_UP)
    
    def get_booking_details(self) -> Dict[str, Any]:
        details = {
            'booking_id': self._booking_id,
            'type': self.booking_type,
            'guest': self._guest.name,
            'room': self._room.room_number,
            'check_in': self._check_in.isoformat(),
            'check_out': self._check_out.isoformat(),
            'package_name': self._package_name,
            'package_inclusions': self._package_inclusions,
            'package_price': float(self._package_price),
            'status': self._status.value,
            'total': float(self.calculate_total())
        }
        return details


class GroupBooking(Booking):
    """Group booking for multiple rooms."""
    
    GROUP_DISCOUNT = Decimal("0.15")  # 15% discount for groups
    
    def __init__(self, guest: Guest, rooms: List[Room],
                 check_in: datetime, check_out: datetime,
                 group_name: str,
                 season: Season = Season.REGULAR,
                 total_guests: int = 1):
        # Use first room for base booking
        if not rooms:
            raise BookingException("Group booking requires at least one room")
        
        super().__init__(guest, rooms[0], check_in, check_out, season, 
                        min(total_guests, rooms[0].capacity))
        self._rooms = rooms
        self._group_name = group_name
        self._total_guests = total_guests
    
    @property
    def rooms(self) -> List[Room]:
        return self._rooms
    
    @property
    def group_name(self) -> str:
        return self._group_name
    
    @property
    def booking_type(self) -> str:
        return f"Group ({self._group_name})"
    
    def calculate_total(self) -> Decimal:
        """Calculate total for all rooms with group discount if applicable."""
        total = Decimal("0.00")
        for room in self._rooms:
            room_cost = room.calculate_stay_cost(
                self._check_in, self._check_out, self._season
            )
            total += room_cost
        
        # Apply group discount if 5+ rooms
        if len(self._rooms) >= 5:
            discount = total * self.GROUP_DISCOUNT
            total -= discount
            print(f"[Group Booking] 15% group discount applied: -${discount:.2f}")
        
        total += self.get_service_charges()
        taxes = (total * Room.TAX_RATE).quantize(Decimal("0.01"), ROUND_HALF_UP)
        return (total + taxes).quantize(Decimal("0.01"), ROUND_HALF_UP)
    
    def get_booking_details(self) -> Dict[str, Any]:
        return {
            'booking_id': self._booking_id,
            'type': self.booking_type,
            'group_name': self._group_name,
            'organizer': self._guest.name,
            'rooms': [r.room_number for r in self._rooms],
            'num_rooms': len(self._rooms),
            'check_in': self._check_in.isoformat(),
            'check_out': self._check_out.isoformat(),
            'total_guests': self._total_guests,
            'status': self._status.value,
            'total': float(self.calculate_total())
        }


class EventBooking(Booking):
    """Booking for events (conferences, weddings, etc.)."""
    
    def __init__(self, guest: Guest, room: Room,
                 check_in: datetime, check_out: datetime,
                 event_name: str,
                 event_type: str,
                 expected_attendees: int,
                 catering_required: bool = True,
                 av_equipment_required: bool = True,
                 season: Season = Season.REGULAR):
        # For events, we don't apply room capacity limits the same way
        # Events use rooms differently (e.g., conference rooms, ballrooms)
        # Pass 1 as num_guests to bypass the capacity check
        super().__init__(guest, room, check_in, check_out, season, 1)
        self._event_name = event_name
        self._event_type = event_type
        self._expected_attendees = expected_attendees
        self._catering_required = catering_required
        self._av_equipment_required = av_equipment_required
    
    @property
    def event_name(self) -> str:
        return self._event_name
    
    @property
    def booking_type(self) -> str:
        return f"Event ({self._event_type})"
    
    def calculate_total(self) -> Decimal:
        """Calculate total including event services."""
        base_total = super().calculate_total()
        
        # Add catering costs ($50 per person)
        if self._catering_required:
            catering = Decimal("50.00") * self._expected_attendees
            base_total += catering
        
        # Add AV equipment rental
        if self._av_equipment_required:
            av_cost = Decimal("500.00")  # Flat fee
            base_total += av_cost
        
        return base_total.quantize(Decimal("0.01"), ROUND_HALF_UP)
    
    def get_booking_details(self) -> Dict[str, Any]:
        return {
            'booking_id': self._booking_id,
            'type': self.booking_type,
            'event_name': self._event_name,
            'event_type': self._event_type,
            'organizer': self._guest.name,
            'room': self._room.room_number,
            'date': self._check_in.date().isoformat(),
            'expected_attendees': self._expected_attendees,
            'catering': self._catering_required,
            'av_equipment': self._av_equipment_required,
            'status': self._status.value,
            'total': float(self.calculate_total())
        }


# =============================================================================
# FACTORY PATTERN - Create objects without specifying exact class
# =============================================================================

class RoomFactory:
    """
    Factory for creating room objects.
    
    Demonstrates the Factory Pattern - creates objects without
    exposing the instantiation logic to the client.
    """
    
    @staticmethod
    def create_room(room_type: str, room_number: str, floor: int,
                    view: str = "Standard") -> Room:
        """
        Create a room of the specified type.
        
        Args:
            room_type: Type of room (standard, deluxe, suite, penthouse)
            room_number: Unique room number
            floor: Floor number
            view: View type (Standard, City, Ocean, Garden, etc.)
        
        Returns:
            Room instance of the appropriate type
        
        Raises:
            InvalidRoomTypeError: If room_type is not recognized
        """
        room_type_lower = room_type.lower()
        
        room_classes = {
            'standard': StandardRoom,
            'deluxe': DeluxeRoom,
            'suite': Suite,
            'penthouse': PenthouseSuite,
        }
        
        if room_type_lower not in room_classes:
            raise InvalidRoomTypeError(room_type)
        
        room_class = room_classes[room_type_lower]
        room = room_class(room_number, floor, view)
        print(f"[RoomFactory] Created {room}")
        return room
    
    @staticmethod
    def create_room_from_enum(room_type: RoomType, room_number: str,
                              floor: int, view: str = "Standard") -> Room:
        """Create a room using RoomType enum."""
        return RoomFactory.create_room(room_type.value, room_number, floor, view)


class BookingFactory:
    """
    Factory for creating booking objects.
    
    Demonstrates the Factory Pattern for the booking hierarchy.
    """
    
    @staticmethod
    def create_standard_booking(guest: Guest, room: Room,
                                check_in: datetime, check_out: datetime,
                                season: Season = Season.REGULAR,
                                num_guests: int = 1) -> StandardBooking:
        """Create a standard booking."""
        booking = StandardBooking(guest, room, check_in, check_out, 
                                  season, num_guests)
        # Apply guest discount if applicable
        if guest.discount_rate > 0:
            booking.apply_discount(guest.discount_rate)
        print(f"[BookingFactory] Created {booking.booking_type} booking: {booking.booking_id}")
        return booking
    
    @staticmethod
    def create_package_booking(guest: Guest, room: Room,
                               check_in: datetime, check_out: datetime,
                               package_name: str,
                               package_inclusions: List[str],
                               package_price: Decimal,
                               season: Season = Season.REGULAR,
                               num_guests: int = 1) -> PackageBooking:
        """Create a package booking."""
        booking = PackageBooking(guest, room, check_in, check_out,
                                 package_name, package_inclusions,
                                 package_price, season, num_guests)
        if guest.discount_rate > 0:
            booking.apply_discount(guest.discount_rate)
        print(f"[BookingFactory] Created Package booking: {booking.booking_id}")
        return booking
    
    @staticmethod
    def create_group_booking(guest: Guest, rooms: List[Room],
                             check_in: datetime, check_out: datetime,
                             group_name: str,
                             season: Season = Season.REGULAR,
                             total_guests: int = 1) -> GroupBooking:
        """Create a group booking."""
        booking = GroupBooking(guest, rooms, check_in, check_out,
                               group_name, season, total_guests)
        print(f"[BookingFactory] Created Group booking: {booking.booking_id}")
        return booking
    
    @staticmethod
    def create_event_booking(guest: Guest, room: Room,
                             check_in: datetime, check_out: datetime,
                             event_name: str, event_type: str,
                             expected_attendees: int,
                             catering: bool = True,
                             av_equipment: bool = True,
                             season: Season = Season.REGULAR) -> EventBooking:
        """Create an event booking."""
        booking = EventBooking(guest, room, check_in, check_out,
                               event_name, event_type, expected_attendees,
                               catering, av_equipment, season)
        print(f"[BookingFactory] Created Event booking: {booking.booking_id}")
        return booking


# =============================================================================
# ADAPTER PATTERN - Adapt legacy system to new interface
# =============================================================================

@dataclass
class LegacyReservation:
    """
    Legacy reservation data format from old booking system.
    
    This represents how the old system stored reservations.
    """
    booking_code: str          # e.g., "STD-101-20240115-20240118-SMITH"
    guest_name: str
    guest_email: str
    guest_phone: str
    date_range: str            # e.g., "15/01/2024-18/01/2024" (DD/MM/YYYY)
    room_code: str             # e.g., "STD-101", "DLX-201", "STE-301", "PH-401"
    guest_count: int
    rate_code: str             # e.g., "PEAK", "REG", "LOW"
    payment_status: str        # e.g., "PAID", "PENDING", "PARTIAL"
    special_notes: str = ""


class LegacyReservationAdapter:
    """
    Adapter to convert legacy reservations to the new booking system.
    
    Demonstrates the Adapter Pattern - converts the interface of
    the legacy system to work with the new booking system.
    """
    
    # Mapping of legacy room codes to new room types
    ROOM_CODE_MAP = {
        'STD': RoomType.STANDARD,
        'DLX': RoomType.DELUXE,
        'STE': RoomType.SUITE,
        'PH': RoomType.PENTHOUSE,
    }
    
    # Mapping of legacy rate codes to seasons
    RATE_CODE_MAP = {
        'PEAK': Season.PEAK,
        'REG': Season.REGULAR,
        'LOW': Season.OFF_PEAK,
    }
    
    def __init__(self, legacy_reservation: LegacyReservation):
        self._legacy = legacy_reservation
        print(f"[Adapter] Processing legacy reservation: {legacy_reservation.booking_code}")
    
    def parse_room_code(self) -> Tuple[RoomType, str]:
        """Parse legacy room code to extract type and number."""
        parts = self._legacy.room_code.split('-')
        if len(parts) != 2:
            raise InvalidRoomTypeError(self._legacy.room_code)
        
        type_code, number = parts
        if type_code not in self.ROOM_CODE_MAP:
            raise InvalidRoomTypeError(type_code)
        
        return self.ROOM_CODE_MAP[type_code], number
    
    def parse_date_range(self) -> Tuple[datetime, datetime]:
        """Parse legacy date format (DD/MM/YYYY-DD/MM/YYYY)."""
        try:
            start_str, end_str = self._legacy.date_range.split('-')
            check_in = datetime.strptime(start_str, "%d/%m/%Y")
            check_out = datetime.strptime(end_str, "%d/%m/%Y")
            return check_in, check_out
        except ValueError as e:
            raise InvalidDateRangeError(datetime.now(), datetime.now())
    
    def parse_season(self) -> Season:
        """Parse legacy rate code to season."""
        return self.RATE_CODE_MAP.get(self._legacy.rate_code, Season.REGULAR)
    
    def create_guest(self) -> WalkInGuest:
        """Create a guest from legacy data."""
        return WalkInGuest(
            name=self._legacy.guest_name,
            email=self._legacy.guest_email,
            phone=self._legacy.guest_phone
        )
    
    def adapt_to_booking(self, registry: HotelRegistry) -> StandardBooking:
        """
        Convert legacy reservation to a new system booking.
        
        Args:
            registry: The hotel registry to find/create rooms
        
        Returns:
            StandardBooking created from legacy data
        """
        # Parse all legacy data
        room_type, room_number = self.parse_room_code()
        check_in, check_out = self.parse_date_range()
        season = self.parse_season()
        
        # Create or find guest
        guest = self.create_guest()
        registry.register_guest(guest)
        
        # Find or create room
        try:
            room = registry.get_room(room_number)
        except RoomNotFoundError:
            # Create the room if it doesn't exist
            floor = int(room_number[0]) if room_number[0].isdigit() else 1
            room = RoomFactory.create_room(room_type.value, room_number, floor)
            registry.register_room(room)
        
        # Create booking using factory
        booking = BookingFactory.create_standard_booking(
            guest=guest,
            room=room,
            check_in=check_in,
            check_out=check_out,
            season=season,
            num_guests=self._legacy.guest_count
        )
        
        # Add special notes as request
        if self._legacy.special_notes:
            booking.add_special_request(self._legacy.special_notes)
        
        # Set status based on payment status
        if self._legacy.payment_status == "PAID":
            booking.status = BookingStatus.CONFIRMED
        
        print(f"[Adapter] Successfully converted legacy booking to: {booking.booking_id}")
        return booking


# =============================================================================
# HOTEL MANAGEMENT - Main system operations
# =============================================================================

class HotelManager:
    """
    Main hotel management class coordinating all operations.
    
    Demonstrates facade pattern - provides a simplified interface
    to the complex subsystems.
    """
    
    def __init__(self):
        self._registry = HotelRegistry()
        self._notification_system = BookingNotificationSystem()
        self._setup_observers()
    
    def _setup_observers(self) -> None:
        """Set up the notification observers."""
        self._guest_notifier = GuestNotifier()
        self._housekeeping = HousekeepingNotifier()
        self._front_desk = FrontDeskNotifier()
        self._billing = BillingNotifier()
        
        self._notification_system.add_observer(self._guest_notifier)
        self._notification_system.add_observer(self._housekeeping)
        self._notification_system.add_observer(self._front_desk)
        self._notification_system.add_observer(self._billing)
    
    @property
    def registry(self) -> HotelRegistry:
        return self._registry
    
    @property
    def notification_system(self) -> BookingNotificationSystem:
        return self._notification_system
    
    def check_in(self, booking: Booking) -> None:
        """Process guest check-in."""
        if booking.status != BookingStatus.CONFIRMED:
            raise BookingException(
                f"Cannot check in - booking status is {booking.status.name}",
                booking.booking_id
            )
        
        booking.status = BookingStatus.CHECKED_IN
        booking.room.status = RoomStatus.OCCUPIED
        booking.room.current_booking_id = booking.booking_id
        
        # Notify all observers
        self._notification_system.notify_observers(
            NotificationType.CHECK_IN,
            {
                'booking_id': booking.booking_id,
                'guest_name': booking.guest.name,
                'guest_type': booking.guest.guest_type.value,
                'room_number': booking.room.room_number
            }
        )
    
    def check_out(self, booking: Booking) -> Decimal:
        """Process guest check-out and return final bill."""
        if booking.status != BookingStatus.CHECKED_IN:
            raise BookingException(
                f"Cannot check out - booking status is {booking.status.name}",
                booking.booking_id
            )
        
        # Calculate final total
        total = booking.calculate_total()
        
        # Award loyalty points
        booking.guest.earn_points(total)
        
        # Update statuses
        booking.status = BookingStatus.CHECKED_OUT
        booking.room.status = RoomStatus.CLEANING
        booking.room.current_booking_id = None
        
        # Notify all observers
        self._notification_system.notify_observers(
            NotificationType.CHECK_OUT,
            {
                'booking_id': booking.booking_id,
                'guest_name': booking.guest.name,
                'room_number': booking.room.room_number,
                'total': total
            }
        )
        
        return total
    
    def cancel_booking(self, booking: Booking) -> Tuple[Decimal, str]:
        """Cancel a booking and calculate refund."""
        if booking.status in (BookingStatus.CHECKED_IN, BookingStatus.CHECKED_OUT):
            raise CancellationNotAllowedError(
                booking.booking_id,
                f"Cannot cancel - guest has already {booking.status.name.lower().replace('_', ' ')}"
            )
        
        refund, message = booking.calculate_cancellation_refund()
        booking.status = BookingStatus.CANCELLED
        booking.room.cancel(booking.room._reservations[-1][2] if booking.room._reservations else "")
        
        # Notify observers
        self._notification_system.notify_observers(
            NotificationType.BOOKING_CANCELLED,
            {
                'booking_id': booking.booking_id,
                'guest_name': booking.guest.name,
                'room_number': booking.room.room_number,
                'refund': refund,
                'message': message
            }
        )
        
        return refund, message
    
    def confirm_booking(self, booking: Booking) -> None:
        """Confirm a pending booking."""
        if booking.status != BookingStatus.PENDING:
            raise BookingException(
                f"Cannot confirm - booking status is {booking.status.name}",
                booking.booking_id
            )
        
        booking.status = BookingStatus.CONFIRMED
        booking.guest.add_booking(booking.booking_id)
        
        # Notify observers
        self._notification_system.notify_observers(
            NotificationType.BOOKING_CONFIRMED,
            {
                'booking_id': booking.booking_id,
                'guest_name': booking.guest.name,
                'room_number': booking.room.room_number,
                'check_in': booking.check_in.date().isoformat(),
                'check_out': booking.check_out.date().isoformat()
            }
        )
    
    def request_room_service(self, booking: Booking, 
                             service_type: ServiceType,
                             details: Dict[str, Any] = None) -> str:
        """Request a room service for a booking."""
        if details is None:
            details = {}
        
        service_id = booking.request_service(service_type, details)
        
        # Notify observers
        self._notification_system.notify_observers(
            NotificationType.ROOM_SERVICE_REQUEST,
            {
                'booking_id': booking.booking_id,
                'guest_name': booking.guest.name,
                'room_number': booking.room.room_number,
                'service': service_type.display_name,
                'charge': service_type.base_charge
            }
        )
        
        return service_id
    
    def get_available_upgrade(self, current_room: Room) -> Optional[Room]:
        """Find an available upgrade room."""
        type_order = [RoomType.STANDARD, RoomType.DELUXE, 
                      RoomType.SUITE, RoomType.PENTHOUSE]
        
        try:
            current_idx = type_order.index(current_room.room_type)
        except ValueError:
            return None
        
        # Look for available room of higher type
        for higher_type in type_order[current_idx + 1:]:
            available = self._registry.get_available_rooms(
                datetime.now(), datetime.now() + timedelta(days=1),
                higher_type
            )
            if available:
                return available[0]
        
        return None


# =============================================================================
# MAIN DEMONSTRATION
# =============================================================================

def print_section(title: str) -> None:
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70 + "\n")


def main():
    """
    Main demonstration function showing all OOP concepts.
    
    This function creates a complete demonstration of:
    1. Singleton pattern (HotelRegistry)
    2. Factory pattern (RoomFactory, BookingFactory)
    3. Observer pattern (notification system)
    4. Adapter pattern (legacy reservation conversion)
    5. Class hierarchies (Room, Guest, Booking)
    6. Interfaces (Bookable, Priceable, Serviceable, Observable)
    7. Encapsulation (private attributes, properties)
    8. Custom exceptions
    9. Business rules (seasonal pricing, discounts, loyalty points)
    """
    
    print("\n" + "=" * 70)
    print(" HOTEL BOOKING SYSTEM - OOP DEMONSTRATION")
    print(" A Complete Reference Implementation")
    print("=" * 70)
    
    # =========================================================================
    # 1. SINGLETON PATTERN - Hotel Registry
    # =========================================================================
    print_section("1. SINGLETON PATTERN - Hotel Registry")
    
    # Get the registry (creates it)
    registry1 = HotelRegistry()
    print(f"Registry 1 ID: {id(registry1)}")
    
    # Get it again (same instance)
    registry2 = HotelRegistry()
    print(f"Registry 2 ID: {id(registry2)}")
    
    print(f"Same instance? {registry1 is registry2}")
    print(f"Hotel Name: {registry1.hotel_name}")
    
    # =========================================================================
    # 2. FACTORY PATTERN - Creating Rooms
    # =========================================================================
    print_section("2. FACTORY PATTERN - Creating Rooms")
    
    # Create rooms using the factory
    rooms = [
        RoomFactory.create_room("standard", "101", 1, "Garden"),
        RoomFactory.create_room("standard", "102", 1, "Pool"),
        RoomFactory.create_room("deluxe", "201", 2, "City"),
        RoomFactory.create_room("deluxe", "202", 2, "City"),
        RoomFactory.create_room("suite", "301", 3, "Ocean"),
        RoomFactory.create_room("suite", "302", 3, "Mountain"),
        RoomFactory.create_room("penthouse", "401", 4, "Panoramic"),
    ]
    
    # Register all rooms
    for room in rooms:
        registry1.register_room(room)
    
    # Display room details
    print("\n--- Room Inventory ---")
    for room in rooms:
        print(f"  {room} | Capacity: {room.capacity} | "
              f"Base Rate: ${room.base_rate} | Min Stay: {room.minimum_stay} nights")
        print(f"    Amenities: {', '.join(room.amenities[:3])}...")
    
    # =========================================================================
    # 3. CLASS HIERARCHY - Creating Guests
    # =========================================================================
    print_section("3. CLASS HIERARCHY - Creating Different Guest Types")
    
    # Create different types of guests
    walk_in = WalkInGuest("John Smith", "john@email.com", "555-0101")
    member = MemberGuest("Sarah Johnson", "sarah@email.com", "555-0102", "Gold")
    vip = VIPGuest("Robert Wilson", "robert@email.com", "555-0103", "VIP-001")
    corporate = CorporateGuest("Emily Chen", "emily@corp.com", "555-0104", 
                               "TechCorp Inc.", "CORP-2024")
    
    guests = [walk_in, member, vip, corporate]
    
    # Register all guests
    for guest in guests:
        registry1.register_guest(guest)
    
    print("\n--- Guest Information ---")
    for guest in guests:
        print(f"\n  {guest.name} ({guest.guest_type.value.replace('_', ' ').title()})")
        print(f"    ID: {guest.guest_id}")
        print(f"    Discount Rate: {guest.discount_rate * 100:.0f}%")
        print(f"    Can Upgrade: {guest.can_upgrade()}")
        print(f"    Privileges: {', '.join(guest.privileges[:3])}...")
    
    # =========================================================================
    # 4. OBSERVER PATTERN - Notification System
    # =========================================================================
    print_section("4. OBSERVER PATTERN - Setting Up Notifications")
    
    # Create hotel manager (sets up observers)
    manager = HotelManager()
    print("Notification system initialized with 4 observers:")
    print("  - GuestNotifier (sends guest communications)")
    print("  - HousekeepingNotifier (manages room cleaning)")
    print("  - FrontDeskNotifier (alerts front desk staff)")
    print("  - BillingNotifier (handles billing updates)")
    
    # =========================================================================
    # 5. BOOKING WITH FACTORY PATTERN
    # =========================================================================
    print_section("5. BOOKING CREATION - Using Factory Pattern")
    
    # Set dates for bookings
    check_in = datetime.now() + timedelta(days=7)
    check_out = datetime.now() + timedelta(days=10)
    
    # Create a standard booking
    print("\n--- Creating Standard Booking ---")
    standard_booking = BookingFactory.create_standard_booking(
        guest=walk_in,
        room=rooms[0],  # Standard room 101
        check_in=check_in,
        check_out=check_out,
        season=Season.REGULAR,
        num_guests=2
    )
    registry1.register_booking(standard_booking)
    
    # Create a package booking
    print("\n--- Creating Package Booking ---")
    package_booking = BookingFactory.create_package_booking(
        guest=member,
        room=rooms[2],  # Deluxe room 201
        check_in=check_in,
        check_out=check_out,
        package_name="Romance Package",
        package_inclusions=["Champagne", "Rose petals", "Couples spa", "Dinner for 2"],
        package_price=Decimal("299.00"),
        season=Season.REGULAR,
        num_guests=2
    )
    registry1.register_booking(package_booking)
    
    # Create a group booking
    print("\n--- Creating Group Booking ---")
    group_rooms = rooms[0:5]  # 5 rooms for group discount
    group_booking = BookingFactory.create_group_booking(
        guest=corporate,
        rooms=group_rooms,
        check_in=check_in + timedelta(days=14),
        check_out=check_in + timedelta(days=17),
        group_name="TechCorp Annual Retreat",
        season=Season.OFF_PEAK,
        total_guests=12
    )
    registry1.register_booking(group_booking)
    
    # Create an event booking
    print("\n--- Creating Event Booking ---")
    event_booking = BookingFactory.create_event_booking(
        guest=vip,
        room=rooms[6],  # Penthouse
        check_in=check_in + timedelta(days=30),
        check_out=check_in + timedelta(days=31),
        event_name="Annual Gala Dinner",
        event_type="Corporate Event",
        expected_attendees=50,
        catering=True,
        av_equipment=True,
        season=Season.PEAK
    )
    registry1.register_booking(event_booking)
    
    # =========================================================================
    # 6. SEASONAL PRICING DEMONSTRATION
    # =========================================================================
    print_section("6. SEASONAL PRICING - Rate Variations")
    
    sample_room = rooms[2]  # Deluxe room
    print(f"Room: {sample_room}")
    print(f"Base Rate: ${sample_room.base_rate}")
    print("\nSeasonal Rates:")
    for season in Season:
        rate = sample_room.calculate_rate(season)
        multiplier = registry1.get_seasonal_multiplier(season)
        print(f"  {season.value.title():10} : ${rate:7.2f} (x{multiplier})")
    
    # =========================================================================
    # 7. BOOKING WORKFLOW WITH OBSERVER NOTIFICATIONS
    # =========================================================================
    print_section("7. BOOKING WORKFLOW - Observer Notifications in Action")
    
    # Confirm a booking (triggers notifications)
    print("--- Confirming Booking ---")
    manager.confirm_booking(standard_booking)
    
    # Check in (triggers notifications)
    print("\n--- Check-In Process ---")
    manager.check_in(standard_booking)
    
    # =========================================================================
    # 8. SERVICES AND CHARGES
    # =========================================================================
    print_section("8. SERVICES - Requesting Room Services")
    
    # Request various services
    print("Requesting services for checked-in booking...\n")
    
    manager.request_room_service(
        standard_booking, 
        ServiceType.ROOM_SERVICE,
        {'items': ['Club Sandwich', 'Coffee']}
    )
    
    manager.request_room_service(
        standard_booking,
        ServiceType.LAUNDRY,
        {'items': ['2 shirts', '1 suit']}
    )
    
    manager.request_room_service(
        standard_booking,
        ServiceType.MINIBAR,
        {'amount': 45.00}  # Variable charge
    )
    
    print(f"\nTotal Service Charges: ${standard_booking.get_service_charges():.2f}")
    
    # =========================================================================
    # 9. BILLING AND CHECKOUT
    # =========================================================================
    print_section("9. BILLING - Checkout and Final Bill")
    
    # Get booking details before checkout
    details = standard_booking.get_booking_details()
    print("Booking Summary:")
    print(f"  Booking ID: {details['booking_id']}")
    print(f"  Guest: {details['guest']} ({details['guest_type']})")
    print(f"  Room: {details['room']} ({details['room_type']})")
    print(f"  Nights: {details['nights']}")
    
    # Calculate breakdown
    room_cost = standard_booking.room.calculate_stay_cost(
        standard_booking.check_in, 
        standard_booking.check_out,
        Season.REGULAR
    )
    services = standard_booking.get_service_charges()
    taxes = standard_booking.get_taxes()
    total = standard_booking.calculate_total()
    
    print(f"\n  Room Cost: ${room_cost:.2f}")
    print(f"  Services:  ${services:.2f}")
    print(f"  Taxes:     ${taxes:.2f}")
    print(f"  ---------------------")
    print(f"  TOTAL:     ${total:.2f}")
    
    # Process checkout
    print("\n--- Processing Checkout ---")
    final_total = manager.check_out(standard_booking)
    print(f"\nFinal bill processed: ${final_total:.2f}")
    
    # =========================================================================
    # 10. LOYALTY POINTS DEMONSTRATION
    # =========================================================================
    print_section("10. LOYALTY POINTS - Earning and Redemption")
    
    print(f"Guest: {walk_in.name}")
    print(f"Points after checkout: {walk_in.loyalty_points}")
    
    # Redeem some points
    if walk_in.loyalty_points >= 1000:
        value = walk_in.redeem_points(1000)
        print(f"Redeemed 1000 points for ${value:.2f} credit")
        print(f"Remaining points: {walk_in.loyalty_points}")
    
    # VIP guest earns double points
    print(f"\n{vip.name} (VIP) - Earns DOUBLE loyalty points")
    
    # =========================================================================
    # 11. ADAPTER PATTERN - Legacy Reservation
    # =========================================================================
    print_section("11. ADAPTER PATTERN - Converting Legacy Reservations")
    
    # Create a legacy reservation (simulating old system data)
    legacy_res = LegacyReservation(
        booking_code="STD-103-20240215-20240218-JONES",
        guest_name="Michael Jones",
        guest_email="mjones@oldmail.com",
        guest_phone="555-9999",
        date_range="15/02/2024-18/02/2024",
        room_code="DLX-203",
        guest_count=2,
        rate_code="REG",
        payment_status="PAID",
        special_notes="Late arrival expected, hold room"
    )
    
    print("Legacy Reservation Data:")
    print(f"  Booking Code: {legacy_res.booking_code}")
    print(f"  Room Code: {legacy_res.room_code}")
    print(f"  Date Range: {legacy_res.date_range}")
    print(f"  Rate Code: {legacy_res.rate_code}")
    
    # Use adapter to convert
    print("\nConverting with LegacyReservationAdapter...")
    adapter = LegacyReservationAdapter(legacy_res)
    converted_booking = adapter.adapt_to_booking(registry1)
    
    print("\nConverted Booking:")
    print(f"  New Booking ID: {converted_booking.booking_id}")
    print(f"  Room Type: {converted_booking.room.room_type.value}")
    print(f"  Status: {converted_booking.status.name}")
    
    # =========================================================================
    # 12. EXCEPTION HANDLING
    # =========================================================================
    print_section("12. EXCEPTION HANDLING - Custom Exceptions")
    
    # Test various exceptions
    print("Testing exception scenarios:\n")
    
    # Room not found
    try:
        registry1.get_room("999")
    except RoomNotFoundError as e:
        print(f"✓ Caught: {e}")
    
    # Invalid room type
    try:
        RoomFactory.create_room("mansion", "501", 5)
    except InvalidRoomTypeError as e:
        print(f"✓ Caught: {e}")
    
    # Guest limit exceeded
    try:
        BookingFactory.create_standard_booking(
            guest=walk_in,
            room=rooms[0],  # Standard room, capacity 2
            check_in=check_in + timedelta(days=30),
            check_out=check_in + timedelta(days=32),
            num_guests=5  # Too many!
        )
    except GuestLimitExceededError as e:
        print(f"✓ Caught: {e}")
    
    # Invalid date range
    try:
        BookingFactory.create_standard_booking(
            guest=walk_in,
            room=rooms[1],
            check_in=check_in + timedelta(days=5),
            check_out=check_in + timedelta(days=3),  # Before check-in!
        )
    except InvalidDateRangeError as e:
        print(f"✓ Caught: {e}")
    
    # Service unavailable (not checked in)
    try:
        package_booking.request_service(ServiceType.SPA, {})
    except ServiceUnavailableError as e:
        print(f"✓ Caught: {e}")
    
    # =========================================================================
    # 13. CANCELLATION POLICY
    # =========================================================================
    print_section("13. CANCELLATION POLICY - Refund Calculation")
    
    # Create a booking to cancel
    cancel_booking = BookingFactory.create_standard_booking(
        guest=member,
        room=rooms[1],
        check_in=datetime.now() + timedelta(hours=72),  # 3 days from now
        check_out=datetime.now() + timedelta(days=5),
        season=Season.REGULAR
    )
    registry1.register_booking(cancel_booking)
    manager.confirm_booking(cancel_booking)
    
    # Calculate potential refund
    refund, message = cancel_booking.calculate_cancellation_refund()
    print(f"Booking: {cancel_booking.booking_id}")
    print(f"Check-in: {cancel_booking.check_in.date()}")
    print(f"Potential refund: ${refund:.2f}")
    print(f"Policy: {message}")
    
    # Process cancellation
    print("\n--- Processing Cancellation ---")
    actual_refund, final_message = manager.cancel_booking(cancel_booking)
    print(f"Refund processed: ${actual_refund:.2f}")
    
    # =========================================================================
    # 14. VIP UPGRADE CHECK
    # =========================================================================
    print_section("14. VIP PRIVILEGES - Automatic Upgrade Check")
    
    print(f"Guest: {vip.name}")
    print(f"VIP Code: {vip.vip_code}")
    print(f"Can Upgrade: {vip.can_upgrade()}")
    
    # Check for available upgrade from a standard room
    sample_standard = rooms[0]
    upgrade_room = manager.get_available_upgrade(sample_standard)
    
    if upgrade_room:
        print(f"\nUpgrade available from {sample_standard.room_type.value} "
              f"to {upgrade_room.room_type.value}!")
        print(f"  Current: Room {sample_standard.room_number} "
              f"(${sample_standard.base_rate}/night)")
        print(f"  Upgrade: Room {upgrade_room.room_number} "
              f"(${upgrade_room.base_rate}/night)")
    
    # =========================================================================
    # 15. FINAL SUMMARY
    # =========================================================================
    print_section("15. SYSTEM SUMMARY")
    
    all_rooms = registry1.get_all_rooms()
    all_guests = registry1.get_all_guests()
    all_bookings = registry1.get_all_bookings()
    
    print(f"Total Rooms: {len(all_rooms)}")
    for room_type in RoomType:
        count = sum(1 for r in all_rooms if r.room_type == room_type)
        print(f"  - {room_type.value.title()}: {count}")
    
    print(f"\nTotal Guests: {len(all_guests)}")
    for guest_type in GuestType:
        count = sum(1 for g in all_guests if g.guest_type == guest_type)
        print(f"  - {guest_type.value.replace('_', ' ').title()}: {count}")
    
    print(f"\nTotal Bookings: {len(all_bookings)}")
    status_counts = {}
    for booking in all_bookings:
        status = booking.status.name
        status_counts[status] = status_counts.get(status, 0) + 1
    for status, count in status_counts.items():
        print(f"  - {status}: {count}")
    
    print("\n" + "=" * 70)
    print(" OOP CONCEPTS DEMONSTRATED:")
    print("=" * 70)
    print("""
    ✓ Abstract Base Classes (ABC) - Room, Guest, Booking hierarchies
    ✓ Interfaces - Bookable, Priceable, Serviceable, Observable
    ✓ Encapsulation - Private attributes, properties with validation
    ✓ Inheritance - Multi-level class hierarchies
    ✓ Polymorphism - Different room/guest/booking types, same interface
    ✓ Factory Pattern - RoomFactory, BookingFactory
    ✓ Singleton Pattern - HotelRegistry with metaclass
    ✓ Observer Pattern - BookingNotificationSystem with multiple observers
    ✓ Adapter Pattern - LegacyReservationAdapter
    ✓ Custom Exceptions - Hierarchical exception classes
    ✓ Enums - Type-safe constants throughout
    ✓ Business Rules - Seasonal pricing, discounts, loyalty points
    """)
    print("=" * 70)
    print(" Hotel Booking System demonstration complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
