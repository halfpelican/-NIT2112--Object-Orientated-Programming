# NIT2112 Object-Oriented Programming
## Practical Test: FitZone Fitness Center Management System

---

### Assessment Overview

| Item | Details |
|------|---------|
| **Assessment Type** | Practical Test (Open Book) |
| **Time Limit** | 1 Hour |
| **Total Marks** | 100 |
| **AI Copilot Usage** | Required |
| **Submission** | Python Source Code (.py) + Reflection Document (PDF) |

---

### Learning Outcomes Assessed

- **LO2:** Utilise AI Copilots for OOP Development
- **LO3:** Solve Practical Problems Using OOP and AI
- **LO4:** Optimize OOP Systems with AI

---

### Scenario: FitZone Fitness Center Management System

**FitZone** is a modern fitness center that offers a variety of fitness classes, personal training sessions, and gym equipment access. They need a comprehensive management system to handle their diverse membership tiers, class scheduling, equipment bookings, and trainer assignments.

The center operates with different membership levels (Basic, Premium, VIP), each with specific access rights and booking privileges. They also have specialized fitness classes (Yoga, HIIT, Spinning, Strength Training) that require different equipment and have varying capacity limits.

FitZone is transitioning from a legacy paper-based booking system and needs to integrate old member records into the new system.

Your task is to design and implement the core OOP architecture for this fitness center management system.

---

### Functional Requirements

#### FR1: Fitness Class Hierarchy (20 marks)

Design and implement an abstract base class `FitnessClass` with the following concrete subclasses:

| Class | Capacity | Duration | Equipment Required |
|-------|----------|----------|-------------------|
| `YogaClass` | 20 | 60 mins | Yoga mats, blocks |
| `HIITClass` | 15 | 45 mins | Dumbbells, kettlebells, jump ropes |
| `SpinningClass` | 25 | 50 mins | Spin bikes |
| `StrengthTraining` | 12 | 60 mins | Barbells, weight plates, benches |

**All Fitness Classes Must Have:**
- `class_id` (string, unique identifier)
- `name` (string)
- `instructor` (Trainer object)
- `schedule_time` (datetime)
- `duration_minutes` (int)
- `max_capacity` (int)
- `enrolled_members` (list of Members)
- `waitlist` (list of Members)

**Required Interfaces (ABC):**
- `Schedulable`: Abstract methods `get_time_slot()`, `check_conflicts(other_class)`
- `Bookable`: Abstract methods `can_enroll(member)`, `get_available_spots()`

**Business Rules:**
- `YogaClass`: All membership levels can attend; max 2 classes per member per day
- `HIITClass`: Premium and VIP only; requires fitness assessment completion
- `SpinningClass`: All levels; VIP members get priority booking (jump queue)
- `StrengthTraining`: Premium and VIP only; requires safety induction completion
- Classes cannot be scheduled within 30 minutes of each other in the same room
- Waitlist is processed FIFO, except VIP members move to front

---

#### FR2: Member Hierarchy (15 marks)

Design a `Member` base class with the following subclasses:

| Class | Monthly Fee | Class Limit/Week | Guest Passes/Month | Booking Advance |
|-------|-------------|------------------|-------------------|-----------------|
| `BasicMember` | $49 | 4 | 0 | 24 hours |
| `PremiumMember` | $89 | 12 | 2 | 72 hours |
| `VIPMember` | $149 | Unlimited | 4 | 7 days |

**All Members Must Have:**
- `member_id` (string, unique)
- `name` (string)
- `email` (string)
- `join_date` (date)
- `fitness_assessment_completed` (bool)
- `safety_induction_completed` (bool)
- `booked_classes` (list of FitnessClass)
- `attendance_history` (list of attendance records)

**Business Rules:**
- Members must complete fitness assessment before attending HIIT classes
- Members must complete safety induction before using Strength Training
- `BasicMember` cannot book more than 24 hours in advance
- `VIPMember` gets 15% discount on personal training sessions
- Members with attendance rate < 50% in last month receive a warning notification
- Cancellation within 2 hours of class time incurs a strike; 3 strikes = 1-week booking suspension

