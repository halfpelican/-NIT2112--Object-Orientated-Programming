"""
NIT2112 Object-Oriented Programming
Practical Test: FitZone Fitness Center Management System

Student Name: ________________________
Student ID:  ________________________
Date:        ________________________

AI Tools Used: ________________________

Declaration: I declare that this is my own work. I have used AI tools as a
development assistant and have documented my interactions. I can explain 
any part of my code and design decisions.
"""

from abc import ABC, abstractmethod
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Callable, Tuple
from enum import Enum
import uuid


# ============================================================================
# SECTION 1: ENUMS AND CONSTANTS
# ============================================================================

class BookingStatus(Enum):
    """Status of a class booking."""
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    ATTENDED = "attended"
    NO_SHOW = "no_show"


class ClassType(Enum):
    """Types of fitness classes offered."""
    YOGA = "yoga"
    HIIT = "hiit"
    SPINNING = "spinning"
    STRENGTH = "strength"


class MembershipTier(Enum):
    """Membership tier levels."""
    BASIC = "basic"
    PREMIUM = "premium"
    VIP = "vip"


# ============================================================================
# SECTION 2: CUSTOM EXCEPTIONS
# ============================================================================

class FitZoneError(Exception):
    """Base exception for all FitZone-related errors."""
    pass


class BookingError(FitZoneError):
    """Base exception for booking-related errors."""
    pass


class ClassFullError(BookingError):
    """Raised when attempting to book a full class."""
    def __init__(self, class_id: str, class_name: str):
        self.class_id = class_id
        self.class_name = class_name
        super().__init__(f"Class '{class_name}' (ID: {class_id}) is full.")


class ClassConflictError(BookingError):
    """Raised when there's a scheduling conflict."""
    def __init__(self, class1_id: str, class2_id: str, reason: str = ""):
        self.class1_id = class1_id
        self.class2_id = class2_id
        message = f"Scheduling conflict between classes '{class1_id}' and '{class2_id}'"
        if reason:
            message += f": {reason}"
        super().__init__(message)


class BookingLimitExceededError(BookingError):
    """Raised when member exceeds their weekly booking limit."""
    def __init__(self, member_id: str, current: int, limit: int):
        self.member_id = member_id
        self.current = current
        self.limit = limit
        super().__init__(
            f"Member '{member_id}' has reached weekly class limit "
            f"({current}/{limit})."
        )


class AdvanceBookingError(BookingError):
    """Raised when booking too far in advance for membership tier."""
    def __init__(self, member_id: str, requested_advance: int, max_advance: int):
        self.member_id = member_id
        self.requested_advance = requested_advance
        self.max_advance = max_advance
        super().__init__(
            f"Member '{member_id}' cannot book {requested_advance} hours in advance "
            f"(max: {max_advance} hours)."
        )


class MemberError(FitZoneError):
    """Base exception for member-related errors."""
    pass


class MemberNotFoundError(MemberError):
    """Raised when a member cannot be found."""
    def __init__(self, member_id: str):
        self.member_id = member_id
        super().__init__(f"Member '{member_id}' not found.")


class MemberSuspendedError(MemberError):
    """Raised when a suspended member tries to book."""
    def __init__(self, member_id: str, suspension_end: date):
        self.member_id = member_id
        self.suspension_end = suspension_end
        super().__init__(
            f"Member '{member_id}' is suspended until {suspension_end}."
        )


class PrerequisiteNotMetError(MemberError):
    """Raised when member hasn't completed required prerequisites."""
    def __init__(self, member_id: str, prerequisite: str, class_type: str):
        self.member_id = member_id
        self.prerequisite = prerequisite
        self.class_type = class_type
        super().__init__(
            f"Member '{member_id}' must complete {prerequisite} "
            f"before attending {class_type} classes."
        )


class MembershipAccessError(MemberError):
    """Raised when membership tier doesn't allow access to a class."""
    def __init__(self, member_id: str, tier: str, class_type: str, required_tiers: List[str]):
        self.member_id = member_id
        self.tier = tier
        self.class_type = class_type
        self.required_tiers = required_tiers
        super().__init__(
            f"Member '{member_id}' with {tier} membership cannot access "
            f"{class_type} classes. Required: {', '.join(required_tiers)}."
        )


class TrainerError(FitZoneError):
    """Base exception for trainer-related errors."""
    pass


class TrainerNotFoundError(TrainerError):
    """Raised when a trainer cannot be found."""
    def __init__(self, trainer_id: str):
        self.trainer_id = trainer_id
        super().__init__(f"Trainer '{trainer_id}' not found.")


class TrainerUnavailableError(TrainerError):
    """Raised when trainer is not available for a time slot."""
    def __init__(self, trainer_id: str, time_slot: str, reason: str = ""):
        self.trainer_id = trainer_id
        self.time_slot = time_slot
        message = f"Trainer '{trainer_id}' unavailable at {time_slot}"
        if reason:
            message += f": {reason}"
        super().__init__(message)


class SpecializationMismatchError(TrainerError):
    """Raised when trainer doesn't have required specialization."""
    def __init__(self, trainer_id: str, class_type: str, trainer_specs: List[str]):
        self.trainer_id = trainer_id
        self.class_type = class_type
        self.trainer_specs = trainer_specs
        super().__init__(
            f"Trainer '{trainer_id}' cannot instruct {class_type} classes. "
            f"Specializations: {', '.join(trainer_specs)}."
        )


class IntegrationError(FitZoneError):
    """Base exception for integration-related errors."""
    pass


class LegacyDataError(IntegrationError):
    """Raised when legacy data format is invalid."""
    def __init__(self, field: str, expected: str, received: str = ""):
        self.field = field
        message = f"Invalid legacy data for field '{field}'"
        if expected:
            message += f": expected {expected}"
        if received:
            message += f", got '{received}'"
        super().__init__(message)


# ============================================================================
# SECTION 3: INTERFACES (Abstract Base Classes)
# ============================================================================

class Schedulable(ABC):
    """Interface for schedulable activities."""
    
    @abstractmethod
    def get_time_slot(self) -> Tuple[datetime, datetime]:
        """Returns (start_time, end_time) tuple."""
        pass
    
    @abstractmethod
    def check_conflicts(self, other: 'Schedulable') -> bool:
        """Check if this conflicts with another schedulable item."""
        pass


class Bookable(ABC):
    """Interface for bookable resources."""
    
    @abstractmethod
    def can_enroll(self, member: 'Member') -> bool:
        """Check if member can enroll in this resource."""
        pass
    
    @abstractmethod
    def get_available_spots(self) -> int:
        """Returns number of available spots."""
        pass


class Observable(ABC):
    """Interface for observable subjects (Observer pattern)."""
    
    @abstractmethod
    def attach(self, observer: Callable[[str], None]) -> None:
        """Attach an observer."""
        pass
    
    @abstractmethod
    def detach(self, observer: Callable[[str], None]) -> None:
        """Detach an observer."""
        pass
    
    @abstractmethod
    def notify(self, message: str) -> None:
        """Notify all observers."""
        pass


# ============================================================================
# SECTION 4: TRAINER HIERARCHY
# ============================================================================

