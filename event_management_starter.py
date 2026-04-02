"""
NIT2112 Practical Test: EventPro Conference Management System
============================================================
Student Name: [Your Name]
Student ID: [Your ID]
Date: [Date]

AI Copilot Used: [Yes/No - Name of tool e.g., GitHub Copilot, ChatGPT]

INSTRUCTIONS:
- Complete all TODO sections
- Demonstrate all required OOP concepts
- Document your AI interactions as you work
- Test your code before submission
============================================================
"""

from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict


# ============================================================
# CUSTOM EXCEPTIONS
# ============================================================
class EventManagementError(Exception):
    """Base exception for event management system errors."""
    pass


class RegistrationError(EventManagementError):
    """Base exception for registration-related errors."""
    pass


class EventFullError(RegistrationError):
    """Raised when attempting to register for a full event."""
    pass


class DuplicateRegistrationError(RegistrationError):
    """Raised when same email tries to register twice for same event."""
    pass


class InvalidTicketError(RegistrationError):
    """Raised when ticket validation fails."""
    pass


class SchedulingError(EventManagementError):
    """Base exception for scheduling-related errors."""
    pass


class RoomConflictError(SchedulingError):
    """Raised when a room is double-booked."""
    pass


class SpeakerConflictError(SchedulingError):
    """Raised when a speaker has overlapping sessions."""
    pass


class EventError(EventManagementError):
    """Base exception for event-related errors."""
    pass


class InvalidEventConfigError(EventError):
    """Raised when event configuration is invalid."""
    pass


# ============================================================
# INTERFACES / ABSTRACT BASE CLASSES
# ============================================================
class Registrable(ABC):
    """Interface for entities that support registration."""
    
    @abstractmethod
    def register_attendee(self, attendee: 'Attendee') -> bool:
        """Register an attendee. Returns True if successful."""
        pass
    
    @abstractmethod
    def get_available_spots(self) -> int:
        """Return number of available registration spots."""
        pass


class Schedulable(ABC):
    """Interface for entities that can be scheduled."""
    
    @abstractmethod
    def get_time_slot(self) -> tuple:
        """Return (start_time, end_time) tuple."""
        pass
    
    @abstractmethod
    def conflicts_with(self, other: 'Schedulable') -> bool:
        """Check if this schedule conflicts with another."""
        pass


# ============================================================
# OBSERVER PATTERN - Waitlist Notifications
# ============================================================
class WaitlistObserver(ABC):
    """Abstract observer for waitlist notifications."""
    
    @abstractmethod
    def notify(self, event_name: str, message: str) -> None:
        """Called when a spot becomes available."""
        pass


class WaitlistManager:
    """
    Manages the waitlist queue and notifications.
    Implements FIFO processing.
    """
    
    def __init__(self):
        """Initialise waitlist storage keyed by event ID."""
        self._waitlists: Dict[str, List['Attendee']] = {}
    
    def add_to_waitlist(self, attendee: 'Attendee', event: 'Event') -> int:
        """
        Add an attendee to the waitlist for an event.
        Returns the position in the waitlist.
        """
        event_queue = self._waitlists.setdefault(event.event_id, [])
        if attendee not in event_queue:
            event_queue.append(attendee)
        return event_queue.index(attendee) + 1
    
    def process_cancellation(self, event: 'Event') -> Optional['Attendee']:
        """
        Process a cancellation - return next waitlisted attendee if any.
        Should notify the attendee that a spot is available.
        """
        event_queue = self._waitlists.get(event.event_id, [])
        if not event_queue:
            return None

        next_attendee = event_queue.pop(0)
        next_attendee.notify(
            event.name,
            f"A spot is now available for {event.name}. Please complete registration."
        )
        return next_attendee
    
    def get_waitlist_position(self, attendee: 'Attendee', event: 'Event') -> int:
        """Get an attendee's position in the waitlist (1-indexed). Returns -1 if not found."""
        event_queue = self._waitlists.get(event.event_id, [])
        if attendee not in event_queue:
            return -1
        return event_queue.index(attendee) + 1


# ============================================================
# TICKET HIERARCHY
# ============================================================
class Ticket(ABC):
    """
    Abstract base class for all ticket types.
    
    Attributes:
        ticket_id (str): Unique ticket identifier
        base_price (float): Base price before modifiers
        event (Event): The event this ticket is for
    """
    
    def __init__(self, ticket_id: str, base_price: float, event: 'Event'):
        """Initialise a ticket with protected attributes for encapsulation."""
        self._ticket_id = ticket_id
        self._base_price = base_price
        self._event = event

    @property
    def ticket_id(self) -> str:
        """Return the unique ticket ID."""
        return self._ticket_id

    @property
    def base_price(self) -> float:
        """Return the ticket base price before modifiers."""
        return self._base_price

    @property
    def event(self) -> 'Event':
        """Return the event associated with this ticket."""
        return self._event
    
    @abstractmethod
    def calculate_price(self) -> float:
        """Calculate final ticket price with any modifiers."""
        pass
    
    @abstractmethod
    def get_benefits(self) -> List[str]:
        """Return list of benefits included with this ticket."""
        pass
    
    def is_valid(self) -> bool:
        """Check if ticket is valid for purchase. Override for specific rules."""
        return True
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}[{self._ticket_id}] - ${self.calculate_price():.2f}"


