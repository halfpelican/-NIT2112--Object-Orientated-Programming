# NIT2112 Practical Test: UniClub Student Club Management System

## 📋 Test Overview

| Item | Details |
|------|---------|
| **Duration** | 1 Hour |
| **Total Marks** | 100 |
| **AI Copilot Use** | **REQUIRED** (Must be documented) |

---

## ⚠️ Important Instructions

1. Read the entire specification before beginning to code
2. **You MUST use an AI Copilot** throughout this test — this is assessed
3. **Document your AI interactions** as you work (copy key prompts/responses)
4. Save your work frequently
5. Submit both your Python file AND reflection document

---

## 📚 Learning Outcomes Assessed

| LO | Description |
|----|-------------|
| **LO 2** | Utilise AI Copilots for OOP Development: Demonstrate a foundational understanding of AI and utilize it for code generation, debugging, and documenting during OOP development, adhering to best practices |
| **LO 3** | Solve Practical Problems Using OOP and AI: Apply OOP principles and AI copilots to design and implement well-structured, modular software solutions for real-world problems |
| **LO 4** | Optimize OOP Systems with AI: Apply critical thinking and AI copilots to effectively analyse and optimize OOP systems, including exception handling, resolving performance bottlenecks, and enhancing maintainability |

---

## 🎯 Scenario: UniClub Student Club Management System

You have been contracted by UniClub Services, a university department responsible for overseeing all registered student clubs. They need a Python system to help club executives manage their operations more effectively, ensuring proper procedures are followed for events and finances, while keeping track of member engagement.

### The Club Environment

University student clubs are dynamic entities involving:
- **Diverse Members**: Standard members and executive members with different roles
- **Various Activities**: Workshops, social gatherings, fundraisers, competitions
- **Limited Resources**: Shared venues, equipment, and constrained budgets
- **Governance Requirements**: Approval workflows and financial oversight

### Your Task

Design and implement an Object-Oriented club management system that models this environment, enforces governance rules, manages approval workflows, and demonstrates your understanding of OOP principles.

---

## 📋 Functional Requirements

### FR1: Member Hierarchy

Create a member class hierarchy to represent different roles within a club:

| Member Type | Additional Attributes | Permissions & Responsibilities |
|-------------|----------------------|-------------------------------|
| **Member** (Base) | `member_id`, `name`, `email`, `join_date` | Abstract — cannot be instantiated directly |
| **StandardMember** | `attendance_count`, `contributions` | Can attend events, propose events, view club info |
| **ExecutiveMember** (Base) | `term_start`, `term_end`, `is_active` | Abstract — base for executive roles |
| **President** | `veto_count` | Final event approval, can veto decisions, appoint roles |
| **Treasurer** | `approved_expenses` | Budget approval, expense tracking, financial reports |
| **Secretary** | `meetings_recorded` | Member records, meeting minutes, communications |
| **EventCoordinator** | `events_managed` | Event logistics, resource booking, attendance tracking |

**All members must:**
- Have a unique member ID within the club
- Support `get_role()` method returning their role name (polymorphic)
- Implement `get_permissions()` method listing their allowed actions
- Provide `display_info()` method showing member details

### FR2: Event Hierarchy & Lifecycle

Implement events with different types and a state-based lifecycle:

| Event Type | Additional Attributes | Special Rules |
|------------|----------------------|---------------|
| **Event** (Base) | `event_id`, `title`, `description`, `proposed_by`, `estimated_cost`, `status` | Abstract — cannot be instantiated directly |
| **Workshop** | `topic`, `instructor`, `materials_needed`, `max_participants` | Requires room booking; limited capacity |
| **SocialGathering** | `theme`, `catering_required`, `expected_attendance` | Catering costs scale with attendance |
| **Fundraiser** | `target_amount`, `actual_raised`, `fundraising_method` | Must project positive revenue |
| **Competition** | `competition_type`, `prizes`, `registration_fee` | Generates revenue from registrations |