class Trainer(ABC):
    """Abstract base class for fitness trainers."""
    
    def __init__(self, trainer_id: str, name: str, 
                 certifications: List[str], specializations: List[str]):
        self._trainer_id = trainer_id
        self._name = name
        self._certifications = certifications
        self._specializations = specializations
        self._assigned_classes: List['FitnessClass'] = []
        self._availability: Dict[str, List[Tuple[datetime, datetime]]] = {}
    
    @property
    def trainer_id(self) -> str:
        return self._trainer_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def certifications(self) -> List[str]:
        return self._certifications.copy()
    
    @property
    def specializations(self) -> List[str]:
        return self._specializations.copy()
    
    @property
    def assigned_classes(self) -> List['FitnessClass']:
        return self._assigned_classes.copy()
    
    @property
    @abstractmethod
    def max_classes_per_day(self) -> int:
        """Maximum classes trainer can teach per day."""
        pass
    
    @property
    @abstractmethod
    def hourly_rate(self) -> float:
        """Trainer's hourly rate for personal training."""
        pass
    
    @property
    @abstractmethod
    def max_specializations(self) -> int:
        """Maximum number of specializations trainer can have."""
        pass
    
    def can_instruct(self, class_type: str) -> bool:
        """Check if trainer can instruct a given class type."""
        return class_type.lower() in [s.lower() for s in self._specializations]
    
    def assign_class(self, fitness_class: 'FitnessClass') -> None:
        """Assign a class to this trainer."""
        self._assigned_classes.append(fitness_class)
    
    def get_classes_on_date(self, target_date: date) -> List['FitnessClass']:
        """Get all classes assigned to trainer on a specific date."""
        return [c for c in self._assigned_classes 
                if c.schedule_time.date() == target_date]
    
    def is_available_at(self, start_time: datetime, end_time: datetime) -> bool:
        """Check if trainer is available during a time slot."""
        for assigned in self._assigned_classes:
            class_start, class_end = assigned.get_time_slot()
            # Check for overlap
            if not (end_time <= class_start or start_time >= class_end):
                return False
            # Check 30-minute break requirement
            break_needed = timedelta(minutes=30)
            if (class_end <= start_time < class_end + break_needed or
                class_start - break_needed < end_time <= class_start):
                return False
        return True
    
    def get_trainer_type(self) -> str:
        """Returns the type of trainer."""
        return self.__class__.__name__
    
    def __str__(self) -> str:
        return (f"{self.get_trainer_type()}: {self._name} "
                f"(Specializations: {', '.join(self._specializations)})")


class JuniorTrainer(Trainer):
    """
    Junior trainer class - entry-level instructor.
    
    - Maximum 1 specialization
    - Maximum 4 classes per day
    - Hourly rate: $25 for personal training
    - Can teach basic fitness classes
    """
    
    def __init__(self, trainer_id: str, name: str,
                 certifications: List[str], specializations: List[str]):
        """Initialise a junior trainer.
        
        Args:
            trainer_id: Unique trainer identifier
            name: Trainer's full name
            certifications: List of certifications held
            specializations: List of specializations (max 1 for junior)
            
        Raises:
            ValueError: If more than 1 specialization provided
        """
        if len(specializations) > 1:
            raise ValueError("Junior trainers can have maximum 1 specialization")
        super().__init__(trainer_id, name, certifications, specializations)
    
    @property
    def max_classes_per_day(self) -> int:
        return 4
    
    @property
    def hourly_rate(self) -> float:
        return 25.0
    
    @property
    def max_specializations(self) -> int:
        return 1


class SeniorTrainer(Trainer):
    """
    Senior trainer class - experienced instructor.
    
    - Maximum 3 specializations
    - Maximum 6 classes per day
    - Hourly rate: $45 for personal training
    - Can teach intermediate to advanced classes
    """
    
    def __init__(self, trainer_id: str, name: str,
                 certifications: List[str], specializations: List[str]):
        """Initialise a senior trainer.
        
        Args:
            trainer_id: Unique trainer identifier
            name: Trainer's full name
            certifications: List of certifications held
            specializations: List of specializations (max 3 for senior)
            
        Raises:
            ValueError: If more than 3 specializations provided
        """
        if len(specializations) > 3:
            raise ValueError("Senior trainers can have maximum 3 specializations")
        super().__init__(trainer_id, name, certifications, specializations)
    
    @property
    def max_classes_per_day(self) -> int:
        return 6
    
    @property
    def hourly_rate(self) -> float:
        return 45.0
    
    @property
    def max_specializations(self) -> int:
        return 3


class MasterTrainer(Trainer):
    """
    Master trainer class - elite instructor with full capabilities.
    
    - All specializations allowed (no limit)
    - Maximum 8 classes per day
    - Hourly rate: $75 for personal training
    - Can teach any class or substitute for other trainers in emergencies
    - Can mentor junior and senior trainers
    """
    
    def __init__(self, trainer_id: str, name: str,
                 certifications: List[str], specializations: List[str]):
        """Initialise a master trainer.
        
        Args:
            trainer_id: Unique trainer identifier
            name: Trainer's full name
            certifications: List of certifications held
            specializations: List of specializations (unlimited for master)
        """
        super().__init__(trainer_id, name, certifications, specializations)
    
    @property
    def max_classes_per_day(self) -> int:
        return 8
    
    @property
    def hourly_rate(self) -> float:
        return 75.0
    
    @property
    def max_specializations(self) -> int:
        return float('inf')  # Unlimited
    
    def can_instruct(self, class_type: str) -> bool:
        """Master trainers can instruct any class type."""
        return True
    
    def can_substitute(self, trainer: Trainer) -> bool:
        """Check if master trainer can substitute for another trainer."""
        return True


# ============================================================================
# SECTION 5: FITNESS CLASS HIERARCHY
# ============================================================================