class StandardTicket(Ticket):
    """Standard admission ticket with basic access."""
    
    PRICE_MODIFIER = 1.0
    
    def calculate_price(self) -> float:
        """Return standard ticket price with no surcharge/discount."""
        return self._base_price * self.PRICE_MODIFIER
    
    def get_benefits(self) -> List[str]:
        """Return benefits included with a standard ticket."""
        return ["Access to main sessions"]


class VIPTicket(Ticket):
    """
    VIP ticket with premium benefits.
    Limited to 20% of event capacity.
    """
    
    PRICE_MODIFIER = 2.5
    MAX_PERCENTAGE = 0.20
    
    def calculate_price(self) -> float:
        """Return VIP price using the VIP multiplier."""
        return self._base_price * self.PRICE_MODIFIER
    
    def get_benefits(self) -> List[str]:
        """Return premium VIP benefits."""
        return [
            "Priority seating",
            "Networking dinner",
            "Speaker meet-and-greet"
        ]
    
    def is_valid(self) -> bool:
        """Check if VIP tickets are still available (20% cap)."""
        if self._event.capacity == -1:
            return True
        return self._event.get_vip_count() < self._event.capacity * self.MAX_PERCENTAGE


class EarlyBirdTicket(Ticket):
    """
    Discounted ticket for early registrations.
    Only available 30+ days before event.
    """
    
    PRICE_MODIFIER = 0.7  # 30% discount
    MIN_DAYS_BEFORE = 30
    
    def calculate_price(self) -> float:
        """Return early bird discounted price."""
        return self._base_price * self.PRICE_MODIFIER
    
    def get_benefits(self) -> List[str]:
        """Return benefits included with an early bird ticket."""
        return ["Access to main sessions", "30% early bird discount"]
    
    def is_valid(self) -> bool:
        """Check if event date is 30+ days away."""
        return (self._event.date - date.today()).days >= self.MIN_DAYS_BEFORE


class GroupTicket(Ticket):
    """
    Group booking ticket with volume discount.
    Requires minimum 5 attendees.
    """
    
    PRICE_MODIFIER = 0.8  # 20% discount per person
    MIN_GROUP_SIZE = 5
    
    def __init__(self, ticket_id: str, base_price: float, event: 'Event', group_size: int):
        """Initialise a group ticket and store the requested group size."""
        super().__init__(ticket_id, base_price, event)
        self._group_size = group_size
    
    @property
    def group_size(self) -> int:
        """Return the number of attendees covered by this group ticket."""
        return self._group_size
    
    def calculate_price(self) -> float:
        """Return discounted group total price."""
        return self._base_price * self.PRICE_MODIFIER * self._group_size
    
    def get_benefits(self) -> List[str]:
        """Return benefits included with a group booking."""
        return [
            "Access to main sessions",
            "20% group discount",
            f"Group of {self._group_size}"
        ]
    
    def is_valid(self) -> bool:
        """Validate minimum group size."""
        return self._group_size >= self.MIN_GROUP_SIZE


# ============================================================
# ATTENDEE HIERARCHY
# ============================================================
class Attendee(WaitlistObserver):
    """
    Base class for event attendees.
    
    Attributes:
        attendee_id (str): Unique identifier
        name (str): Full name
        email (str): Contact email
        ticket (Ticket): Assigned ticket (None until registered)
    """
    
    def __init__(self, attendee_id: str, name: str, email: str):
        """Initialise an attendee and default ticket to None until registration."""
        self._attendee_id = attendee_id
        self._name = name
        self._email = email
        self._ticket: Optional[Ticket] = None

    @property
    def attendee_id(self) -> str:
        """Return attendee unique ID."""
        return self._attendee_id

    @property
    def name(self) -> str:
        """Return attendee full name."""
        return self._name

    @property
    def email(self) -> str:
        """Return attendee contact email."""
        return self._email

    @property
    def ticket(self) -> Optional[Ticket]:
        """Return assigned ticket, or None when not assigned."""
        return self._ticket
    
    def assign_ticket(self, ticket: Ticket) -> None:
        """Assign a ticket to this attendee."""
        self._ticket = ticket
    
    def notify(self, event_name: str, message: str) -> None:
        """Receive notification about waitlist status."""
        print(f"NOTIFICATION to {self._name} ({event_name}): {message}")
    
    def display_info(self) -> None:
        """Display attendee information."""
        ticket_text = self._ticket.__class__.__name__ if self._ticket else "No ticket"
        print(
            f"{self.get_role()} - {self._name} | "
            f"Email: {self._email} | Ticket: {ticket_text}"
        )
    
    def get_role(self) -> str:
        """Return the attendee's role."""
        return "Attendee"
    
    def __str__(self) -> str:
        return f"{self._name} ({self._email})"


class SpeakerAttendee(Attendee):
    """
    Attendee who is also a speaker at the event.
    Receives complimentary VIP ticket.
    
    Additional Attributes:
        bio (str): Speaker biography
        session_title (str): Title of their presentation
    """
    
    def __init__(self, attendee_id: str, name: str, email: str, 
                 bio: str, session_title: str):
        """Initialise a speaker attendee with biography and session title."""
        super().__init__(attendee_id, name, email)
        self._bio = bio
        self._session_title = session_title

    @property
    def bio(self) -> str:
        """Return speaker biography."""
        return self._bio

    @property
    def session_title(self) -> str:
        """Return the title of the speaker's presentation."""
        return self._session_title
    
    def display_info(self) -> None:
        """Override to show speaker details."""
        print(
            f"Speaker - {self.name} | Email: {self.email} | "
            f"Session: {self._session_title} | Bio: {self._bio}"
        )
    
    def get_role(self) -> str:
        return "Speaker"