---

#### FR3: Trainer Hierarchy (10 marks)

Design a `Trainer` base class with the following subclasses:

| Class | Specializations | Max Classes/Day | Hourly Rate |
|-------|-----------------|-----------------|-------------|
| `JuniorTrainer` | 1 | 4 | $25 |
| `SeniorTrainer` | 3 | 6 | $45 |
| `MasterTrainer` | All | 8 | $75 |

**All Trainers Must Have:**
- `trainer_id` (string, unique)
- `name` (string)
- `certifications` (list of strings)
- `specializations` (list: "yoga", "hiit", "spinning", "strength")
- `assigned_classes` (list of FitnessClass)
- `availability` (dict of day -> time slots)

**Business Rules:**
- Trainers can only instruct classes within their specializations
- `MasterTrainer` can substitute for any trainer in emergencies
- Trainers cannot be double-booked (same time slot)
- Minimum 30-minute break required between consecutive classes

---

#### FR4: Custom Exception Hierarchy (10 marks)

Implement a domain-specific exception hierarchy:

```
FitZoneError (base)
├── BookingError
│   ├── ClassFullError
│   ├── ClassConflictError
│   ├── BookingLimitExceededError
│   └── AdvanceBookingError
├── MemberError
│   ├── MemberNotFoundError
│   ├── MemberSuspendedError
│   ├── PrerequisiteNotMetError
│   └── MembershipAccessError
├── TrainerError
│   ├── TrainerNotFoundError
│   ├── TrainerUnavailableError
│   └── SpecializationMismatchError
└── IntegrationError
    └── LegacyDataError
```

Each exception should include meaningful error messages with relevant context.

---

#### FR5: Design Patterns (25 marks)

Implement the following design patterns:

##### Factory Pattern (7 marks)
Create a `FitnessClassFactory` that:
- Creates appropriate class subclass based on a `class_type` parameter ("yoga", "hiit", "spinning", "strength")
- Validates instructor specialization matches class type
- Validates required equipment availability
- Raises `BookingError` if validation fails

##### Adapter Pattern (6 marks)
The legacy system exports member data in this format:
```python
legacy_record = {
    "mem_no": "M-1234",
    "full_name": "John Smith",
    "contact_email": "john@email.com",
    "signup_date": "15/03/2024",  # DD/MM/YYYY format
    "tier": "gold",  # bronze=Basic, silver=Premium, gold=VIP
    "assess_done": "Y",  # Y/N
    "safety_done": "N"
}
```

Create a `LegacyMemberAdapter` that converts this format to your modern `Member` objects.

##### Observer Pattern (6 marks)
Implement a notification system where:
- When a spot opens in a full class, waitlisted members are notified (FIFO, VIP priority)
- When a member's attendance drops below 50%, management receives an alert
- When a trainer becomes unavailable, affected class members are notified
- When equipment becomes unavailable, classes using it are flagged

##### Singleton Pattern (6 marks)
Create a `FitZoneRegistry` singleton (using metaclass) that:
- Maintains the central schedule of all classes
- Maintains trainer directory and availability
- Maintains member directory
- Ensures no scheduling conflicts across the system

---

#### FR6: Booking System (20 marks)

Implement the core booking functionality:

**Methods Required:**
- `book_class(member: Member, fitness_class: FitnessClass) -> Booking`
- `cancel_booking(member: Member, fitness_class: FitnessClass, cancel_time: datetime) -> bool`
- `join_waitlist(member: Member, fitness_class: FitnessClass) -> int` (returns position)
- `process_cancellation(fitness_class: FitnessClass) -> Optional[Member]` (promotes from waitlist)
- `check_in_member(member: Member, fitness_class: FitnessClass) -> bool`
- `get_member_schedule(member: Member, week_start: date) -> List[FitnessClass]`