class FitnessClass(Schedulable, Bookable, Observable):
    """Abstract base class for all fitness classes."""
    
    def __init__(self, class_id: str, name: str, instructor: Trainer,
                 schedule_time: datetime, duration_minutes: int,
                 max_capacity: int):
        self._class_id = class_id
        self._name = name
        self._instructor = instructor
        self._schedule_time = schedule_time
        self._duration_minutes = duration_minutes
        self._max_capacity = max_capacity
        self._enrolled_members: List['Member'] = []
        self._waitlist: List['Member'] = []
        self._observers: List[Callable[[str], None]] = []
        
        # Assign this class to the instructor
        instructor.assign_class(self)
    
    @property
    def class_id(self) -> str:
        return self._class_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def instructor(self) -> Trainer:
        return self._instructor
    
    @property
    def schedule_time(self) -> datetime:
        return self._schedule_time
    
    @property
    def duration_minutes(self) -> int:
        return self._duration_minutes
    
    @property
    def max_capacity(self) -> int:
        return self._max_capacity
    
    @property
    def enrolled_members(self) -> List['Member']:
        return self._enrolled_members.copy()
    
    @property
    def waitlist(self) -> List['Member']:
        return self._waitlist.copy()
    
    # Schedulable interface implementation
    def get_time_slot(self) -> Tuple[datetime, datetime]:
        """Returns (start_time, end_time) tuple."""
        end_time = self._schedule_time + timedelta(minutes=self._duration_minutes)
        return (self._schedule_time, end_time)
    
    def check_conflicts(self, other: 'Schedulable') -> bool:
        """Check if this conflicts with another schedulable item."""
        my_start, my_end = self.get_time_slot()
        other_start, other_end = other.get_time_slot()
        
        # Classes conflict if they overlap or are within 30 minutes
        buffer = timedelta(minutes=30)
        return not (my_end + buffer <= other_start or 
                    other_end + buffer <= my_start)
    
    # Bookable interface implementation
    def can_enroll(self, member: 'Member') -> bool:
        """Check if member can enroll (not full and no conflicts)."""
        return not self.is_full()
    
    def get_available_spots(self) -> int:
        """Returns number of available spots."""
        return self._max_capacity - len(self._enrolled_members)
    
    def is_full(self) -> bool:
        """Check if class is at capacity."""
        return len(self._enrolled_members) >= self._max_capacity
    
    # Observable interface implementation
    def attach(self, observer: Callable[[str], None]) -> None:
        """Attach an observer for notifications."""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Callable[[str], None]) -> None:
        """Detach an observer."""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self, message: str) -> None:
        """Notify all observers."""
        for observer in self._observers:
            observer(message)
    
    @abstractmethod
    def get_class_type(self) -> ClassType:
        """Returns the type of fitness class."""
        pass
    
    @abstractmethod
    def get_required_equipment(self) -> List[str]:
        """Returns list of required equipment."""
        pass
    
    @abstractmethod
    def get_allowed_tiers(self) -> List[MembershipTier]:
        """Returns list of membership tiers that can attend."""
        pass
    
    @abstractmethod
    def get_prerequisites(self) -> List[str]:
        """Returns list of prerequisites (e.g., 'fitness_assessment')."""
        pass
    
    def enroll_member(self, member: 'Member') -> None:
        """Enroll a member in this class."""
        if member not in self._enrolled_members:
            self._enrolled_members.append(member)
    
    def remove_member(self, member: 'Member') -> None:
        """Remove a member from this class."""
        if member in self._enrolled_members:
            self._enrolled_members.remove(member)
            # Notify about available spot
            if self._waitlist:
                self.notify(f"A spot has opened in {self._name}!")
    
    def add_to_waitlist(self, member: 'Member', is_vip: bool = False) -> int:
        """
        Add a member to the waitlist.
        VIP members are added to the front.
        Returns position in waitlist (1-indexed).
        """
        if member in self._waitlist:
            return self._waitlist.index(member) + 1
        
        if is_vip:
            # Find position after other VIPs
            vip_count = sum(1 for m in self._waitlist if m.get_tier() == MembershipTier.VIP)
            self._waitlist.insert(vip_count, member)
            return vip_count + 1
        else:
            self._waitlist.append(member)
            return len(self._waitlist)
    
    def remove_from_waitlist(self, member: 'Member') -> bool:
        """Remove a member from the waitlist."""
        if member in self._waitlist:
            self._waitlist.remove(member)
            return True
        return False
    
    def promote_from_waitlist(self) -> Optional['Member']:
        """Promote the first member from waitlist to enrolled."""
        if self._waitlist and not self.is_full():
            member = self._waitlist.pop(0)
            self.enroll_member(member)
            member.receive_notification(
                f"You've been enrolled in {self._name} from the waitlist!"
            )
            return member
        return None
    
    def __str__(self) -> str:
        return (f"{self.get_class_type().value.title()}: {self._name} "
                f"({len(self._enrolled_members)}/{self._max_capacity}) "
                f"at {self._schedule_time.strftime('%Y-%m-%d %H:%M')}")


class YogaClass(FitnessClass):
    """
    Yoga fitness class - low-impact flexibility training.
    
    - Capacity: 20 members
    - Duration: 60 minutes
    - Equipment: Yoga mats, blocks
    - Access: All membership tiers
    - Prerequisites: None
    - Limitations: Maximum 2 per member per day
    """
    
    MAX_CAPACITY = 20
    DURATION_MINS = 60
    
    def __init__(self, class_id: str, name: str, instructor: Trainer,
                 schedule_time: datetime):
        """Initialise a yoga class.
        
        Args:
            class_id: Unique class identifier
            name: Display name for the class
            instructor: Trainer who will instruct
            schedule_time: When the class is scheduled
        """
        super().__init__(class_id, name, instructor, schedule_time,
                         self.DURATION_MINS, self.MAX_CAPACITY)
    
    def get_class_type(self) -> ClassType:
        return ClassType.YOGA
    
    def get_required_equipment(self) -> List[str]:
        return ["Yoga mats", "Blocks"]
    
    def get_allowed_tiers(self) -> List[MembershipTier]:
        return [MembershipTier.BASIC, MembershipTier.PREMIUM, MembershipTier.VIP]
    
    def get_prerequisites(self) -> List[str]:
        return []


class HIITClass(FitnessClass):
    """
    HIIT (High-Intensity Interval Training) class - intense cardio workout.
    
    - Capacity: 15 members
    - Duration: 45 minutes
    - Equipment: Dumbbells, kettlebells, jump ropes
    - Access: Premium and VIP only
    - Prerequisites: Fitness assessment required
    """
    
    MAX_CAPACITY = 15
    DURATION_MINS = 45
    
    def __init__(self, class_id: str, name: str, instructor: Trainer,
                 schedule_time: datetime):
        """Initialise a HIIT class.
        
        Args:
            class_id: Unique class identifier
            name: Display name for the class
            instructor: Trainer who will instruct
            schedule_time: When the class is scheduled
        """
        super().__init__(class_id, name, instructor, schedule_time,
                         self.DURATION_MINS, self.MAX_CAPACITY)
    
    def get_class_type(self) -> ClassType:
        return ClassType.HIIT
    
    def get_required_equipment(self) -> List[str]:
        return ["Dumbbells", "Kettlebells", "Jump ropes"]
    
    def get_allowed_tiers(self) -> List[MembershipTier]:
        return [MembershipTier.PREMIUM, MembershipTier.VIP]
    
    def get_prerequisites(self) -> List[str]:
        return ["fitness_assessment"]


class SpinningClass(FitnessClass):
    """
    Spinning class - high-energy stationary bike training.
    
    - Capacity: 25 members
    - Duration: 50 minutes
    - Equipment: Spin bikes
    - Access: All membership tiers
    - VIP members receive priority booking during waitlist
    """
    
    MAX_CAPACITY = 25
    DURATION_MINS = 50
    
    def __init__(self, class_id: str, name: str, instructor: Trainer,
                 schedule_time: datetime):
        """Initialise a spinning class.
        
        Args:
            class_id: Unique class identifier
            name: Display name for the class
            instructor: Trainer who will instruct
            schedule_time: When the class is scheduled
        """
        super().__init__(class_id, name, instructor, schedule_time,
                         self.DURATION_MINS, self.MAX_CAPACITY)
    
    def get_class_type(self) -> ClassType:
        return ClassType.SPINNING
    
    def get_required_equipment(self) -> List[str]:
        return ["Spin bikes"]
    
    def get_allowed_tiers(self) -> List[MembershipTier]:
        return [MembershipTier.BASIC, MembershipTier.PREMIUM, MembershipTier.VIP]
    
    def get_prerequisites(self) -> List[str]:
        return []


class StrengthTraining(FitnessClass):
    """
    Strength training class - resistance and weightlifting training.
    
    - Capacity: 12 members
    - Duration: 60 minutes
    - Equipment: Barbells, weight plates, benches
    - Access: Premium and VIP only
    - Prerequisites: Safety induction required
    """
    
    MAX_CAPACITY = 12
    DURATION_MINS = 60
    
    def __init__(self, class_id: str, name: str, instructor: Trainer,
                 schedule_time: datetime):
        """Initialise a strength training class.
        
        Args:
            class_id: Unique class identifier
            name: Display name for the class
            instructor: Trainer who will instruct
            schedule_time: When the class is scheduled
        """
        super().__init__(class_id, name, instructor, schedule_time,
                         self.DURATION_MINS, self.MAX_CAPACITY)
    
    def get_class_type(self) -> ClassType:
        return ClassType.STRENGTH
    
    def get_required_equipment(self) -> List[str]:
        return ["Barbells", "Weight plates", "Benches"]
    
    def get_allowed_tiers(self) -> List[MembershipTier]:
        return [MembershipTier.PREMIUM, MembershipTier.VIP]
    
    def get_prerequisites(self) -> List[str]:
        return ["safety_induction"]