class SponsorAttendee(Attendee):
    """
    Attendee from a sponsor company.
    Has booth access and special badge.
    
    Additional Attributes:
        company_name (str): Sponsor company name
        sponsorship_tier (str): e.g., "Gold", "Silver", "Bronze"
    """
    
    def __init__(self, attendee_id: str, name: str, email: str,
                 company_name: str, sponsorship_tier: str):
        """Initialise a sponsor attendee with company and tier information."""
        super().__init__(attendee_id, name, email)
        self._company_name = company_name
        self._sponsorship_tier = sponsorship_tier

    @property
    def company_name(self) -> str:
        """Return sponsor company name."""
        return self._company_name

    @property
    def sponsorship_tier(self) -> str:
        """Return sponsor tier label."""
        return self._sponsorship_tier
    
    def display_info(self) -> None:
        """Override to show sponsor details."""
        print(
            f"Sponsor Representative - {self.name} | Email: {self.email} | "
            f"Company: {self._company_name} | Tier: {self._sponsorship_tier}"
        )
    
    def get_role(self) -> str:
        return "Sponsor Representative"


# ============================================================
# EVENT HIERARCHY
# ============================================================
class Event(Registrable, ABC):
    """
    Abstract base class for all events.
    
    Attributes:
        event_id (str): Unique identifier
        name (str): Event name
        date (date): Event date
        capacity (int): Maximum attendees (-1 for unlimited)
        attendees (list): Registered attendees
        base_ticket_price (float): Base price for tickets
    """
    
    def __init__(self, event_id: str, name: str, event_date: date, 
                 capacity: int, base_ticket_price: float = 100.0):
        """Initialise core event attributes and supporting state."""
        self._event_id = event_id
        self._name = name
        self._date = event_date
        self._capacity = capacity
        self._base_ticket_price = base_ticket_price
        self._attendees: List[Attendee] = []
        self._waitlist_manager = WaitlistManager()

    @property
    def event_id(self) -> str:
        """Return unique event ID."""
        return self._event_id

    @property
    def name(self) -> str:
        """Return event display name."""
        return self._name

    @property
    def date(self) -> date:
        """Return event date."""
        return self._date

    @property
    def capacity(self) -> int:
        """Return event capacity (-1 means unlimited)."""
        return self._capacity

    @property
    def base_ticket_price(self) -> float:
        """Return base ticket price used by ticket factory."""
        return self._base_ticket_price
    
    @abstractmethod
    def display_details(self) -> None:
        """Display event details. Must be overridden."""
        pass
    
    @abstractmethod
    def is_registration_open(self) -> bool:
        """Check if registration is still open."""
        pass
    
    def register_attendee(self, attendee: Attendee) -> bool:
        """
        Register an attendee for this event.
        
        Args:
            attendee: The attendee to register
            
        Returns:
            bool: True if registration successful
            
        Raises:
            EventFullError: If event is at capacity
            DuplicateRegistrationError: If email already registered
        """
        if self.get_attendee_by_email(attendee.email):
            raise DuplicateRegistrationError(
                f"Email '{attendee.email}' is already registered for {self._name}"
            )

        if self._capacity != -1 and len(self._attendees) >= self._capacity:
            raise EventFullError(f"Event '{self._name}' is full")

        self._attendees.append(attendee)
        return True
    
    def cancel_registration(self, attendee_id: str) -> Optional[Attendee]:
        """
        Cancel an attendee's registration.
        
        Returns the cancelled attendee, or None if not found.
        Should trigger waitlist processing.
        """
        for idx, attendee in enumerate(self._attendees):
            if attendee.attendee_id == attendee_id:
                removed = self._attendees.pop(idx)
                next_attendee = self._waitlist_manager.process_cancellation(self)
                if next_attendee:
                    self.register_attendee(next_attendee)
                return removed
        return None
    
    def get_available_spots(self) -> int:
        """Return number of available spots. -1 if unlimited."""
        if self._capacity == -1:
            return -1
        return self._capacity - len(self._attendees)
    
    def calculate_revenue(self) -> float:
        """Calculate total revenue from ticket sales."""
        total = 0.0
        for attendee in self._attendees:
            if attendee.ticket is not None:
                total += attendee.ticket.calculate_price()
        return total
    
    def get_vip_count(self) -> int:
        """Return count of VIP tickets sold."""
        return sum(1 for attendee in self._attendees if isinstance(attendee.ticket, VIPTicket))
    
    def get_attendee_by_email(self, email: str) -> Optional[Attendee]:
        """Find an attendee by email."""
        for attendee in self._attendees:
            if attendee.email.lower() == email.lower():
                return attendee
        return None
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}[{self._event_id}] {self._name}"