**Event Status Lifecycle:**
```
PROPOSED → BUDGET_REVIEW → RESOURCE_CHECK → APPROVED → SCHEDULED → COMPLETED
                ↓              ↓                           ↓
            REJECTED      REJECTED                     CANCELLED
```

**Event Rules:**
- Only members can propose events
- Treasurer must approve budget for events with cost > $0
- President gives final approval
- Resource availability must be verified before scheduling
- Cancelled events after approval incur 10% cancellation fee

### FR3: Approval Workflow (State Pattern)

Implement a formal approval workflow using the **State Pattern**:

| Approval Stage | Approver | Criteria |
|----------------|----------|----------|
| **Budget Review** | Treasurer | Estimated cost ≤ available budget; cost is reasonable |
| **Resource Check** | EventCoordinator | Required resources are available for the date |
| **Final Approval** | President | Aligns with club goals; no policy conflicts |

**Workflow Rules:**
- Events must progress through stages in order
- Rejection at any stage stops the workflow with a reason
- Only designated executive roles can approve their respective stages
- Each approval must be logged with approver ID and timestamp

### FR4: Financial Management

Implement budget tracking with these rules:

| Requirement | Description |
|-------------|-------------|
| **Initial Budget** | Each club has a starting budget allocation |
| **Expense Tracking** | Approved event costs are reserved from budget |
| **Revenue Recording** | Fundraisers and competitions can add to budget |
| **Balance Inquiry** | Current available balance must be queryable |
| **Transaction History** | All financial changes must be logged |

**Financial Rules:**
- Cannot approve event if `estimated_cost > available_budget`
- Fundraiser events don't reserve budget (they generate revenue)
- Competitions reserve budget for prizes but may generate net positive
- Budget can have a small overdraft allowance for emergencies (set by Treasurer)

### FR5: Resource Management

Implement a simple resource coordination system:

| Resource Type | Attributes | Constraints |
|---------------|------------|-------------|
| **Venue** | `venue_id`, `name`, `capacity`, `has_av_equipment` | One booking per time slot |
| **Equipment** | `equipment_id`, `name`, `quantity_available` | Track available quantity |

**Resource Rules:**
- Events can request specific resources
- Resources have availability that can be checked for a date/time
- Double-booking a venue raises an exception
- Equipment requests cannot exceed available quantity

### FR6: Attendance Tracking (Observer Pattern)

Implement attendance tracking using the **Observer Pattern**:

- Members can register attendance at approved/scheduled events
- Events notify observers (e.g., `AttendanceTracker`, `EngagementAnalytics`) when attendance is recorded
- Track: member ID, event ID, check-in time, participation type (attendee/volunteer/organizer)
- Generate attendance reports per member and per event

### FR7: Club Factory (Factory Pattern)

Implement a Factory to create clubs with predefined structures:

```python
factory.create_club("academic", name="AI Research Society", budget=5000.0)
factory.create_club("social", name="International Students Club", budget=3000.0)
factory.create_club("sports", name="Tennis Club", budget=4000.0, equipment_budget=1500.0)
factory.create_club("cultural", name="Drama Society", budget=3500.0)
```

### FR8: Club Registry (Singleton Pattern)

Ensure only one `ClubRegistry` exists to maintain consistency:

```python
registry = ClubRegistry()
registry.register_club(club)
registry.get_club("AI Research Society")
registry.get_all_clubs()
registry.get_member_across_clubs(member_id)  # Members can join multiple clubs
```

---

## 🔧 Technical Requirements

Your solution **MUST** demonstrate the following OOP concepts:

| Concept | Requirement | Marks |
|---------|-------------|-------|
| **Encapsulation** | Use private/protected attributes with getters/setters or properties | 10 |
| **Inheritance** | Create meaningful class hierarchies (min. 3 levels for Members, 2 for Events) | 10 |
| **Polymorphism** | Override methods to provide role/type-specific behaviour | 10 |
| **Abstraction** | Use ABC with at least 2 abstract methods | 10 |
| **Interfaces** | Define at least 1 interface (e.g., `Approvable`, `Trackable`) | 5 |
| **Custom Exceptions** | Create exception hierarchy for error handling | 10 |
| **State Pattern** | Implement event approval workflow with state transitions | 10 |
| **Factory Pattern** | Implement club creation via factory | 5 |
| **Observer Pattern** | Implement attendance/notification system | 5 |
| **Singleton Pattern** | Ensure only one `ClubRegistry` exists | 5 |

