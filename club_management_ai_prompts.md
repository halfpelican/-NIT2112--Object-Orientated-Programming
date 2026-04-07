# AI Copilot Prompts for Student Club Management System

## Table of Contents
1. [Initial Design & Architecture](#1-initial-design--architecture)
2. [Exception Hierarchy](#2-exception-hierarchy)
3. [Interfaces & Abstract Base Classes](#3-interfaces--abstract-base-classes)
4. [State Pattern Implementation](#4-state-pattern-implementation)
5. [Member Hierarchy](#5-member-hierarchy)
6. [Event Hierarchy](#6-event-hierarchy)
7. [Financial Management](#7-financial-management)
8. [Resource Management](#8-resource-management)
9. [Club Class](#9-club-class)
10. [Design Patterns](#10-design-patterns)
11. [Observer Implementations](#11-observer-implementations)
12. [Main Demonstration](#12-main-demonstration)
13. [Debugging & Refactoring](#13-debugging--refactoring)
14. [Documentation](#14-documentation)

---

## 1. Initial Design & Architecture

### Prompt: Explore OOP Design Options
```
I need to design a Student Club Management System. The system must handle:
- Different types of members (standard members and executives like President, Treasurer)
- Event lifecycle with approval workflows (propose → budget review → resource check → final approval)
- Budget management with fund reservations and expenses
- Resource booking (venues, equipment)
- Attendance tracking

What OOP design approach would you recommend? Consider:
- Class hierarchies for members and events
- Design patterns that would be useful (State, Factory, Observer, Singleton)
- How to model the approval workflow
- Exception handling strategy
```

### Prompt: Define Core Enums
```
Create Python enums for a student club management system:
1. EventStatus - states for event lifecycle (PROPOSED, BUDGET_REVIEW, RESOURCE_CHECK, APPROVED, SCHEDULED, COMPLETED, REJECTED, CANCELLED)
2. Permission - member permissions (VIEW_CLUB_INFO, PROPOSE_EVENT, ATTEND_EVENT, APPROVE_BUDGET, etc.)
3. TransactionType - financial transaction types (ALLOCATION, EXPENSE, REVENUE, REFUND, RESERVATION)
4. ClubType - types of clubs (ACADEMIC, SOCIAL, SPORTS, CULTURAL)
5. ResourceType - bookable resources (VENUE, EQUIPMENT)

Use auto() for values and add docstrings explaining each enum's purpose.
```

### Prompt: Design Class Structure
```
Create a class diagram outline for a Club Management System with:

Classes needed:
- Member (ABC) → StandardMember, ExecutiveMember → President, Treasurer, Secretary, EventCoordinator
- Event (ABC) → Workshop, SocialGathering, Fundraiser, Competition
- Resource (ABC) → Venue, Equipment
- Club, Budget, ResourceManager, ClubRegistry

Interfaces:
- Approvable (submit_for_approval, approve, reject)
- Trackable (record_attendance, get_attendance_list)
- Observable (add_observer, notify_observers)

Show the relationships and key attributes for each class.
```

---

## 2. Exception Hierarchy

### Prompt: Create Custom Exception Hierarchy
```
Create a comprehensive custom exception hierarchy for a club management system. Base exception should be ClubManagementError with:
- message: str
- details: Optional[Dict]
- timestamp: datetime

Categories needed:
1. MemberError → MemberNotFoundError, DuplicateMemberError, PermissionDeniedError
2. EventError → EventNotFoundError, InvalidEventStateError, EventCapacityExceededError
3. FinancialError → InsufficientFundsError, BudgetExceededError, InvalidTransactionError
4. ResourceError → ResourceNotAvailableError, ResourceConflictError, ResourceNotFoundError
5. ApprovalError → ApprovalRequiredError, UnauthorizedApproverError, ApprovalAlreadyProcessedError

Each exception should store relevant context in the details dict.
```

### Prompt: Generate Exception with Context
```
Create a PermissionDeniedError exception class that:
- Inherits from MemberError
- Takes member_id, permission (Permission enum), and action (str) as parameters
- Stores all parameters in the details dict
- Generates a descriptive error message like "Permission denied: 'M001' lacks APPROVE_BUDGET for action 'approve event'"
```

### Prompt: Add Exception for Resource Conflicts
```
Create a ResourceConflictError exception that indicates when a resource is already booked:
- Inherits from ResourceError
- Takes resource_id, date, and existing_event as parameters
- Message format: "Conflict: Resource 'VEN001' already booked on 2024-06-15 for 'Annual Gala'"
- Include all context in details dict
```

---

## 3. Interfaces & Abstract Base Classes

### Prompt: Create Approvable Interface
```
Create an abstract base class (ABC) called Approvable that defines the interface for items requiring approval:
- submit_for_approval() → None: Submit item into approval workflow
- approve(approver: ExecutiveMember) → bool: Approve at current stage
- reject(approver: ExecutiveMember, reason: str) → None: Reject with reason
- get_approval_status() → Dict[str, Any]: Get current status and history

Use @abstractmethod decorators and add docstrings for each method.
```

### Prompt: Create Trackable Interface
```
Create a Trackable ABC interface for items that track attendance:
- record_attendance(member_id: str, role: str = "attendee") → None
- get_attendance_list() → List[Dict[str, Any]]
- get_attendance_count() → int

Include type hints and docstrings explaining each method's purpose.
```

### Prompt: Create Observer Pattern Interfaces
```
Create Observer and Observable abstract base classes for the Observer pattern:

Observer:
- update(event_type: str, data: Dict[str, Any]) → None

Observable:
- add_observer(observer: Observer) → None
- remove_observer(observer: Observer) → None
- notify_observers(event_type: str, data: Dict[str, Any]) → None

Both should be ABCs with @abstractmethod decorators.
```

---

## 4. State Pattern Implementation

### Prompt: Design State Pattern for Events
```
Implement the State Pattern for an event approval workflow with these states:
- PROPOSED → BUDGET_REVIEW → RESOURCE_CHECK → APPROVED → SCHEDULED → COMPLETED
- REJECTED (terminal state from any approval stage)
- CANCELLED (terminal state)

Create an EventState ABC with methods:
- get_status() → EventStatus
- get_required_approver_role() → Optional[str]
- can_transition_to(new_status: EventStatus) → bool
- process_approval(event, approver) → EventState
- process_rejection(event, approver, reason) → EventState

Then create concrete state classes for each state.
```

### Prompt: Create BudgetReviewState
```
Create a BudgetReviewState class implementing EventState:
- Returns EventStatus.BUDGET_REVIEW from get_status()
- Requires "Treasurer" role for approval
- Can transition to RESOURCE_CHECK (approved) or REJECTED (rejected)
- process_approval should verify approver is Treasurer, raise UnauthorizedApproverError if not
- On successful approval, return ResourceCheckState()
- On rejection, return RejectedState(reason)
```

### Prompt: Create Terminal States
```
Create CompletedState, RejectedState, and CancelledState classes:
- All are terminal states (can_transition_to returns False)
- process_approval and process_rejection should raise InvalidEventStateError
- RejectedState and CancelledState should store a reason
- CancelledState should also store cancellation_fee
- Add properties to access the stored reason/fee
```

---

## 5. Member Hierarchy

### Prompt: Create Member ABC
```
Create an abstract Member base class with:

Properties (with private backing fields):
- member_id: str
- name: str
- email: str
- join_date: date (set automatically)
- clubs: List[str] (returns copy to prevent modification)

Abstract methods:
- role: str (property)
- get_permissions() → Set[Permission]
- display_info() → str

Concrete methods:
- has_permission(permission: Permission) → bool
- join_club(club_name: str) → None
- leave_club(club_name: str) → None
- __str__() → formatted string with role and name
```

### Prompt: Create StandardMember Class
```
Create a StandardMember class extending Member:
- role property returns "StandardMember"
- Add _attendance_count and _contributions (list of event IDs)
- get_permissions returns {VIEW_CLUB_INFO, PROPOSE_EVENT, ATTEND_EVENT}
- Add increment_attendance() and add_contribution(event_id) methods
- display_info() shows name, ID, email, join date, attendance count, contributions
```

### Prompt: Create Executive Member Hierarchy
```
Create an ExecutiveMember abstract class extending Member, then create concrete classes:

ExecutiveMember:
- Add term_start, term_end dates and _is_active flag
- is_active property checks both flag and current date vs term_end
- deactivate() method
- Base permissions: VIEW_CLUB_INFO, PROPOSE_EVENT, ATTEND_EVENT, MANAGE_MEMBERS

President:
- role = "President"
- Additional permissions: FINAL_APPROVAL, VETO_DECISION, MANAGE_FINANCES
- Track veto_count and final_approvals list
- Methods: record_veto(), record_approval(event_id)

Treasurer:
- role = "Treasurer"
- Additional permissions: APPROVE_BUDGET, MANAGE_FINANCES
- Track approved_expenses as List[Tuple[str, float]]
- Property: total_approved_expenses
- Method: set_overdraft_allowance(amount), record_expense_approval(event_id, amount)

Secretary:
- role = "Secretary"
- Additional permission: RECORD_MINUTES
- Track meetings_recorded and communications_sent

EventCoordinator:
- role = "EventCoordinator"
- Additional permission: APPROVE_RESOURCES
- Track events_managed list
- Method: add_managed_event(event_id)
```

---

## 6. Event Hierarchy

### Prompt: Create Event ABC
```
Create an Event abstract base class that implements Approvable, Trackable, and Observable:

Constructor parameters:
- event_id, title, description, proposed_by, estimated_cost, event_date

Private attributes:
- _state: EventState (starts as ProposedState)
- _approval_history: List[ApprovalRecord]
- _attendance: List[AttendanceRecord]
- _observers: List[Observer]
- _required_resources: List[str]
- _created_at: datetime

Properties: event_id, title, description, proposed_by, estimated_cost, event_date, status, approval_history

Abstract properties/methods:
- event_type: str (property)
- calculate_total_cost() → float
- get_required_resources() → List[str]

Implement all interface methods (Approvable, Trackable, Observable).
Use the State Pattern for approve/reject - delegate to self._state.process_approval/rejection.
```

### Prompt: Create ApprovalRecord and AttendanceRecord Dataclasses
```
Create dataclasses for tracking approvals and attendance:

ApprovalRecord:
- stage: str
- approver_id: str
- approver_role: str
- action: str ("approved" or "rejected")
- timestamp: datetime
- notes: str = ""

AttendanceRecord:
- member_id: str
- check_in_time: datetime
- participation_type: str ("attendee", "volunteer", "organizer")
```

### Prompt: Create Workshop Event Class
```
Create a Workshop class extending Event:
- Additional attributes: topic, instructor, max_participants, _materials_needed list
- event_type returns "Workshop"
- calculate_total_cost() = estimated_cost + (materials count * $10)
- get_required_resources() returns base resources + ["venue"]
- Override record_attendance to check capacity before recording
- Add add_material(material: str) method
```

### Prompt: Create Fundraiser Event Class
```
Create a Fundraiser class extending Event that generates revenue:
- Additional: target_amount, _actual_raised, fundraising_method
- event_type = "Fundraiser"
- Properties: target_amount, actual_raised, net_revenue (raised - cost)
- Method: record_donation(amount) adds to _actual_raised
- calculate_total_cost() returns estimated_cost (minimal setup)
- get_required_resources() returns base resources only
```

### Prompt: Create Competition Event Class
```
Create a Competition class with registration fees:
- Additional: competition_type, prize_pool, registration_fee, _registrations count
- Properties: prize_pool, registration_revenue (registrations * fee), net_cost
- Method: register_participant(member_id) increments count and records attendance
- calculate_total_cost() = estimated_cost + prize_pool
- get_required_resources() returns resources + ["venue"]
```

---

## 7. Financial Management

### Prompt: Create Transaction Dataclass
```
Create a Transaction dataclass for financial records:
- transaction_id: str
- transaction_type: TransactionType enum
- amount: float
- description: str
- timestamp: datetime
- related_event: Optional[str] = None
- balance_after: float = 0.0
```

### Prompt: Create Budget Class
```
Create a Budget class for managing club finances:

Constructor:
- initial_allocation: float = 0.0
- overdraft_limit: float = 0.0

Private attributes:
- _balance: float
- _transactions: List[Transaction]
- _reserved: Dict[str, float] (event_id → reserved amount)
- _transaction_counter: int

Properties:
- balance, available_balance (balance - reserved), total_reserved, transactions

Methods:
- can_afford(amount) → bool (check against available + overdraft)
- reserve_funds(event_id, amount) → raise InsufficientFundsError if can't afford
- release_reservation(event_id) → float (returns amount released)
- spend(event_id, amount, description) → process expense, use reservation if exists
- add_revenue(amount, description, event_id=None)
- add_allocation(amount, description)
- apply_cancellation_fee(event_id, fee)
- get_financial_report() → formatted string

All transactions should be recorded using _record_transaction helper.
```

---

## 8. Resource Management

### Prompt: Create Booking Dataclass
```
Create a Booking dataclass:
- booking_id: str
- resource_id: str
- event_id: str
- booking_date: date
- booked_by: str
- created_at: datetime (default_factory=datetime.now)
```

### Prompt: Create Resource ABC
```
Create an abstract Resource base class:

Constructor: resource_id, name
Private: _bookings: Dict[date, Booking]

Properties:
- resource_id, name
- resource_type: ResourceType (abstract property)

Methods:
- is_available(booking_date: date) → bool
- book(event_id, booking_date, booked_by) → Booking (raise ResourceConflictError if not available)
- cancel_booking(booking_date) → None
- get_bookings() → List[Booking]
```

### Prompt: Create Venue Class
```
Create a Venue class extending Resource:
- Additional: capacity, has_av_equipment
- resource_type returns ResourceType.VENUE
- Properties: capacity, has_av_equipment
- __str__ shows name, capacity, and AV status
```

### Prompt: Create Equipment Class with Quantity
```
Create an Equipment class with quantity tracking:
- Additional: total_quantity, _quantity_bookings: Dict[date, int]
- resource_type returns ResourceType.EQUIPMENT
- available_quantity(date) → remaining quantity for date
- Override is_available(date, quantity=1) to check quantity
- book_quantity(event_id, date, booked_by, quantity) → Booking
  (raise ResourceNotAvailableError if insufficient quantity)
```

### Prompt: Create ResourceManager
```
Create a ResourceManager class to coordinate resources:
- _resources: Dict[str, Resource]

Methods:
- add_resource(resource) → None
- get_resource(resource_id) → Resource (raise ResourceNotFoundError if not found)
- check_availability(resource_ids, date) → Dict[str, bool]
- book_resources(resource_ids, event_id, date, booked_by) → List[Booking]
- cancel_bookings(event_id) → None (cancel all bookings for event)
- get_all_venues() → List[Venue]
- get_all_equipment() → List[Equipment]
```

---

## 9. Club Class

### Prompt: Create Club Class
```
Create a Club class implementing Observable:

Constructor:
- club_id, name, club_type: ClubType, initial_budget: float = 0.0

Private attributes:
- _budget: Budget
- _members: Dict[str, Member]
- _events: Dict[str, Event]
- _resource_manager: ResourceManager
- _observers: List[Observer]
- _president, _treasurer, _secretary, _event_coordinator: Optional executive references

Properties: club_id, name, club_type, budget, member_count, president, treasurer

Methods for member management:
- add_member(member) → auto-detect and store executive roles, notify observers
- get_member(member_id) → Member or raise MemberNotFoundError
- remove_member(member_id)
- get_all_members(), get_executives()

Methods for event management:
- propose_event(event, proposer_id) → check permission, attach observers
- get_event(event_id), get_all_events(), get_events_by_status(status)
- process_event_approval(event_id, approver_id, approve, reason="")
  - Handle budget check at BUDGET_REVIEW, reserve funds
  - Handle resource check at RESOURCE_CHECK
  - Delegate to event.approve/reject
- cancel_event(event_id, reason), complete_event(event_id, actual_cost=None)

Resource methods:
- add_resource(resource), book_resources_for_event(event_id, resource_ids)

Reports:
- get_club_report() → formatted string
```

---

## 10. Design Patterns

### Prompt: Create ClubFactory (Factory Pattern)
```
Create a ClubFactory class for creating pre-configured clubs:

Class method: create_club(club_type: str, name: str, budget: float, **kwargs) → Club

Behavior:
- Generate unique club_id using counter
- Map club_type string to ClubType enum
- Create Club with appropriate type and budget
- Add default resources based on type:
  - "academic": Lecture Hall venue with AV
  - "sports": Sports Hall, Sports Balls equipment, add equipment_budget from kwargs
  - "social": Common Room venue
  - "cultural": Theater with AV, Costume Sets equipment
- Return configured Club
```

### Prompt: Create Singleton ClubRegistry
```
Create a ClubRegistry using the Singleton pattern with a metaclass:

SingletonMeta (metaclass):
- _instances: Dict[type, Any]
- __call__ method returns existing instance or creates new one

ClubRegistry (uses SingletonMeta):
- _clubs: Dict[str, Club]
- _members: Dict[str, List[str]] (member tracking across clubs)
- _observers: List[Observer]

Methods:
- register_club(club) → add to registry, attach global observers
- get_club(name) → Club
- get_all_clubs() → List[Club]
- get_member_across_clubs(member_id) → Dict[str, Member]
- add_global_observer(observer) → add to all current and future clubs
- get_statistics() → Dict with totals (clubs, members, events, budget, by type)
```

---

## 11. Observer Implementations

### Prompt: Create AttendanceTracker Observer
```
Create an AttendanceTracker class implementing Observer:

Private:
- _attendance_records: List[Dict]
- _member_attendance: Dict[str, int] (member_id → count)

update(event_type, data):
- If event_type == "attendance_recorded":
  - Store record with timestamp
  - Increment member's attendance count
  - Print "📋 ATTENDANCE: {member_id} checked in to {event_id}"

Methods:
- get_member_attendance_count(member_id) → int
- get_attendance_report() → formatted string sorted by attendance count
```

### Prompt: Create NotificationService Observer
```
Create a NotificationService class implementing Observer:

update(event_type, data):
- Store notification with timestamp
- Print appropriate emoji and message based on event_type:
  - "event_proposed": "📧 NOTIFICATION: New event proposed..."
  - "event_approved": "✅ NOTIFICATION: Event approved at stage..."
  - "event_rejected": "❌ NOTIFICATION: Event rejected..."
  - "event_completed": "🎉 NOTIFICATION: Event completed!"
  - "member_added": "👋 NOTIFICATION: {name} joined as {role}"

Method: get_notifications() → List[Dict]
```

### Prompt: Create EngagementAnalytics Observer
```
Create an EngagementAnalytics class implementing Observer:

update(event_type, data):
- Log all events with timestamp
- If "event_completed": print analytics summary with attendance count

Method: get_event_count_by_type() → Dict[str, int]
```

---

## 12. Main Demonstration

### Prompt: Create Comprehensive main() Function
```
Create a main() function that demonstrates all OOP concepts:

1. Singleton Pattern: Create ClubRegistry twice, verify same instance
2. Factory Pattern: Create academic and sports clubs using ClubFactory
3. Member Hierarchy: Create all member types, show polymorphic permissions
4. State Pattern: Walk through complete event approval workflow
5. Financial Management: Show budget reservation and spending
6. Custom Exceptions: Demonstrate catching each exception type
7. Observer Pattern: Show attendance tracking and notifications
8. Registry Statistics: Display aggregate data

End with a summary of all OOP concepts demonstrated:
- Encapsulation, Inheritance, Polymorphism, Abstraction
- State, Factory, Observer, Singleton patterns
- Custom Exceptions

Use clear section headers and explanatory print statements.
```

---

## 13. Debugging & Refactoring

### Prompt: Fix MRO (Method Resolution Order) Error
```
I'm getting a TypeError: "Cannot create a consistent method resolution order (MRO)"
when my Event class inherits from multiple ABCs like:
class Event(ABC, Approvable, Trackable, Observable):

How do I fix this? The interfaces (Approvable, Trackable, Observable) already inherit from ABC.
```

**Solution:**
```python
# WRONG - causes MRO error
class Event(ABC, Approvable, Trackable, Observable):
    pass

# CORRECT - remove ABC since interfaces already inherit from it
class Event(Approvable, Trackable, Observable):
    pass
```

### Prompt: Debug State Transition
```
My event is stuck in PROPOSED state and won't transition to BUDGET_REVIEW.
The submit_for_approval() method doesn't seem to work.

Here's my code:
```python
event = Workshop(...)
club.propose_event(event, "M001")
event.submit_for_approval()
print(event.status)  # Still shows PROPOSED
```

What could be wrong?
```

### Prompt: Refactor Permission Checking
```
I have repetitive permission checking code scattered throughout my Club class.
Each method manually checks if member has permission:

```python
def approve_event(self, member_id, event_id):
    member = self.get_member(member_id)
    if not member.has_permission(Permission.APPROVE_BUDGET):
        raise PermissionDeniedError(...)
    # ... rest of method
```

How can I refactor this using a decorator pattern?
```

### Prompt: Optimize Financial Calculations
```
My Budget class recalculates total_reserved by summing the dict every time:

```python
@property
def total_reserved(self) -> float:
    return sum(self._reserved.values())  # O(n) every call
```

For a system with many reservations, how can I optimize this while keeping the data consistent?
```

---

## 14. Documentation

### Prompt: Generate Docstrings for Class
```
Generate comprehensive docstrings for this Club class including:
- Class docstring with description, attributes, and example usage
- Method docstrings with Args, Returns, Raises sections
- Use Google-style docstring format

Focus on the public interface: add_member, propose_event, process_event_approval, complete_event
```

### Prompt: Create Module Header Documentation
```
Generate a module-level docstring for the club_management_starter.py file that includes:
- Module description
- OOP concepts demonstrated (list each with brief explanation)
- Design patterns used
- Usage example
- Author and version information placeholders
```

### Prompt: Document Exception Handling Strategy
```
Create documentation explaining the custom exception hierarchy:
- Base exception and its attributes (message, details, timestamp)
- Category exceptions (MemberError, EventError, etc.)
- When to use each specific exception
- Best practices for catching and handling these exceptions
- Example try/except blocks showing proper exception handling
```

---

## Quick Reference: Most Useful Prompts

### For Starting the Project
1. "Explore OOP Design Options" - Get initial architecture guidance
2. "Define Core Enums" - Set up data types quickly
3. "Create Custom Exception Hierarchy" - Build error handling foundation

### For Core Implementation
4. "Design State Pattern for Events" - Implement approval workflow
5. "Create Member ABC" + "Create Executive Member Hierarchy" - Build member system
6. "Create Budget Class" - Handle financial management

### For Design Patterns
7. "Create ClubFactory (Factory Pattern)" - Club creation
8. "Create Singleton ClubRegistry" - Central registry
9. "Create Observer Pattern Interfaces" - Event notification

### For Debugging
10. "Fix MRO Error" - Common ABC inheritance issue
11. "Debug State Transition" - Workflow problems
12. "Optimize Financial Calculations" - Performance issues

### For Documentation
13. "Generate Docstrings for Class" - Add documentation
14. "Create Module Header Documentation" - Project overview

---

## Tips for Effective AI Copilot Usage

1. **Be Specific**: Include exact method signatures, return types, and exception types in your prompts

2. **Provide Context**: When debugging, include the relevant code snippet and error message

3. **Iterate**: Start with high-level design, then drill down into specific implementations

4. **Validate Output**: Always review generated code for correctness and adherence to your design

5. **Ask for Alternatives**: Request multiple approaches when making design decisions

6. **Document Interactions**: Keep a log of prompts and responses for your reflection document

7. **Combine Prompts**: Chain prompts together (e.g., "Create X, then show me how to test it")

8. **Request Tests**: Ask for unit test examples to verify your implementations