class Conference(Event):
    """
    Multi-track conference with keynote speaker.
    Minimum 50 attendees recommended.
    
    Additional Attributes:
        num_tracks (int): Number of parallel session tracks
        keynote_speaker (str): Name of keynote speaker
    """
    
    MIN_ATTENDEES = 50
    
    def __init__(self, event_id: str, name: str, event_date: date, capacity: int,
                 num_tracks: int, keynote_speaker: str, base_ticket_price: float = 200.0):
        """Initialise a conference and validate recommended minimum capacity."""
        if capacity < self.MIN_ATTENDEES:
            raise InvalidEventConfigError(
                f"Conference capacity must be >= {self.MIN_ATTENDEES}"
            )
        super().__init__(event_id, name, event_date, capacity, base_ticket_price)
        self._num_tracks = num_tracks
        self._keynote_speaker = keynote_speaker

    @property
    def num_tracks(self) -> int:
        """Return number of conference tracks."""
        return self._num_tracks

    @property
    def keynote_speaker(self) -> str:
        """Return keynote speaker name."""
        return self._keynote_speaker
    
    def display_details(self) -> None:
        """Show conference details including tracks and keynote."""
        print(
            f"Conference: {self.name} ({self.event_id}) on {self.date} | "
            f"Capacity: {self.capacity} | Tracks: {self._num_tracks} | "
            f"Keynote: {self._keynote_speaker}"
        )
    
    def is_registration_open(self) -> bool:
        """Check if registration is open (has capacity and date in future)."""
        return self.date >= date.today() and self.get_available_spots() > 0


class Workshop(Event):
    """
    Hands-on workshop with limited capacity.
    Maximum 30 participants.
    
    Additional Attributes:
        instructor (str): Workshop instructor name
        skill_level (str): e.g., "Beginner", "Intermediate", "Advanced"
        materials_included (bool): Whether materials are provided
    """
    
    MAX_CAPACITY = 30
    
    def __init__(self, event_id: str, name: str, event_date: date, capacity: int,
                 instructor: str, skill_level: str, materials_included: bool,
                 base_ticket_price: float = 150.0):
        """Initialise workshop details and enforce maximum capacity constraint."""
        if capacity > self.MAX_CAPACITY:
            raise InvalidEventConfigError(
                f"Workshop capacity cannot exceed {self.MAX_CAPACITY}"
            )
        super().__init__(event_id, name, event_date, capacity, base_ticket_price)
        self._instructor = instructor
        self._skill_level = skill_level
        self._materials_included = materials_included

    @property
    def instructor(self) -> str:
        """Return workshop instructor name."""
        return self._instructor

    @property
    def skill_level(self) -> str:
        """Return workshop skill level."""
        return self._skill_level

    @property
    def materials_included(self) -> bool:
        """Return whether workshop materials are provided."""
        return self._materials_included
    
    def display_details(self) -> None:
        """Show workshop details."""
        print(
            f"Workshop: {self.name} ({self.event_id}) on {self.date} | "
            f"Capacity: {self.capacity} | Instructor: {self._instructor} | "
            f"Level: {self._skill_level} | Materials: {self._materials_included}"
        )
    
    def is_registration_open(self) -> bool:
        """Check if registration is open (within capacity and date in future)."""
        return self.date >= date.today() and self.get_available_spots() > 0


class Webinar(Event):
    """
    Online event with unlimited capacity.
    Set capacity to -1 for unlimited.
    
    Additional Attributes:
        platform (str): e.g., "Zoom", "Teams", "Webex"
        recording_available (bool): Whether recording will be available
        timezone (str): Event timezone e.g., "AEST", "UTC"
    """
    
    def __init__(self, event_id: str, name: str, event_date: date,
                 platform: str, recording_available: bool, timezone: str,
                 base_ticket_price: float = 50.0):
        """Initialise webinar with unlimited capacity and online-delivery metadata."""
        super().__init__(event_id, name, event_date, -1, base_ticket_price)
        self._platform = platform
        self._recording_available = recording_available
        self._timezone = timezone

    @property
    def platform(self) -> str:
        """Return webinar delivery platform."""
        return self._platform

    @property
    def recording_available(self) -> bool:
        """Return whether recording is available after the session."""
        return self._recording_available

    @property
    def timezone(self) -> str:
        """Return webinar timezone label."""
        return self._timezone
    
    def display_details(self) -> None:
        """Show webinar details including platform and timezone."""
        print(
            f"Webinar: {self.name} ({self.event_id}) on {self.date} | "
            f"Platform: {self._platform} | Timezone: {self._timezone} | "
            f"Recording: {self._recording_available}"
        )
    
    def is_registration_open(self) -> bool:
        """Always open if before event date (unlimited capacity)."""
        return self.date >= date.today()
    
    def get_available_spots(self) -> int:
        """Return -1 for unlimited capacity."""
        return -1