**Booking Class:**
- `booking_id` (auto-generated)
- `member` (Member)
- `fitness_class` (FitnessClass)
- `booking_time` (datetime)
- `status` (Confirmed/Cancelled/Attended/NoShow)

**Business Rules:**
- Enforce class limits per week based on membership tier
- Enforce advance booking limits based on membership tier
- VIP members jump to front of waitlist
- Late cancellations (< 2 hours) add a strike to member record
- No-shows (didn't check in) count as strikes
- 3 strikes = 1-week booking suspension
- `MasterTrainer` can override any booking restriction for special circumstances

---

### Marking Rubric

| Criteria | Marks |
|----------|-------|
| **OOP Design & Architecture** | 20 |
| Logical class structure, appropriate abstractions, clear responsibilities | |
| **Encapsulation** | 10 |
| Appropriate use of private/protected attributes, properties, data hiding | |
| **Inheritance & Polymorphism** | 15 |
| Effective use of inheritance hierarchies, method overriding, polymorphic behavior | |
| **Abstraction & Interfaces** | 10 |
| Proper use of ABC, @abstractmethod, interface contracts | |
| **Custom Exceptions** | 10 |
| Complete hierarchy, meaningful messages, appropriate usage | |
| **Design Patterns** | 15 |
| Factory (4), Adapter (4), Observer (4), Singleton (3) | |
| **Code Quality** | 5 |
| Readability, naming conventions, type hints, docstrings | |
| **AI Copilot Usage** | 10 |
| Effective prompts, critical evaluation, documented interactions | |
| **Reflection Document** | 5 |
| Design rationale clarity, AI interaction log quality | |
| **TOTAL** | **100** |

---

### Submission Requirements

#### 1. Python Source Code
- Single file: `fitness_center.py`
- Include your student details in the header
- Code must be executable without errors
- Include a `main()` function demonstrating key functionality

#### 2. Reflection Document (PDF)

**Part A: Design Rationale (max 500 words)**
- Explain your class hierarchy choices
- Justify design pattern implementations
- Discuss trade-offs you considered
- Describe how you handled complex business rules

**Part B: AI Interaction Log**
Document at least 5 significant AI interactions:

| # | Purpose | Prompt Summary | AI Contribution | Your Modification/Evaluation |
|---|---------|----------------|-----------------|------------------------------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

---

### Starter Code Template

```python
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
from typing import List, Optional, Dict, Callable
from enum import Enum
import uuid


# ============================================================================
# SECTION 1: ENUMS AND CONSTANTS
# ============================================================================

class BookingStatus(Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    ATTENDED = "attended"
    NO_SHOW = "no_show"


class ClassType(Enum):
    YOGA = "yoga"
    HIIT = "hiit"
    SPINNING = "spinning"
    STRENGTH = "strength"


# ============================================================================
# SECTION 2: CUSTOM EXCEPTIONS
# ============================================================================

class FitZoneError(Exception):
    """Base exception for all FitZone-related errors."""
    pass

# TODO: Implement complete exception hierarchy (FR4)


# ============================================================================
# SECTION 3: INTERFACES (Abstract Base Classes)
# ============================================================================

class Schedulable(ABC):
    """Interface for schedulable activities."""
    
    @abstractmethod
    def get_time_slot(self) -> tuple:
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
        """Check if member can enroll."""
        pass
    
    @abstractmethod
    def get_available_spots(self) -> int:
        """Returns number of available spots."""
        pass


# ============================================================================
# SECTION 4: TRAINER HIERARCHY
# ============================================================================

class Trainer(ABC):
    """Abstract base class for fitness trainers."""
    
    def __init__(self, trainer_id: str, name: str, 
                 certifications: List[str]):
        # TODO: Implement with proper encapsulation
        pass

# TODO: Implement JuniorTrainer, SeniorTrainer, MasterTrainer (FR3)


# ============================================================================
# SECTION 5: FITNESS CLASS HIERARCHY
# ============================================================================

class FitnessClass(ABC, Schedulable, Bookable):
    """Abstract base class for all fitness classes."""
    
    def __init__(self, class_id: str, name: str, instructor: Trainer,
                 schedule_time: datetime, duration_minutes: int):
        # TODO: Implement with proper encapsulation
        pass

# TODO: Implement YogaClass, HIITClass, SpinningClass, StrengthTraining (FR1)


# ============================================================================
# SECTION 6: MEMBER HIERARCHY
# ============================================================================

class Member(ABC):
    """Abstract base class for fitness center members."""
    
    def __init__(self, member_id: str, name: str, email: str,
                 join_date: date):
        # TODO: Implement with proper encapsulation
        pass

# TODO: Implement BasicMember, PremiumMember, VIPMember (FR2)


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

# TODO: Implement FitZoneRegistry using RegistryMeta (FR5)


# --- Factory Pattern ---
# TODO: Implement FitnessClassFactory (FR5)


# --- Adapter Pattern ---
# TODO: Implement LegacyMemberAdapter (FR5)


# --- Observer Pattern ---
# TODO: Implement notification system (FR5)


# ============================================================================
# SECTION 8: BOOKING SYSTEM
# ============================================================================

class Booking:
    """Represents a class booking."""
    
    def __init__(self, member: Member, fitness_class: FitnessClass):
        # TODO: Implement
        pass


class BookingService:
    """Manages all booking operations."""
    
    def __init__(self, registry: 'FitZoneRegistry'):
        # TODO: Implement
        pass

# TODO: Implement booking methods (FR6)


# ============================================================================
# SECTION 9: MAIN DEMONSTRATION
# ============================================================================

def main():
    """Demonstrate the fitness center management system."""
    print("=" * 60)
    print("FitZone Fitness Center - System Demonstration")
    print("=" * 60)
    
    # TODO: Demonstrate:
    # 1. Singleton registry verification
    # 2. Creating trainers and classes using factory
    # 3. Creating members of different tiers
    # 4. Booking classes with business rule enforcement
    # 5. Waitlist management with VIP priority
    # 6. Cancellation and strike system
    # 7. Observer notifications
    # 8. Legacy member data adaptation
    # 9. Exception handling


if __name__ == "__main__":
    main()
```

---

### Recommended Time Allocation

| Phase | Duration | Activities |
|-------|----------|------------|
| **Analysis & Design** | 10 mins | Read requirements, sketch class diagram, consult AI on design |
| **Core Implementation** | 30 mins | Implement hierarchies, business logic, design patterns |
| **Testing & Refinement** | 15 mins | Test scenarios, fix bugs, add documentation |
| **Reflection Writing** | 5 mins | Complete design rationale and AI interaction log |

---

### Tips for Success

1. **Start with Exceptions and Enums** - They're quick and everything else depends on them.

2. **Build Trainers Before Classes** - Classes need a Trainer reference, so implement trainers first.

3. **Use AI for Complex Logic** - The waitlist with VIP priority and strike system are good AI prompts.

4. **Test Incrementally** - Don't wait until the end to test; verify each class works before moving on.

5. **Focus on Core Requirements** - Get basic booking working before perfecting edge cases.

---

### Sample Test Scenarios

Test your implementation with these scenarios:

1. **Basic Booking**: BasicMember books a YogaClass successfully
2. **Access Denied**: BasicMember tries to book HIITClass (should fail - Premium+ only)
3. **Prerequisite Check**: PremiumMember without fitness assessment tries HIIT (should fail)
4. **Waitlist with VIP Priority**: Full class, BasicMember joins waitlist, then VIPMember joins (VIP should be position 1)
5. **Strike System**: Member cancels within 2 hours, receives strike
6. **Legacy Adaptation**: Convert legacy "gold" tier member to VIPMember

---

### Academic Integrity Notice

⚠️ **Important:** While AI Copilot usage is required, you must:
- Understand every line of code you submit
- Be able to explain your design decisions
- Adapt AI suggestions to fit the specific requirements
- Critically evaluate AI output for correctness

Blindly copying AI-generated code without understanding is academic malpractice and will be investigated.

---

*End of Assessment Document*