# ============================================================================
# SECTION 6: MEMBER HIERARCHY
# ============================================================================

class Member(ABC):
    """Abstract base class for fitness center members."""
    
    def __init__(self, member_id: str, name: str, email: str,
                 join_date: date):
        self._member_id = member_id
        self._name = name
        self._email = email
        self._join_date = join_date
        self._fitness_assessment_completed = False
        self._safety_induction_completed = False
        self._booked_classes: List[FitnessClass] = []
        self._attendance_history: List[Dict] = []  # {class_id, date, status}
        self._strikes = 0
        self._suspension_end: Optional[date] = None
    
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
    def fitness_assessment_completed(self) -> bool:
        return self._fitness_assessment_completed
    
    @fitness_assessment_completed.setter
    def fitness_assessment_completed(self, value: bool) -> None:
        self._fitness_assessment_completed = value
    
    @property
    def safety_induction_completed(self) -> bool:
        return self._safety_induction_completed
    
    @safety_induction_completed.setter
    def safety_induction_completed(self, value: bool) -> None:
        self._safety_induction_completed = value
    
    @property
    def booked_classes(self) -> List[FitnessClass]:
        return self._booked_classes.copy()
    
    @property
    def strikes(self) -> int:
        return self._strikes
    
    @property
    def suspension_end(self) -> Optional[date]:
        return self._suspension_end
    
    @property
    @abstractmethod
    def monthly_fee(self) -> float:
        """Monthly membership fee."""
        pass
    
    @property
    @abstractmethod
    def weekly_class_limit(self) -> int:
        """Maximum classes per week (0 = unlimited)."""
        pass
    
    @property
    @abstractmethod
    def guest_passes_per_month(self) -> int:
        """Number of guest passes per month."""
        pass
    
    @property
    @abstractmethod
    def booking_advance_hours(self) -> int:
        """How far in advance member can book (hours)."""
        pass
    
    @abstractmethod
    def get_tier(self) -> MembershipTier:
        """Returns the membership tier."""
        pass
    
    def is_suspended(self) -> bool:
        """Check if member is currently suspended."""
        if self._suspension_end is None:
            return False
        return date.today() < self._suspension_end
    
    def add_strike(self) -> None:
        """Add a strike to the member's record."""
        self._strikes += 1
        if self._strikes >= 3:
            self._suspension_end = date.today() + timedelta(days=7)
            self._strikes = 0  # Reset after suspension
    
    def book_class(self, fitness_class: FitnessClass) -> None:
        """Add a class to booked classes."""
        self._booked_classes.append(fitness_class)
    
    def cancel_class(self, fitness_class: FitnessClass) -> None:
        """Remove a class from booked classes."""
        if fitness_class in self._booked_classes:
            self._booked_classes.remove(fitness_class)
    
    def get_classes_this_week(self) -> int:
        """Count classes booked this week."""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=7)
        return sum(1 for c in self._booked_classes 
                   if week_start <= c.schedule_time.date() < week_end)
    
    def get_attendance_rate(self, days: int = 30) -> float:
        """Calculate attendance rate for the last N days."""
        cutoff = date.today() - timedelta(days=days)
        recent = [r for r in self._attendance_history 
                  if r['date'] >= cutoff]
        if not recent:
            return 1.0  # No history = assume good standing
        attended = sum(1 for r in recent if r['status'] == BookingStatus.ATTENDED)
        return attended / len(recent)
    
    def record_attendance(self, class_id: str, status: BookingStatus) -> None:
        """Record attendance for a class."""
        self._attendance_history.append({
            'class_id': class_id,
            'date': date.today(),
            'status': status
        })
        if status == BookingStatus.NO_SHOW:
            self.add_strike()
    
    def receive_notification(self, message: str) -> None:
        """Receive a notification (observer callback)."""
        print(f"[NOTIFICATION to {self._name}]: {message}")
    
    def can_book_in_advance(self, class_time: datetime) -> bool:
        """Check if member can book this far in advance."""
        hours_in_advance = (class_time - datetime.now()).total_seconds() / 3600
        return hours_in_advance <= self.booking_advance_hours
    
    def __str__(self) -> str:
        status = "SUSPENDED" if self.is_suspended() else "Active"
        return (f"{self.get_tier().value.title()}Member: {self._name} "
                f"({status}, Classes this week: {self.get_classes_this_week()})")


class BasicMember(Member):
    """
    Basic membership tier - entry-level membership.
    
    - Monthly fee: $49
    - Weekly class limit: 4 classes
    - Guest passes: 0 per month
    - Advance booking: 24 hours
    - Access: Yoga, Spinning classes only
    """
    
    def __init__(self, member_id: str, name: str, email: str,
                 join_date: date):
        """Initialise a basic member.
        
        Args:
            member_id: Unique member identifier
            name: Member's full name
            email: Member's email address
            join_date: Date member joined
        """
        super().__init__(member_id, name, email, join_date)
    
    @property
    def monthly_fee(self) -> float:
        return 49.0
    
    @property
    def weekly_class_limit(self) -> int:
        return 4
    
    @property
    def guest_passes_per_month(self) -> int:
        return 0
    
    @property
    def booking_advance_hours(self) -> int:
        return 24
    
    def get_tier(self) -> MembershipTier:
        return MembershipTier.BASIC


class PremiumMember(Member):
    """
    Premium membership tier - mid-level membership.
    
    - Monthly fee: $89
    - Weekly class limit: 12 classes
    - Guest passes: 2 per month
    - Advance booking: 72 hours (3 days)
    - Access: All classes except VIP-exclusive programs
    """
    
    def __init__(self, member_id: str, name: str, email: str,
                 join_date: date):
        """Initialise a premium member.
        
        Args:
            member_id: Unique member identifier
            name: Member's full name
            email: Member's email address
            join_date: Date member joined
        """
        super().__init__(member_id, name, email, join_date)
    
    @property
    def monthly_fee(self) -> float:
        return 89.0
    
    @property
    def weekly_class_limit(self) -> int:
        return 12
    
    @property
    def guest_passes_per_month(self) -> int:
        return 2
    
    @property
    def booking_advance_hours(self) -> int:
        return 72
    
    def get_tier(self) -> MembershipTier:
        return MembershipTier.PREMIUM


class VIPMember(Member):
    """
    VIP membership tier - elite membership with premium benefits.
    
    - Monthly fee: $149
    - Weekly class limit: Unlimited (0)
    - Guest passes: 4 per month
    - Advance booking: 168 hours (7 days)
    - Access: All classes
    - Personal training discount: 15% off hourly rates
    - Priority positioning on waitlists
    """
    
    TRAINER_DISCOUNT = 0.15  # 15% off
    
    def __init__(self, member_id: str, name: str, email: str,
                 join_date: date):
        """Initialise a VIP member.
        
        Args:
            member_id: Unique member identifier
            name: Member's full name
            email: Member's email address
            join_date: Date member joined
        """
        super().__init__(member_id, name, email, join_date)
        self._personal_training_hours = 0
    
    @property
    def monthly_fee(self) -> float:
        return 149.0
    
    @property
    def weekly_class_limit(self) -> int:
        return 0  # Unlimited
    
    @property
    def guest_passes_per_month(self) -> int:
        return 4
    
    @property
    def booking_advance_hours(self) -> int:
        return 168  # 7 days
    
    def get_tier(self) -> MembershipTier:
        return MembershipTier.VIP
    
    def get_trainer_discount_rate(self) -> float:
        """Get the personal training discount rate for VIP members.
        
        Returns:
            float: 15% discount rate (0.15)
        """
        return self.TRAINER_DISCOUNT