# ============================================================
# SESSION MANAGEMENT
# ============================================================
class Session(Schedulable):
    """
    Represents a single session within an event.
    
    Attributes:
        session_id (str): Unique identifier
        title (str): Session title
        speaker (SpeakerAttendee): The presenter
        duration_minutes (int): Length of session
        room (str): Room assignment
        start_time (datetime): When session starts
    """
    
    def __init__(self, session_id: str, title: str, speaker: SpeakerAttendee,
                 duration_minutes: int, room: str, start_time: datetime):
        """Initialise a session with scheduling and room metadata."""
        self._session_id = session_id
        self._title = title
        self._speaker = speaker
        self._duration_minutes = duration_minutes
        self._room = room
        self._start_time = start_time

    @property
    def session_id(self) -> str:
        """Return session unique ID."""
        return self._session_id

    @property
    def title(self) -> str:
        """Return session title."""
        return self._title

    @property
    def speaker(self) -> SpeakerAttendee:
        """Return speaker presenting this session."""
        return self._speaker

    @property
    def duration_minutes(self) -> int:
        """Return session duration in minutes."""
        return self._duration_minutes

    @property
    def room(self) -> str:
        """Return room assignment."""
        return self._room

    @property
    def start_time(self) -> datetime:
        """Return scheduled start time."""
        return self._start_time
    
    def get_time_slot(self) -> tuple:
        """Return (start_time, end_time) as datetime objects."""
        return self._start_time, self.get_end_time()
    
    def get_end_time(self) -> datetime:
        """Calculate and return the end time."""
        return self._start_time + timedelta(minutes=self._duration_minutes)
    
    def conflicts_with(self, other: 'Session') -> bool:
        """
        Check if this session conflicts with another in the same room.
        Returns True if same room AND overlapping times.
        """
        return self._room == other.room and self._times_overlap(other)
    
    def has_speaker_conflict(self, other: 'Session') -> bool:
        """Check if same speaker has overlapping sessions."""
        return self._speaker.attendee_id == other.speaker.attendee_id and self._times_overlap(other)
    
    def _times_overlap(self, other: 'Session') -> bool:
        """Helper to check if two sessions' times overlap."""
        my_start, my_end = self.get_time_slot()
        other_start, other_end = other.get_time_slot()
        return my_start < other_end and other_start < my_end
    
    def __str__(self) -> str:
        start, end = self.get_time_slot()
        return f"Session[{self._session_id}] '{self._title}' in {self._room} ({start.strftime('%H:%M')}-{end.strftime('%H:%M')})"


class SessionScheduler:
    """
    Manages session scheduling and conflict detection.
    """
    
    def __init__(self):
        self._sessions: List[Session] = []
    
    def add_session(self, session: Session) -> None:
        """
        Add a session to the schedule.
        
        Args:
            session: The session to add
            
        Raises:
            RoomConflictError: If room is already booked at that time
            SpeakerConflictError: If speaker has conflicting session
        """
        for existing in self._sessions:
            if session.conflicts_with(existing):
                raise RoomConflictError(
                    f"Room conflict: {session.room} already in use during requested slot"
                )
            if session.has_speaker_conflict(existing):
                raise SpeakerConflictError(
                    f"Speaker conflict: {session.speaker.name} has overlapping sessions"
                )
        self._sessions.append(session)
    
    def remove_session(self, session_id: str) -> Optional[Session]:
        """Remove a session by ID. Returns the removed session or None."""
        for idx, session in enumerate(self._sessions):
            if session.session_id == session_id:
                return self._sessions.pop(idx)
        return None
    
    def get_schedule(self) -> List[Session]:
        """Return all scheduled sessions sorted by start time."""
        return sorted(self._sessions.copy(), key=lambda s: s.start_time)
    
    def get_sessions_by_room(self, room: str) -> List[Session]:
        """Get all sessions in a specific room."""
        return [session for session in self._sessions if session.room == room]
    
    def get_sessions_by_speaker(self, speaker: SpeakerAttendee) -> List[Session]:
        """Get all sessions by a specific speaker."""
        return [session for session in self._sessions if session.speaker.attendee_id == speaker.attendee_id]


# ============================================================
# FACTORY PATTERN
# ============================================================
class EventFactory:
    """
    Factory for creating different types of events.
    
    Usage:
        factory = EventFactory()
        event = factory.create_event("conference", event_id="CONF001", ...)
    """
    
    def create_event(self, event_type: str, **kwargs) -> Event:
        """
        Create an event of the specified type.
        
        Args:
            event_type: One of "conference", "workshop", "webinar"
            **kwargs: Event-specific attributes
            
        Returns:
            Event: The created event instance
            
        Raises:
            ValueError: If event_type is unknown
            InvalidEventConfigError: If required kwargs are missing or invalid
        """
        event_type = event_type.lower()
        
        try:
            if event_type == "conference":
                return Conference(
                    event_id=kwargs["event_id"],
                    name=kwargs["name"],
                    event_date=kwargs["event_date"],
                    capacity=kwargs["capacity"],
                    num_tracks=kwargs["num_tracks"],
                    keynote_speaker=kwargs["keynote_speaker"],
                    base_ticket_price=kwargs.get("base_ticket_price", 200.0),
                )
            elif event_type == "workshop":
                return Workshop(
                    event_id=kwargs["event_id"],
                    name=kwargs["name"],
                    event_date=kwargs["event_date"],
                    capacity=kwargs["capacity"],
                    instructor=kwargs["instructor"],
                    skill_level=kwargs["skill_level"],
                    materials_included=kwargs["materials_included"],
                    base_ticket_price=kwargs.get("base_ticket_price", 150.0),
                )
            elif event_type == "webinar":
                return Webinar(
                    event_id=kwargs["event_id"],
                    name=kwargs["name"],
                    event_date=kwargs["event_date"],
                    platform=kwargs["platform"],
                    recording_available=kwargs["recording_available"],
                    timezone=kwargs["timezone"],
                    base_ticket_price=kwargs.get("base_ticket_price", 50.0),
                )
            else:
                raise ValueError(f"Unknown event type: '{event_type}'")
        except KeyError as e:
            raise InvalidEventConfigError(f"Missing required field for {event_type}: {e}") from e
        except Exception as e:
            raise InvalidEventConfigError(f"Failed to create {event_type}: {e}") from e