---

## ⚠️ Custom Exceptions Required

Implement the following exception hierarchy:

```
ClubManagementError (base)
├── MemberError
│   ├── MemberNotFoundError
│   ├── DuplicateMemberError
│   └── PermissionDeniedError
├── EventError
│   ├── EventNotFoundError
│   ├── InvalidEventStateError
│   └── EventCapacityExceededError
├── FinancialError
│   ├── InsufficientFundsError
│   ├── BudgetExceededError
│   └── InvalidTransactionError
├── ResourceError
│   ├── ResourceNotAvailableError
│   ├── ResourceConflictError
│   └── ResourceNotFoundError
└── ApprovalError
    ├── ApprovalRequiredError
    ├── UnauthorizedApproverError
    └── ApprovalAlreadyProcessedError
```

---

## 🤖 AI Copilot Usage Requirements

### You MUST use your AI Copilot for:

1. **Design Exploration** — Ask about OOP design options and trade-offs
2. **Code Generation** — Generate boilerplate and method implementations
3. **Business Rules** — Implement approval workflows and permission checks
4. **Refactoring** — Improve code structure and clarity
5. **Documentation** — Generate docstrings and comments
6. **Debugging** — Identify and fix logical errors

### Good AI Copilot Usage Examples ✅

| Prompt Type | Example |
|-------------|---------|
| Design | "Should executive roles be separate classes or use composition with a Role object?" |
| Implementation | "Help me implement the State pattern for event approval workflow transitions" |
| Refactoring | "How can I refactor permission checking to avoid repeating code in each executive class?" |
| Debugging | "Why is my event state transition allowing PROPOSED to jump directly to APPROVED?" |

### Poor AI Copilot Usage Examples ❌

| Issue | Example |
|-------|---------|
| Wholesale delegation | "Write the entire club management system for me" |
| No critical thinking | Accepting generated code without understanding or testing it |
| No documentation | Using AI but not recording how it influenced your solution |
| Ignoring context | Pasting AI code that doesn't integrate with your existing design |

---

## 📝 Submission Requirements

### 1. Python Source Code (`club_management_system.py`)

- Complete implementation of all required classes
- Working demonstration in `main()` function
- Clear comments and docstrings

### 2. Reflection Document (PDF)

- **Design Rationale** (max 500 words): Explain your class design choices, how you modeled roles/permissions, and why you structured the approval workflow as you did
- **AI Interaction Log**: Document at least 5 significant AI interactions:
  - The prompt you used
  - Summary of AI's response
  - How you used/modified/rejected the suggestion and why

---

## ⏱️ Time Management Suggestion

| Phase | Time | Focus |
|-------|------|-------|
| **Read & Plan** | 10 min | Understand requirements, sketch class diagram |
| **Core Classes** | 20 min | Member hierarchy, Event hierarchy, basic Club |
| **Patterns & Logic** | 20 min | State pattern, Factory, approval workflow, budget |
| **Testing & Polish** | 10 min | Test scenarios, fix bugs, add documentation |

---

## 📊 Marking Rubric Summary

| Category | Excellent (90-100%) | Good (70-89%) | Satisfactory (50-69%) | Needs Improvement (<50%) |
|----------|---------------------|---------------|----------------------|--------------------------|
| **OOP Design** | Elegant hierarchy with clear role modeling; state pattern well implemented | Good structure with appropriate inheritance | Basic hierarchy, some design issues | Poor design or missing key concepts |
| **Business Logic** | Approval workflow correct; permissions properly enforced; budget rules work | Most rules work; minor edge cases missed | Core rules work; some errors | Major logic errors |
| **Exception Handling** | Comprehensive hierarchy; informative messages; used appropriately | Good coverage; meaningful messages | Basic exceptions; some gaps | Missing or incorrect |
| **Design Patterns** | All 4 patterns correctly implemented and justified | 3+ patterns working well | 2 patterns implemented | <2 patterns or incorrect |
| **AI Usage** | Strategic use; well-documented; critical evaluation shown | Good documentation; some critical analysis | Basic usage recorded | No documentation |