# ============================================================================
# SECTION 7: DESIGN PATTERNS
# ============================================================================

# --- Singleton Pattern ---
class RegistryMeta(type):
    """Metaclass for implementing Singleton pattern."""
    _instances: Dict[type, object] = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class FitZoneRegistry(metaclass=RegistryMeta):
    """
    Central registry for FitZone fitness center.
    Singleton pattern ensures single source of truth.
    """
    
    def __init__(self):
        self._classes: Dict[str, FitnessClass] = {}
        self._trainers: Dict[str, Trainer] = {}
        self._members: Dict[str, Member] = {}
        self._admin_observers: List[Callable[[str], None]] = []
    
    def add_class(self, fitness_class: FitnessClass) -> None:
        """Add a fitness class to the schedule."""
        # Check for conflicts with existing classes
        for existing in self._classes.values():
            if fitness_class.check_conflicts(existing):
                raise ClassConflictError(
                    fitness_class.class_id, 
                    existing.class_id,
                    "Classes overlap or are within 30 minutes of each other"
                )
        self._classes[fitness_class.class_id] = fitness_class
    
    def get_class(self, class_id: str) -> FitnessClass:
        """Retrieve a fitness class."""
        if class_id not in self._classes:
            raise BookingError(f"Class '{class_id}' not found.")
        return self._classes[class_id]
    
    def add_trainer(self, trainer: Trainer) -> None:
        """Add a trainer to the directory."""
        self._trainers[trainer.trainer_id] = trainer
    
    def get_trainer(self, trainer_id: str) -> Trainer:
        """Retrieve a trainer."""
        if trainer_id not in self._trainers:
            raise TrainerNotFoundError(trainer_id)
        return self._trainers[trainer_id]
    
    def add_member(self, member: Member) -> None:
        """Add a member to the directory."""
        self._members[member.member_id] = member
    
    def get_member(self, member_id: str) -> Member:
        """Retrieve a member."""
        if member_id not in self._members:
            raise MemberNotFoundError(member_id)
        return self._members[member_id]
    
    def attach_admin_observer(self, observer: Callable[[str], None]) -> None:
        """Attach an admin observer for system alerts."""
        if observer not in self._admin_observers:
            self._admin_observers.append(observer)
    
    def notify_admins(self, message: str) -> None:
        """Notify all admin observers."""
        for observer in self._admin_observers:
            observer(message)
    
    def get_all_classes(self) -> List[FitnessClass]:
        """Get all scheduled classes."""
        return list(self._classes.values())
    
    def get_all_trainers(self) -> List[Trainer]:
        """Get all trainers."""
        return list(self._trainers.values())
    
    def get_all_members(self) -> List[Member]:
        """Get all members."""
        return list(self._members.values())
    
    def get_classes_by_type(self, class_type: ClassType) -> List[FitnessClass]:
        """Get all classes of a specific type."""
        return [c for c in self._classes.values() 
                if c.get_class_type() == class_type]


# --- Factory Pattern ---
class FitnessClassFactory:
    """
    Factory for creating fitness classes.
    Centralizes creation logic and validates requirements.
    """
    
    @staticmethod
    def create_class(class_type: str, class_id: str, name: str,
                     instructor: Trainer, schedule_time: datetime,
                     **kwargs) -> FitnessClass:
        """
        Create a fitness class of the specified type.
        
        Args:
            class_type: One of 'yoga', 'hiit', 'spinning', 'strength'
            class_id: Unique identifier for the class
            name: Display name for the class
            instructor: Trainer who will instruct the class
            schedule_time: When the class is scheduled
            **kwargs: Additional parameters for specific class types
            
        Returns:
            FitnessClass: The created class
            
        Raises:
            SpecializationMismatchError: If trainer can't instruct this type
            BookingError: If class type is unknown
        """
        # Validate instructor specialization
        if not instructor.can_instruct(class_type):
            raise SpecializationMismatchError(
                instructor.trainer_id,
                class_type,
                instructor.specializations
            )
        
        class_type_lower = class_type.lower()
        
        if class_type_lower == "yoga":
            return YogaClass(class_id, name, instructor, schedule_time)
        elif class_type_lower == "hiit":
            return HIITClass(class_id, name, instructor, schedule_time)
        elif class_type_lower == "spinning":
            return SpinningClass(class_id, name, instructor, schedule_time)
        elif class_type_lower == "strength":
            return StrengthTraining(class_id, name, instructor, schedule_time)
        else:
            raise BookingError(f"Unknown fitness class type: '{class_type}'")


# --- Adapter Pattern ---
class LegacyMemberAdapter:
    """
    Adapter to convert legacy member data to modern Member objects.
    
    Legacy format:
    {
        "mem_no": "M-1234",
        "full_name": "John Smith",
        "contact_email": "john@email.com",
        "signup_date": "15/03/2024",  # DD/MM/YYYY
        "tier": "gold",  # bronze=Basic, silver=Premium, gold=VIP
        "assess_done": "Y",  # Y/N
        "safety_done": "N"
    }
    """
    
    TIER_MAPPING = {
        "bronze": "basic",
        "silver": "premium",
        "gold": "vip"
    }
    
    def adapt(self, legacy_data: Dict) -> Member:
        """
        Convert legacy member data to a Member object.
        
        Legacy format:
        {
            "mem_no": "M-1234",
            "full_name": "John Smith",
            "contact_email": "john@email.com",
            "signup_date": "15/03/2024",  # DD/MM/YYYY
            "tier": "gold",  # bronze=Basic, silver=Premium, gold=VIP
            "assess_done": "Y",  # Y/N
            "safety_done": "N"
        }
        
        Args:
            legacy_data: Dictionary in legacy format
            
        Returns:
            Member: Converted modern member
            
        Raises:
            LegacyDataError: If required fields are missing or invalid
        """
        # Validate required fields
        required_fields = ["mem_no", "full_name", "contact_email", 
                          "signup_date", "tier", "assess_done", "safety_done"]
        
        for field in required_fields:
            if field not in legacy_data:
                raise LegacyDataError(field, "present", "missing")
        
        # Map tier names
        tier_raw = legacy_data.get("tier", "").lower()
        if tier_raw not in self.TIER_MAPPING:
            raise LegacyDataError("tier", "bronze/silver/gold", tier_raw)
        
        modern_tier = self.TIER_MAPPING[tier_raw]
        
        # Parse date string (DD/MM/YYYY format)
        try:
            date_parts = legacy_data["signup_date"].split("/")
            if len(date_parts) != 3:
                raise ValueError("Invalid date format")
            day, month, year = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
            signup_date = date(year, month, day)
        except (ValueError, IndexError) as e:
            raise LegacyDataError("signup_date", "DD/MM/YYYY", 
                                legacy_data["signup_date"])
        
        # Convert Y/N to boolean
        assess_done = legacy_data["assess_done"].upper() == "Y"
        safety_done = legacy_data["safety_done"].upper() == "Y"
        
        # Create appropriate member type
        if modern_tier == "basic":
            member = BasicMember(
                legacy_data["mem_no"],
                legacy_data["full_name"],
                legacy_data["contact_email"],
                signup_date
            )
        elif modern_tier == "premium":
            member = PremiumMember(
                legacy_data["mem_no"],
                legacy_data["full_name"],
                legacy_data["contact_email"],
                signup_date
            )
        else:  # vip
            member = VIPMember(
                legacy_data["mem_no"],
                legacy_data["full_name"],
                legacy_data["contact_email"],
                signup_date
            )
        
        # Set completed prerequisites
        member.fitness_assessment_completed = assess_done
        member.safety_induction_completed = safety_done
        
        return member