class TicketFactory:
    """Factory for creating different types of tickets."""
    
    def create_ticket(self, ticket_type: str, ticket_id: str, 
                      event: Event, **kwargs) -> Ticket:
        """
        Create a ticket of the specified type.
        
        Args:
            ticket_type: One of "standard", "vip", "earlybird", "group"
            ticket_id: Unique ticket identifier
            event: The event this ticket is for
            **kwargs: Ticket-specific attributes (e.g., group_size for GroupTicket)
            
        Returns:
            Ticket: The created ticket instance
            
        Raises:
            ValueError: If ticket_type is unknown
            InvalidTicketError: If ticket validation fails
        """
        ticket_type = ticket_type.lower()
        base_price = event.base_ticket_price

        if ticket_type == "standard":
            return StandardTicket(ticket_id, base_price, event)

        if ticket_type == "vip":
            ticket = VIPTicket(ticket_id, base_price, event)
            if not ticket.is_valid():
                raise InvalidTicketError("VIP ticket limit reached for this event")
            return ticket

        if ticket_type == "earlybird":
            ticket = EarlyBirdTicket(ticket_id, base_price, event)
            if not ticket.is_valid():
                raise InvalidTicketError("Early bird tickets are no longer available")
            return ticket

        if ticket_type == "group":
            if "group_size" not in kwargs:
                raise InvalidTicketError("Group ticket requires 'group_size'")
            ticket = GroupTicket(ticket_id, base_price, event, kwargs["group_size"])
            if not ticket.is_valid():
                raise InvalidTicketError("Group ticket requires at least 5 attendees")
            return ticket

        raise ValueError(f"Unknown ticket type: '{ticket_type}'")


# ============================================================
# ADAPTER PATTERN
# ============================================================
class LegacyTicketingSystem:
    """
    Legacy ticketing system from previous vendor.
    DO NOT MODIFY THIS CLASS.
    """
    
    def __init__(self):
        self.old_bookings = {
            "BK001": {"guest_name": "John Smith", "email_addr": "john@email.com", 
                      "event_code": "EVT100", "tier": "GOLD", "amount_paid": 15000},
            "BK002": {"guest_name": "Jane Doe", "email_addr": "jane@email.com",
                      "event_code": "EVT100", "tier": "SILVER", "amount_paid": 8000},
            "BK003": {"guest_name": "Bob Wilson", "email_addr": "bob@email.com",
                      "event_code": "EVT200", "tier": "BRONZE", "amount_paid": 5000},
        }
    
    def fetch_booking(self, booking_ref: str) -> Optional[Dict]:
        """Fetch booking data in legacy format. Returns None if not found."""
        return self.old_bookings.get(booking_ref, None)
    
    def get_all_bookings(self) -> Dict[str, Dict]:
        """Return all bookings."""
        return self.old_bookings.copy()


class LegacyBookingAdapter:
    """
    Adapter to convert legacy booking data to current system format.
    
    Conversions:
        - amount_paid (cents) → ticket_price (dollars): divide by 100
        - tier GOLD → VIPTicket, SILVER/BRONZE → StandardTicket
        - guest_name → name
        - email_addr → email
        - booking_ref → attendee_id
    """
    
    TIER_MAPPING = {
        "GOLD": "vip",
        "SILVER": "standard",
        "BRONZE": "standard"
    }
    
    def __init__(self, legacy_system: LegacyTicketingSystem):
        """Store dependency on the legacy booking source system."""
        self._legacy_system = legacy_system
        self._ticket_factory = TicketFactory()
    
    def convert_booking(self, booking_ref: str, event: Event) -> tuple:
        """
        Convert legacy booking to (Attendee, Ticket) tuple.
        
        Args:
            booking_ref: The legacy booking reference
            event: The event to create the ticket for
            
        Returns:
            tuple: (Attendee, Ticket) objects
            
        Raises:
            ValueError: If booking_ref not found in legacy system
        """
        legacy_data = self._legacy_system.fetch_booking(booking_ref)
        if legacy_data is None:
            raise ValueError(f"Legacy booking '{booking_ref}' not found")

        attendee = Attendee(
            attendee_id=booking_ref,
            name=legacy_data["guest_name"],
            email=legacy_data["email_addr"]
        )

        ticket_type = self.TIER_MAPPING.get(legacy_data["tier"], "standard")
        ticket = self._ticket_factory.create_ticket(
            ticket_type=ticket_type,
            ticket_id=f"TKT-{booking_ref}",
            event=event,
        )
        attendee.assign_ticket(ticket)
        return attendee, ticket
    
    def import_all_bookings(self, event: Event) -> List[tuple]:
        """Import all legacy bookings for an event."""
        converted: List[tuple] = []
        for booking_ref in self._legacy_system.get_all_bookings().keys():
            converted.append(self.convert_booking(booking_ref, event))
        return converted