---

## 💻 Starter Code Template

```python
"""
NIT2112 Practical Test: UniClub Student Club Management System
Student Name: [Your Name]
Student ID: [Your ID]
Date: [Date]
AI Copilot Used: [Yes/No - Name of tool]
"""

from abc import ABC, abstractmethod
from enum import Enum, auto
from datetime import datetime, date
from typing import List, Dict, Optional, Set, Any


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


class TransactionType(Enum):
    """Types of financial transactions."""
    ALLOCATION = auto()
    EXPENSE = auto()
    REVENUE = auto()
    REFUND = auto()
    RESERVATION = auto()


# =============================================================================
# CUSTOM EXCEPTIONS
# =============================================================================

class ClubManagementError(Exception):
    """Base exception for all club management errors."""
    pass

# TODO: Implement the complete exception hierarchy as specified


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
    def approve(self, approver_id: str, stage: str) -> bool:
        """Approve the item at a specific stage."""
        pass
    
    @abstractmethod
    def reject(self, approver_id: str, reason: str) -> None:
        """Reject the item with a reason."""
        pass


class Trackable(ABC):
    """Interface for items that track attendance/participation."""
    
    @abstractmethod
    def record_attendance(self, member_id: str) -> None:
        """Record a member's attendance."""
        pass
    
    @abstractmethod
    def get_attendance_list(self) -> List[str]:
        """Get list of attendees."""
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
        pass
    
    @abstractmethod
    def remove_observer(self, observer: Observer) -> None:
        pass
    
    @abstractmethod
    def notify_observers(self, event_type: str, data: Dict[str, Any]) -> None:
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
    def can_transition_to(self, new_status: EventStatus) -> bool:
        """Check if transition to new status is allowed."""
        pass
    
    @abstractmethod
    def process_approval(self, event: 'Event', approver: 'ExecutiveMember') -> 'EventState':
        """Process approval and return new state."""
        pass


# TODO: Implement concrete state classes:
# - ProposedState
# - BudgetReviewState
# - ResourceCheckState
# - ApprovedState
# - ScheduledState
# - CompletedState
# - RejectedState
# - CancelledState


# =============================================================================
# MEMBER HIERARCHY
# =============================================================================

class Member(ABC):
    """Abstract base class for all club members."""
    
    def __init__(self, member_id: str, name: str, email: str):
        # TODO: Implement with encapsulation
        pass
    
    @property
    @abstractmethod
    def role(self) -> str:
        """Return the role name of this member."""
        pass
    
    @abstractmethod
    def get_permissions(self) -> Set[Permission]:
        """Return the set of permissions for this member."""
        pass
    
    @abstractmethod
    def display_info(self) -> str:
        """Return formatted member information."""
        pass


class StandardMember(Member):
    """Regular club member with basic permissions."""
    # TODO: Implement
    pass


class ExecutiveMember(Member):
    """Abstract base class for executive committee members."""
    # TODO: Implement
    pass


class President(ExecutiveMember):
    """Club President with final approval authority."""
    # TODO: Implement
    pass


class Treasurer(ExecutiveMember):
    """Club Treasurer with budget approval authority."""
    # TODO: Implement
    pass


class Secretary(ExecutiveMember):
    """Club Secretary managing records and communications."""
    # TODO: Implement
    pass


class EventCoordinator(ExecutiveMember):
    """Event Coordinator managing logistics and resources."""
    # TODO: Implement
    pass


# =============================================================================
# EVENT HIERARCHY
# =============================================================================

class Event(ABC, Approvable, Trackable, Observable):
    """Abstract base class for all events."""
    
    def __init__(
        self,
        event_id: str,
        title: str,
        description: str,
        proposed_by: str,
        estimated_cost: float
    ):
        # TODO: Implement with state pattern
        pass
    
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


class Workshop(Event):
    """Educational workshop event."""
    # TODO: Implement
    pass


class SocialGathering(Event):
    """Social event for member engagement."""
    # TODO: Implement
    pass


class Fundraiser(Event):
    """Fundraising event that generates revenue."""
    # TODO: Implement
    pass


class Competition(Event):
    """Competition event with prizes and registration fees."""
    # TODO: Implement
    pass


# =============================================================================
# FINANCIAL MANAGEMENT
# =============================================================================

class Transaction:
    """Represents a financial transaction."""
    # TODO: Implement
    pass


class Budget:
    """Manages club budget and transactions."""
    # TODO: Implement
    pass


# =============================================================================
# RESOURCE MANAGEMENT
# =============================================================================

class Resource(ABC):
    """Abstract base class for bookable resources."""
    # TODO: Implement
    pass


class Venue(Resource):
    """A bookable venue/room."""
    # TODO: Implement
    pass


class Equipment(Resource):
    """Bookable equipment with quantity tracking."""
    # TODO: Implement
    pass


class ResourceManager:
    """Manages resource availability and bookings."""
    # TODO: Implement
    pass


# =============================================================================
# CLUB CLASS
# =============================================================================

class Club:
    """Represents a student club with members, events, and budget."""
    # TODO: Implement
    pass


# =============================================================================
# FACTORY PATTERN
# =============================================================================

class ClubFactory:
    """Factory for creating clubs with predefined configurations."""
    
    @staticmethod
    def create_club(club_type: str, name: str, budget: float, **kwargs) -> Club:
        """
        Create a club of the specified type.
        
        Args:
            club_type: Type of club ('academic', 'social', 'sports', 'cultural')
            name: Name of the club
            budget: Initial budget allocation
            **kwargs: Additional configuration options
        
        Returns:
            Configured Club instance
        """
        # TODO: Implement
        pass


# =============================================================================
# SINGLETON PATTERN - Club Registry
# =============================================================================

class SingletonMeta(type):
    """Metaclass for implementing Singleton pattern."""
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class ClubRegistry(metaclass=SingletonMeta):
    """
    Singleton registry for all clubs.
    Ensures single source of truth for club data.
    """
    # TODO: Implement
    pass


# =============================================================================
# OBSERVER IMPLEMENTATIONS
# =============================================================================

class AttendanceTracker(Observer):
    """Tracks attendance across all events."""
    # TODO: Implement
    pass


class EngagementAnalytics(Observer):
    """Analyzes member engagement patterns."""
    # TODO: Implement
    pass


class NotificationService(Observer):
    """Sends notifications for club activities."""
    # TODO: Implement
    pass


# =============================================================================
# MAIN DEMONSTRATION
# =============================================================================

def main():
    """Demonstrate the Club Management System functionality."""
    
    print("=" * 60)
    print("   UNICLUB STUDENT CLUB MANAGEMENT SYSTEM")
    print("=" * 60)
    
    # TODO: Implement demonstration covering:
    # 1. Create clubs using Factory
    # 2. Add members with different roles
    # 3. Propose events
    # 4. Show approval workflow (State pattern)
    # 5. Demonstrate budget checks
    # 6. Show resource booking
    # 7. Record attendance (Observer pattern)
    # 8. Generate reports
    # 9. Handle exceptions appropriately
    
    print("\n[Implement your demonstration here]")


if __name__ == "__main__":
    main()
```

---

## 🎯 Key Test Scenarios to Implement

1. **Create a club** with executives and standard members
2. **Propose an event** and walk through the full approval workflow
3. **Reject an event** at budget review (insufficient funds)
4. **Approve an event** through all stages
5. **Handle resource conflict** when double-booking a venue
6. **Record attendance** and show observer notifications
7. **Generate financial report** showing transactions
8. **Demonstrate permission denied** when unauthorized member tries to approve

---

**Good luck! Remember to document your AI interactions and think critically about the suggestions you receive.**