# --- Observer Pattern ---
class AttendanceMonitor:
    """
    Monitors member attendance and alerts management.
    Observer pattern implementation.
    """
    
    def __init__(self, registry: FitZoneRegistry, threshold: float = 0.5):
        self._registry = registry
        self._threshold = threshold
        self._alerted_members: set = set()
    
    def check_attendance(self, member: Member) -> None:
        """
        Check a member's attendance rate and alert if below threshold.
        """
        if member.member_id in self._alerted_members:
            return  # Already alerted
        
        rate = member.get_attendance_rate()
        if rate < self._threshold:
            self._registry.notify_admins(
                f"ALERT: Member {member.name} (ID: {member.member_id}) "
                f"has attendance rate of {rate:.0%} (below {self._threshold:.0%})"
            )
            self._alerted_members.add(member.member_id)
    
    def reset_alerts(self) -> None:
        """Reset alerted members for a new period."""
        self._alerted_members.clear()


# ============================================================================
# SECTION 8: BOOKING SYSTEM
# ============================================================================

class Booking:
    """Represents a class booking."""
    
    def __init__(self, member: Member, fitness_class: FitnessClass):
        self._booking_id = str(uuid.uuid4())[:8]
        self._member = member
        self._fitness_class = fitness_class
        self._booking_time = datetime.now()
        self._status = BookingStatus.CONFIRMED
    
    @property
    def booking_id(self) -> str:
        return self._booking_id
    
    @property
    def member(self) -> Member:
        return self._member
    
    @property
    def fitness_class(self) -> FitnessClass:
        return self._fitness_class
    
    @property
    def booking_time(self) -> datetime:
        return self._booking_time
    
    @property
    def status(self) -> BookingStatus:
        return self._status
    
    @status.setter
    def status(self, value: BookingStatus) -> None:
        self._status = value
    
    def __str__(self) -> str:
        return (f"Booking {self._booking_id}: {self._member.name} -> "
                f"{self._fitness_class.name} ({self._status.value})")


class BookingService:
    """
    Manages all booking operations for FitZone.
    Enforces business rules and handles waitlists.
    """
    
    def __init__(self, registry: FitZoneRegistry):
        self._registry = registry
        self._bookings: Dict[str, Booking] = {}
        self._attendance_monitor = AttendanceMonitor(registry)
    
    def book_class(self, member: Member, fitness_class: FitnessClass) -> Booking:
        """
        Book a member into a fitness class.
        
        Enforces comprehensive business rules:
        - Member must not be suspended
        - Member tier must be allowed for this class
        - Member must complete required prerequisites
        - Member must not exceed weekly class limit
        - Booking must be within member's advance booking window
        - Class must not be full (else use join_waitlist)
        
        Parameters:
            member: The member booking the class
            fitness_class: The class to book
            
        Returns:
            Booking: Confirmed booking object
            
        Raises:
            MemberSuspendedError: If member is currently suspended
            MembershipAccessError: If tier not allowed for class
            PrerequisiteNotMetError: If prerequisites not completed
            BookingLimitExceededError: If weekly limit exceeded
            AdvanceBookingError: If booking too far in advance
            ClassFullError: If class is at capacity
        """
        # Check if member is suspended
        if member.is_suspended():
            raise MemberSuspendedError(member.member_id, member.suspension_end)
        
        # Check membership tier access
        allowed_tiers = fitness_class.get_allowed_tiers()
        if member.get_tier() not in allowed_tiers:
            raise MembershipAccessError(
                member.member_id,
                member.get_tier().value,
                fitness_class.get_class_type().value,
                [t.value for t in allowed_tiers]
            )
        
        # Check prerequisites
        prerequisites = fitness_class.get_prerequisites()
        if "fitness_assessment" in prerequisites:
            if not member.fitness_assessment_completed:
                raise PrerequisiteNotMetError(
                    member.member_id,
                    "fitness_assessment",
                    fitness_class.get_class_type().value
                )
        
        if "safety_induction" in prerequisites:
            if not member.safety_induction_completed:
                raise PrerequisiteNotMetError(
                    member.member_id,
                    "safety_induction",
                    fitness_class.get_class_type().value
                )
        
        # Check weekly class limit
        if member.weekly_class_limit > 0:  # 0 = unlimited
            classes_this_week = member.get_classes_this_week()
            if classes_this_week >= member.weekly_class_limit:
                raise BookingLimitExceededError(
                    member.member_id,
                    classes_this_week,
                    member.weekly_class_limit
                )
        
        # Check advance booking window
        if not member.can_book_in_advance(fitness_class.schedule_time):
            hours_available = member.booking_advance_hours
            raise AdvanceBookingError(
                member.member_id,
                int((fitness_class.schedule_time - datetime.now()).total_seconds() / 3600),
                hours_available
            )
        
        # Check if class is full
        if fitness_class.is_full():
            raise ClassFullError(fitness_class.class_id, fitness_class.name)
        
        # Create booking
        booking = Booking(member, fitness_class)
        self._bookings[booking.booking_id] = booking
        
        # Enroll member in class
        fitness_class.enroll_member(member)
        member.book_class(fitness_class)
        
        # Notify admins
        self._registry.notify_admins(
            f"BOOKING: {member.name} ({member.get_tier().value}) "
            f"booked {fitness_class.name}"
        )
        
        return booking
    
    def cancel_booking(self, member: Member, fitness_class: FitnessClass,
                       cancel_time: datetime = None) -> bool:
        """
        Cancel a member's booking for a fitness class.
        
        Late cancellations (within 2 hours of class start) add a strike
        to the member's record. Strikes can lead to suspension.
        
        Parameters:
            member: The member cancelling
            fitness_class: The class to cancel
            cancel_time: Time of cancellation (default: now)
            
        Returns:
            bool: True if cancelled successfully, False if booking not found
        """
        if cancel_time is None:
            cancel_time = datetime.now()
        
        # Find the booking to cancel
        found_booking = None
        for booking in self._bookings.values():
            if booking.member == member and booking.fitness_class == fitness_class:
                found_booking = booking
                break
        
        if not found_booking:
            return False  # Booking not found
        
        # Check if cancellation is late (within 2 hours of class start)
        hours_until_class = (fitness_class.schedule_time - cancel_time).total_seconds() / 3600
        is_late_cancellation = hours_until_class <= 2
        
        if is_late_cancellation:
            # Add strike for late cancellation
            member.add_strike()
            if member.is_suspended():
                member.receive_notification(
                    f"You have been suspended until {member.suspension_end} "
                    f"due to repeated late cancellations."
                )
        
        # Update booking status
        found_booking.status = BookingStatus.CANCELLED
        
        # Remove member from class enrollment
        fitness_class.remove_member(member)
        member.cancel_class(fitness_class)
        
        # Process waitlist if there are members waiting
        promoted_member = fitness_class.promote_from_waitlist()
        if promoted_member:
            fitness_class.attach(promoted_member.receive_notification)
        
        # Notify admins
        self._registry.notify_admins(
            f"CANCELLATION: {member.name} cancelled {fitness_class.name} "
            f"({('Late cancellation - Strike added' if is_late_cancellation else 'No penalty')})"
        )
        
        return True
    
    def join_waitlist(self, member: Member, 
                      fitness_class: FitnessClass) -> int:
        """
        Add member to waitlist for a full class.
        VIP members get priority positioning.
        
        Returns:
            int: Position in waitlist (1-indexed)
        """
        is_vip = member.get_tier() == MembershipTier.VIP
        position = fitness_class.add_to_waitlist(member, is_vip)
        
        # Subscribe member to notifications
        fitness_class.attach(member.receive_notification)
        
        return position
    
    def check_in_member(self, member: Member, 
                        fitness_class: FitnessClass) -> bool:
        """
        Check a member into a class.
        Records attendance.
        """
        if member not in fitness_class.enrolled_members:
            return False
        
        member.record_attendance(fitness_class.class_id, BookingStatus.ATTENDED)
        
        # Check attendance after recording
        self._attendance_monitor.check_attendance(member)
        
        return True
    
    def process_no_shows(self, fitness_class: FitnessClass) -> List[Member]:
        """
        Process no-shows after class time.
        Returns list of members who didn't check in.
        """
        no_shows = []
        for member in fitness_class.enrolled_members:
            # Check if member attended
            recent_attendance = [r for r in member._attendance_history 
                                 if r['class_id'] == fitness_class.class_id]
            if not recent_attendance or recent_attendance[-1]['status'] != BookingStatus.ATTENDED:
                member.record_attendance(fitness_class.class_id, BookingStatus.NO_SHOW)
                no_shows.append(member)
        return no_shows
    
    def get_member_schedule(self, member: Member, 
                            week_start: date = None) -> List[FitnessClass]:
        """Get a member's scheduled classes for a week."""
        if week_start is None:
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
        
        week_end = week_start + timedelta(days=7)
        
        return [c for c in member.booked_classes 
                if week_start <= c.schedule_time.date() < week_end]