# ============================================================
# SINGLETON PATTERN - Event Registry
# ============================================================
class EventRegistryMeta(type):
    """Metaclass implementing Singleton pattern."""
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class EventRegistry(metaclass=EventRegistryMeta):
    """
    Central registry for all events and attendees.
    Implemented as a Singleton to ensure single source of truth.
    
    Attributes:
        events (dict): All events by event_id
        attendees (dict): All attendees by attendee_id
    """
    
    def __init__(self):
        """Initialise singleton registry storage for events and attendees."""
        self.events: Dict[str, Event] = {}
        self.attendees: Dict[str, Attendee] = {}
    
    def register_event(self, event: Event) -> None:
        """Register an event in the system."""
        self.events[event.event_id] = event
    
    def register_attendee(self, attendee: Attendee) -> None:
        """Register an attendee in the system."""
        self.attendees[attendee.attendee_id] = attendee
    
    def find_event(self, event_id: str) -> Optional[Event]:
        """Find an event by ID."""
        return self.events.get(event_id)
    
    def find_attendee(self, attendee_id: str) -> Optional[Attendee]:
        """Find an attendee by ID."""
        return self.attendees.get(attendee_id)
    
    def get_all_events(self) -> List[Event]:
        """Return all registered events."""
        return list(self.events.values())
    
    def get_all_attendees(self) -> List[Attendee]:
        """Return all registered attendees."""
        return list(self.attendees.values())
    
    def clear(self) -> None:
        """Clear all data (useful for testing)."""
        self.events.clear()
        self.attendees.clear()