# ============================================================================
# SECTION 9: MAIN DEMONSTRATION
# ============================================================================

def main():
    """
    Comprehensive demonstration of the FitZone Fitness Center Management System.
    
    Showcases:
    - Singleton pattern for registry
    - Trainer hierarchy (Junior, Senior, Master)
    - Fitness class types with specialization requirements
    - Member tiers with different privileges
    - Factory pattern for class creation
    - Booking system with business rule validation
    - Waitlist management with VIP priority
    - Strike system for late cancellations
    - Observer pattern for notifications
    - Legacy data adapter pattern
    - Exception handling and error cases
    """
    print("=" * 70)
    print("FitZone Fitness Center - System Demonstration")
    print("=" * 70)
    
    # ================================================================
    # 1. SINGLETON PATTERN VERIFICATION
    # ================================================================
    print("\n1. SINGLETON PATTERN VERIFICATION")
    print("-" * 70)
    reg1 = FitZoneRegistry()
    reg2 = FitZoneRegistry()
    print(f"   Same instance: {reg1 is reg2}")  # Should be True
    print("   ✓ FitZoneRegistry singleton verified")
    
    # ================================================================
    # 2. CREATE TRAINERS OF DIFFERENT LEVELS
    # ================================================================
    print("\n2. CREATING TRAINERS (Hierarchy)")
    print("-" * 70)
    
    junior_trainer = JuniorTrainer(
        "TR-001", "Alex Smith",
        ["CPT Level 1", "Basic First Aid"],
        ["Yoga"]
    )
    reg1.add_trainer(junior_trainer)
    print(f"   {junior_trainer}")
    print(f"      Max/day: {junior_trainer.max_classes_per_day}, "
          f"Rate: ${junior_trainer.hourly_rate}/hr")
    
    senior_trainer = SeniorTrainer(
        "TR-002", "Jordan Lee",
        ["CPT Level 2", "Nutrition Cert", "HIIT Cert"],
        ["HIIT", "Spinning", "Fitness Assessment"]
    )
    reg1.add_trainer(senior_trainer)
    print(f"   {senior_trainer}")
    print(f"      Max/day: {senior_trainer.max_classes_per_day}, "
          f"Rate: ${senior_trainer.hourly_rate}/hr")
    
    master_trainer = MasterTrainer(
        "TR-003", "Morgan Chen",
        ["Master CPT", "Nutrition", "Strength Athlete Cert", "Yoga Master"],
        ["HIIT", "Strength", "Yoga", "Spinning", "Advanced Training"]
    )
    reg1.add_trainer(master_trainer)
    print(f"   {master_trainer}")
    print(f"      Max/day: {master_trainer.max_classes_per_day}, "
          f"Rate: ${master_trainer.hourly_rate}/hr")
    print(f"      Can substitute: Yes")
    
    # ================================================================
    # 3. CREATE FITNESS CLASSES USING FACTORY
    # ================================================================
    print("\n3. FACTORY PATTERN - CREATING FITNESS CLASSES")
    print("-" * 70)
    factory = FitnessClassFactory()
    
    # Schedule times (today and tomorrow to be within booking windows)
    yoga_time = datetime(2026, 4, 2, 14, 0)  # Today 2pm
    hiit_time = datetime(2026, 4, 2, 15, 30)  # Today 3:30pm
    spinning_time = datetime(2026, 4, 2, 17, 0)  # Today 5pm
    strength_time = datetime(2026, 4, 3, 18, 0)  # Tomorrow 6pm
    
    yoga_class = factory.create_class(
        "yoga", "YG-001", "Morning Yoga Flow",
        junior_trainer, yoga_time
    )
    reg1.add_class(yoga_class)
    print(f"   {yoga_class}")
    
    hiit_class = factory.create_class(
        "hiit", "HI-001", "Intense HIIT Blast",
        senior_trainer, hiit_time
    )
    reg1.add_class(hiit_class)
    print(f"   {hiit_class}")
    
    spinning_class = factory.create_class(
        "spinning", "SP-001", "High Energy Spin",
        senior_trainer, spinning_time
    )
    reg1.add_class(spinning_class)
    print(f"   {spinning_class}")
    
    strength_class = factory.create_class(
        "strength", "ST-001", "Strength & Power",
        master_trainer, strength_time
    )
    reg1.add_class(strength_class)
    print(f"   {strength_class}")
    
    # ================================================================
    # 4. CREATE MEMBERS OF DIFFERENT TIERS
    # ================================================================
    print("\n4. MEMBER TIER SYSTEM")
    print("-" * 70)
    
    basic_member = BasicMember(
        "M-001", "Emma Thompson", "emma@email.com",
        date(2024, 1, 15)
    )
    basic_member.fitness_assessment_completed = True
    reg1.add_member(basic_member)
    print(f"   {basic_member}")
    print(f"      Fee: ${basic_member.monthly_fee}, "
          f"Limit: {basic_member.weekly_class_limit}/week, "
          f"Advance: {basic_member.booking_advance_hours}h")
    
    premium_member = PremiumMember(
        "M-002", "David Rodriguez", "david@email.com",
        date(2023, 6, 20)
    )
    premium_member.fitness_assessment_completed = True
    premium_member.safety_induction_completed = True
    reg1.add_member(premium_member)
    print(f"   {premium_member}")
    print(f"      Fee: ${premium_member.monthly_fee}, "
          f"Limit: {premium_member.weekly_class_limit}/week, "
          f"Advance: {premium_member.booking_advance_hours}h")
    
    vip_member = VIPMember(
        "M-003", "Sophie Wilson", "sophie@email.com",
        date(2023, 3, 10)
    )
    vip_member.fitness_assessment_completed = True
    vip_member.safety_induction_completed = True
    reg1.add_member(vip_member)
    print(f"   {vip_member}")
    print(f"      Fee: ${vip_member.monthly_fee}, "
          f"Limit: {'Unlimited' if vip_member.weekly_class_limit == 0 else vip_member.weekly_class_limit}/week, "
          f"Advance: {vip_member.booking_advance_hours}h")
    print(f"      Trainer discount: {int(vip_member.get_trainer_discount_rate() * 100)}%")
    
    # ================================================================
    # 5. BOOKING SYSTEM - SUCCESS CASES
    # ================================================================
    print("\n5. BOOKING SYSTEM - SUCCESSFUL BOOKINGS")
    print("-" * 70)
    
    service = BookingService(reg1)
    
    try:
        booking1 = service.book_class(basic_member, yoga_class)
        print(f"   ✓ {basic_member.name} booked {yoga_class.name}")
        print(f"     Booking ID: {booking1.booking_id}")
    except (BookingError, MemberError) as e:
        print(f"   ✗ Booking failed: {e}")
    
    try:
        booking2 = service.book_class(premium_member, hiit_class)
        print(f"   ✓ {premium_member.name} booked {hiit_class.name}")
    except (BookingError, MemberError) as e:
        print(f"   ✗ Booking failed: {e}")
    
    try:
        booking3 = service.book_class(vip_member, strength_class)
        print(f"   ✓ {vip_member.name} booked {strength_class.name}")
    except (BookingError, MemberError) as e:
        print(f"   ✗ Booking failed: {e}")
    
    # ================================================================
    # 6. BOOKING VALIDATION - ERROR CASES
    # ================================================================
    print("\n6. BOOKING VALIDATION - ERROR HANDLING")
    print("-" * 70)
    
    # Try to book restricted class (Basic can't access HIIT)
    try:
        booking_fail = service.book_class(basic_member, hiit_class)
        print(f"   ✓ Basic member booked HIIT")
    except MembershipAccessError as e:
        print(f"   ✗ Membership restriction: {e}")
    
    # Try to book without prerequisites (need fitness assessment for HIIT)
    basic_no_assess = BasicMember(
        "M-004", "New Member", "new@email.com",
        date.today()
    )
    reg1.add_member(basic_no_assess)
    try:
        booking_fail2 = service.book_class(basic_no_assess, yoga_class)
        print(f"   ✓ Booking succeeded")
    except PrerequisiteNotMetError as e:
        print(f"   ✗ Prerequisite error: {e}")
    
    # ================================================================
    # 7. WAITLIST MANAGEMENT WITH VIP PRIORITY
    # ================================================================
    print("\n7. WAITLIST MANAGEMENT - VIP PRIORITY")
    print("-" * 70)
    
    # Fill up spinning class
    print(f"   Spinning class capacity: {spinning_class.max_capacity}")
    for i in range(spinning_class.max_capacity - 1):
        temp_member = BasicMember(
            f"TEMP-{i}", f"Temp Member {i}", f"temp{i}@email.com",
            date.today()
        )
        reg1.add_member(temp_member)
        try:
            service.book_class(temp_member, spinning_class)
        except:
            pass
    
    print(f"   Current enrollment: {len(spinning_class.enrolled_members)}/{spinning_class.max_capacity}")
    
    # Add basic member to waitlist
    pos1 = service.join_waitlist(basic_member, spinning_class)
    print(f"   {basic_member.name} (Basic) added to waitlist - Position: {pos1}")
    
    # Add VIP to waitlist (should get priority)
    vip_member2 = VIPMember(
        "M-005", "VIP Priority", "vip2@email.com",
        date.today()
    )
    reg1.add_member(vip_member2)
    pos2 = service.join_waitlist(vip_member2, spinning_class)
    print(f"   {vip_member2.name} (VIP) added to waitlist - Position: {pos2}")
    print(f"   ✓ VIP gets priority positioning")
    
    # ================================================================
    # 8. CANCELLATION AND STRIKE SYSTEM
    # ================================================================
    print("\n8. CANCELLATION AND STRIKE SYSTEM")
    print("-" * 70)
    
    # Create a test member with some bookings
    test_member = PremiumMember(
        "M-006", "Strike Test", "strike@email.com",
        date.today()
    )
    test_member.fitness_assessment_completed = True
    test_member.safety_induction_completed = True
    reg1.add_member(test_member)
    
    # Add member to a late class
    late_yoga_time = datetime(2026, 4, 2, 19, 0)  # Class tonight at 7pm
    late_yoga = factory.create_class(
        "yoga", "YG-002", "Evening Yoga",
        junior_trainer, late_yoga_time
    )
    reg1.add_class(late_yoga)
    service.book_class(test_member, late_yoga)
    
    # Cancel within 2 hours (should add strike)
    cancel_time = datetime(2026, 4, 2, 18, 30)  # Cancel 30 mins before
    success = service.cancel_booking(test_member, late_yoga, cancel_time)
    print(f"   Cancellation 30 mins before class: {('✓ Success' if success else '✗ Failed')}")
    print(f"   Strikes: {test_member.strikes}")
    print(f"   Member status: {'SUSPENDED' if test_member.is_suspended() else 'Active'}")
    
    # ================================================================
    # 9. LEGACY DATA ADAPTER
    # ================================================================
    print("\n9. ADAPTER PATTERN - LEGACY DATA CONVERSION")
    print("-" * 70)
    
    adapter = LegacyMemberAdapter()
    
    legacy_data = {
        "mem_no": "M-LEGACY-001",
        "full_name": "Legacy Member",
        "contact_email": "legacy@email.com",
        "signup_date": "15/03/2024",  # DD/MM/YYYY
        "tier": "gold",  # Maps to VIP
        "assess_done": "Y",
        "safety_done": "N"
    }
    
    try:
        adapted_member = adapter.adapt(legacy_data)
        reg1.add_member(adapted_member)
        print(f"   ✓ Adapted legacy member: {adapted_member}")
        print(f"     Join date: {adapted_member.join_date}")
        print(f"     Fitness assessment: {adapted_member.fitness_assessment_completed}")
        print(f"     Safety induction: {adapted_member.safety_induction_completed}")
    except LegacyDataError as e:
        print(f"   ✗ Adaptation error: {e}")
    
    # ================================================================
    # 10. ADMINISTRATIVE SUMMARY
    # ================================================================
    print("\n10. ADMINISTRATIVE SUMMARY")
    print("-" * 70)
    
    all_classes = reg1.get_all_classes()
    all_trainers = reg1.get_all_trainers()
    all_members = reg1.get_all_members()
    
    print(f"   Total classes scheduled: {len(all_classes)}")
    print(f"   Total trainers: {len(all_trainers)}")
    print(f"   Total members: {len(all_members)}")
    
    print(f"\n   Class Utilization:")
    for cls in all_classes[:4]:  # Show first 4 regular classes
        utilization = len(cls.enrolled_members) / cls.max_capacity
        bar = "█" * int(utilization * 10) + "░" * (10 - int(utilization * 10))
        print(f"     {cls.name:20} {bar} "
              f"({len(cls.enrolled_members)}/{cls.max_capacity})")
    
    print(f"\n   Member Tier Distribution:")
    tier_counts = {}
    for member in all_members:
        tier = member.get_tier().value
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
    
    for tier, count in tier_counts.items():
        print(f"     {tier.title():10}: {count}")
    
    # ================================================================
    # SUMMARY
    # ================================================================
    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("  ✓ Singleton pattern (single registry instance)")
    print("  ✓ Trainer hierarchy (Junior, Senior, Master)")
    print("  ✓ Factory pattern (class creation by type)")
    print("  ✓ Booking system with comprehensive validation")
    print("  ✓ Member tier system with different privileges")
    print("  ✓ Waitlist management with VIP priority")
    print("  ✓ Strike system for late cancellations")
    print("  ✓ Observer pattern (notifications)")
    print("  ✓ Adapter pattern (legacy data conversion)")
    print("  ✓ Exception handling and error checking")
    print("=" * 70)


if __name__ == "__main__":
    main()