# ============================================================
# MAIN DEMONSTRATION
# ============================================================
def main():
    """
    Main function to demonstrate all system capabilities.
    
    You should demonstrate:
    1. Creating events using the factory
    2. Creating different ticket types
    3. Registering attendees (successful and failed)
    4. Waitlist functionality (Observer pattern)
    5. Session scheduling with conflict detection
    6. Legacy system integration via adapter
    7. Exception handling for various error conditions
    8. Revenue reporting
    9. Singleton verification
    """
    
    print("=" * 60)
    print("EventPro Conference Management System")
    print("=" * 60)
    
    # ----------------------------------------------------------
    # 1. FACTORY PATTERN DEMO - Event Creation
    # ----------------------------------------------------------
    print("\n--- Creating Events via Factory ---")
    event_factory = EventFactory()
    ticket_factory = TicketFactory()

    pycon = event_factory.create_event(
        "conference",
        event_id="CONF001",
        name="PyCon AU 2026",
        event_date=date(2026, 8, 15),
        capacity=500,
        num_tracks=4,
        keynote_speaker="Guido van Rossum",
        base_ticket_price=220.0,
    )
    workshop = event_factory.create_event(
        "workshop",
        event_id="WS001",
        name="Data Science Bootcamp",
        event_date=date(2026, 6, 1),
        capacity=20,
        instructor="Dr Ada",
        skill_level="Intermediate",
        materials_included=True,
        base_ticket_price=180.0,
    )
    webinar = event_factory.create_event(
        "webinar",
        event_id="WEB001",
        name="MLOps Essentials",
        event_date=date(2026, 5, 30),
        platform="Zoom",
        recording_available=True,
        timezone="AEST",
        base_ticket_price=60.0,
    )
    pycon.display_details()
    workshop.display_details()
    webinar.display_details()
    
    # ----------------------------------------------------------
    # 2. TICKET CREATION
    # ----------------------------------------------------------
    print("\n--- Creating Tickets ---")
    standard_ticket = ticket_factory.create_ticket("standard", "T001", pycon)
    vip_ticket = ticket_factory.create_ticket("vip", "T002", pycon)
    early_bird_ticket = ticket_factory.create_ticket("earlybird", "T003", pycon)
    group_ticket = ticket_factory.create_ticket("group", "T004", pycon, group_size=6)

    print(standard_ticket, standard_ticket.get_benefits())
    print(vip_ticket, vip_ticket.get_benefits())
    print(early_bird_ticket, early_bird_ticket.get_benefits())
    print(group_ticket, group_ticket.get_benefits())
    
    # ----------------------------------------------------------
    # 3. ATTENDEE REGISTRATION
    # ----------------------------------------------------------
    print("\n--- Registering Attendees ---")
    attendee_1 = Attendee("A001", "Alice Tran", "alice@example.com")
    attendee_1.assign_ticket(standard_ticket)

    speaker_1 = SpeakerAttendee(
        "S001", "Bob Lin", "bob@example.com",
        "Senior Python engineer and educator.",
        "Scaling Python Services"
    )
    speaker_1.assign_ticket(vip_ticket)

    sponsor_1 = SponsorAttendee(
        "SP001", "Charlie Ng", "charlie@example.com",
        "TechCorp", "Gold"
    )
    sponsor_1.assign_ticket(group_ticket)

    pycon.register_attendee(attendee_1)
    pycon.register_attendee(speaker_1)
    pycon.register_attendee(sponsor_1)

    attendee_1.display_info()
    speaker_1.display_info()
    sponsor_1.display_info()
    
    # ----------------------------------------------------------
    # 4. OBSERVER PATTERN - Waitlist Demo
    # ----------------------------------------------------------
    print("\n--- Waitlist Demonstration ---")
    small_ws = event_factory.create_event(
        "workshop",
        event_id="WS002",
        name="Mini Workshop",
        event_date=date(2026, 5, 20),
        capacity=5,
        instructor="Sam Lee",
        skill_level="Beginner",
        materials_included=False,
        base_ticket_price=120.0,
    )

    for i in range(1, 6):
        attendee = Attendee(f"W{i:03}", f"Workshop Attendee {i}", f"w{i}@example.com")
        attendee.assign_ticket(ticket_factory.create_ticket("standard", f"WS-T{i}", small_ws))
        small_ws.register_attendee(attendee)

    wait_1 = Attendee("W006", "Wait One", "wait1@example.com")
    wait_2 = Attendee("W007", "Wait Two", "wait2@example.com")
    small_ws._waitlist_manager.add_to_waitlist(wait_1, small_ws)
    small_ws._waitlist_manager.add_to_waitlist(wait_2, small_ws)

    cancelled = small_ws.cancel_registration("W001")
    print(f"Cancelled: {cancelled.name if cancelled else 'None'}")
    
    # ----------------------------------------------------------
    # 5. SESSION SCHEDULING
    # ----------------------------------------------------------
    print("\n--- Session Scheduling ---")
    scheduler = SessionScheduler()
    session_1 = Session(
        "SES001", "Python at Scale", speaker_1, 60,
        "Room A", datetime(2026, 8, 15, 9, 0)
    )
    session_2 = Session(
        "SES002", "Data Pipelines", SpeakerAttendee(
            "S002", "Dana Fox", "dana@example.com", "Data architect", "Pipelines"
        ),
        60,
        "Room B", datetime(2026, 8, 15, 9, 30)
    )
    scheduler.add_session(session_1)
    scheduler.add_session(session_2)

    try:
        scheduler.add_session(Session(
            "SES003", "Room Clash", SpeakerAttendee(
                "S003", "Evan Lim", "evan@example.com", "Engineer", "Room Clash"
            ),
            45,
            "Room A", datetime(2026, 8, 15, 9, 30)
        ))
    except RoomConflictError as exc:
        print(f"Caught RoomConflictError: {exc}")

    try:
        scheduler.add_session(Session(
            "SES004", "Speaker Clash", speaker_1,
            45,
            "Room C", datetime(2026, 8, 15, 9, 45)
        ))
    except SpeakerConflictError as exc:
        print(f"Caught SpeakerConflictError: {exc}")
    
    # ----------------------------------------------------------
    # 6. ADAPTER PATTERN DEMO
    # ----------------------------------------------------------
    print("\n--- Legacy System Integration ---")
    legacy_system = LegacyTicketingSystem()
    adapter = LegacyBookingAdapter(legacy_system)
    imported = adapter.import_all_bookings(pycon)
    for attendee, ticket in imported:
        print(
            f"Imported {attendee.name} -> {ticket.__class__.__name__} "
            f"(${ticket.calculate_price():.2f})"
        )
    
    # ----------------------------------------------------------
    # 7. EXCEPTION HANDLING DEMO
    # ----------------------------------------------------------
    print("\n--- Exception Handling Demo ---")
    try:
        small_ws.register_attendee(Attendee("W008", "Overflow", "overflow@example.com"))
    except EventFullError as exc:
        print(f"Caught EventFullError: {exc}")

    try:
        pycon.register_attendee(Attendee("A999", "Duplicate", "alice@example.com"))
    except DuplicateRegistrationError as exc:
        print(f"Caught DuplicateRegistrationError: {exc}")

    near_event = event_factory.create_event(
        "webinar",
        event_id="WEB002",
        name="Near Event",
        event_date=date.today() + timedelta(days=10),
        platform="Teams",
        recording_available=False,
        timezone="AEST",
        base_ticket_price=40.0,
    )
    try:
        ticket_factory.create_ticket("earlybird", "EB-FAIL", near_event)
    except InvalidTicketError as exc:
        print(f"Caught InvalidTicketError (earlybird): {exc}")

    try:
        ticket_factory.create_ticket("group", "GR-FAIL", pycon, group_size=3)
    except InvalidTicketError as exc:
        print(f"Caught InvalidTicketError (group): {exc}")
    
    # ----------------------------------------------------------
    # 8. REVENUE REPORTING
    # ----------------------------------------------------------
    print("\n--- Revenue Report ---")
    total_revenue = pycon.calculate_revenue()
    print(f"{pycon.name} revenue: ${total_revenue:.2f}")

    breakdown: Dict[str, int] = {}
    for attendee in pycon._attendees:
        if attendee.ticket:
            key = attendee.ticket.__class__.__name__
            breakdown[key] = breakdown.get(key, 0) + 1
    print("Ticket breakdown:")
    for ticket_type, count in breakdown.items():
        print(f"  {ticket_type}: {count}")
    
    # ----------------------------------------------------------
    # 9. SINGLETON VERIFICATION
    # ----------------------------------------------------------
    print("\n--- Singleton Verification ---")
    reg1 = EventRegistry()
    reg2 = EventRegistry()
    reg1.register_event(pycon)
    reg1.register_event(workshop)
    reg1.register_event(webinar)
    reg1.register_attendee(attendee_1)
    reg1.register_attendee(speaker_1)

    print(f"Registry 1 ID: {id(reg1)}")
    print(f"Registry 2 ID: {id(reg2)}")
    print(f"Same instance? {reg1 is reg2}")
    print(f"Registry event count: {len(reg2.get_all_events())}")
    print(f"Registry attendee count: {len(reg2.get_all_attendees())}")


if __name__ == "__main__":
    main()
