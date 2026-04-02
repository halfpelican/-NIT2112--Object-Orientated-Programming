# NIT2112 Object-Oriented Programming
## Practical Test: BookHaven Library Management System

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

### Scenario: BookHaven Library Management System

**BookHaven Public Library** is modernising its library management system. The library handles a diverse collection including physical books, e-books, audiobooks, and academic journals. They need a robust, object-oriented system to manage their catalogue, membership types, borrowing transactions, and reservation queues.

The library has different membership tiers (Standard, Premium, Academic), each with different borrowing privileges. They also have a legacy catalogue system that exports data in an old format, which must be integrated with the new system.

Your task is to design and implement the core OOP architecture for this library management system.

---

### Functional Requirements

#### FR1: Catalogue Item Hierarchy (20 marks)

Design and implement an abstract base class `CatalogueItem` with the following concrete subclasses:

| Class | Description |
|-------|-------------|
| `PhysicalBook` | Traditional printed book with a physical location in the library |
| `EBook` | Digital book with download size and format (PDF, EPUB, MOBI) |
| `Audiobook` | Audio format with duration and narrator information |
| `AcademicJournal` | Scholarly publication with volume, issue, and impact factor |

**All Catalogue Items Must Have:**
- `item_id` (string, unique identifier)
- `title` (string)
- `author` (string)
- `publication_year` (int)
- `is_available` (bool)

**Specific Attributes:**
- `PhysicalBook`: `isbn`, `shelf_location`, `condition` (Excellent/Good/Fair/Poor)
- `EBook`: `file_format`, `file_size_mb`, `drm_protected` (bool)
- `Audiobook`: `narrator`, `duration_minutes`, `chapter_count`
- `AcademicJournal`: `journal_name`, `volume`, `issue`, `impact_factor`, `peer_reviewed` (bool)

**Required Interfaces (ABC):**
- `Borrowable`: Abstract method `calculate_loan_period()` → returns max loan days
- `Reservable`: Abstract method `get_reservation_priority()` → returns priority weight

**Business Rules:**
- `PhysicalBook` loan period: 21 days (14 days if condition is "Poor")
- `EBook` loan period: 14 days (instant return, license-based)
- `Audiobook` loan period: 14 days
- `AcademicJournal`: 7 days (non-renewable), priority weight = impact_factor × 10
- Items in "Poor" condition cannot be reserved

---

#### FR2: Member Hierarchy (15 marks)

Design a `Member` base class with the following subclasses:

| Class | Max Active Loans | Reservation Limit | Late Fee (per day) |
|-------|------------------|-------------------|-------------------|
| `StandardMember` | 5 | 2 | $0.50 |
| `PremiumMember` | 15 | 5 | $0.25 |
| `AcademicMember` | 25 | 10 | $0.00 (exempt) |

**All Members Must Have:**
- `member_id` (string, unique)
- `name` (string)
- `email` (string)
- `join_date` (date)
- `active_loans` (list of items currently borrowed)
- `outstanding_fines` (float)

**Business Rules:**
- Members with outstanding fines > $10.00 cannot borrow new items
- `AcademicMember` can only borrow `AcademicJournal` items if they are peer-reviewed
- `StandardMember` cannot borrow `AcademicJournal` items
- New members (joined within last 30 days) get a 10% fine discount

---

#### FR3: Custom Exception Hierarchy (10 marks)

Implement a domain-specific exception hierarchy:

```
LibraryError (base)
├── CatalogueError
│   ├── ItemNotFoundError
│   └── ItemUnavailableError
├── MemberError
│   ├── MemberNotFoundError
│   ├── LoanLimitExceededError
│   └── OutstandingFinesError
├── TransactionError
│   ├── InvalidReturnError
│   └── ReservationConflictError
└── IntegrationError
    └── LegacyDataFormatError
```

Each exception should include meaningful error messages and relevant context (e.g., member_id, item_id).

---

#### FR4: Design Patterns (25 marks)

Implement the following design patterns:

##### Factory Pattern (7 marks)
Create a `CatalogueItemFactory` that:
- Creates appropriate item subclass based on a `type` parameter ("physical", "ebook", "audiobook", "journal")
- Validates required parameters for each item type
- Raises `CatalogueError` if item type is unknown

##### Adapter Pattern (6 marks)
The legacy catalogue system exports data in this format:
```python
legacy_data = {
    "book_code": "LB-001",
    "book_title": "Design Patterns",
    "writer": "Gang of Four",
    "year_published": 1994,
    "book_type": "physical",
    "rack_position": "A-12-3",
    "book_condition": "good"
}
```

Create a `LegacyCatalogueAdapter` that converts this legacy format to your modern `CatalogueItem` objects.

##### Observer Pattern (6 marks)
Implement a notification system where:
- When a reserved item becomes available, all members on the waitlist are notified (FIFO order)
- When a member's fines exceed $10.00, the library administrator is notified
- Observers receive a notification message string

##### Singleton Pattern (6 marks)
Create a `LibraryRegistry` singleton (using metaclass) that:
- Maintains the central catalogue of all items
- Maintains the member directory
- Ensures data consistency across the application

---

#### FR5: Borrowing System (15 marks)

Implement the core borrowing functionality:

**Methods Required:**
- `borrow_item(member: Member, item: CatalogueItem) -> Transaction`
- `return_item(member: Member, item: CatalogueItem, return_date: date) -> float` (returns fine amount)
- `calculate_fine(member: Member, item: CatalogueItem, days_overdue: int) -> float`

**Transaction Class:**
- `transaction_id` (auto-generated)
- `member` (Member)
- `item` (CatalogueItem)
- `borrow_date` (date)
- `due_date` (date)
- `returned_date` (date, optional)
- `fine_amount` (float)

**Business Rules:**
- Cannot borrow if loan limit exceeded (raise `LoanLimitExceededError`)
- Cannot borrow if outstanding fines > $10.00 (raise `OutstandingFinesError`)
- Cannot borrow unavailable items (raise `ItemUnavailableError`)
- Fines calculated based on member type late fee rate
- Apply 10% new member discount to fines if applicable

---

#### FR6: Reservation Queue (15 marks)

Implement a reservation system with waitlist management:

**Methods Required:**
- `reserve_item(member: Member, item: CatalogueItem) -> int` (returns queue position)
- `cancel_reservation(member: Member, item: CatalogueItem) -> bool`
- `process_return(item: CatalogueItem) -> Optional[Member]` (returns next member in queue, or None)

**Business Rules:**
- Items in "Poor" condition cannot be reserved
- Members cannot reserve items they currently have on loan
- Reservation limit enforced per member type
- When item returned, notify next member in queue (Observer pattern)
- Reserved items held for 48 hours before releasing to next in queue

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
- Single file: `library_system.py`
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
Practical Test: BookHaven Library Management System

Student Name: ________________________
Student ID:  ________________________
Date:        ________________________

AI Tools Used: ________________________

Declaration: I declare that this is my own work. I have used AI tools as a
development assistant and have documented my interactions. I can explain 
any part of my code and design decisions.
"""

from abc import ABC, abstractmethod
from datetime import date, timedelta
from typing import List, Optional, Dict
import uuid


# ============================================================================
# SECTION 1: CUSTOM EXCEPTIONS
# ============================================================================

class LibraryError(Exception):
    """Base exception for all library-related errors."""
    pass

# TODO: Implement exception hierarchy (FR3)


# ============================================================================
# SECTION 2: INTERFACES (Abstract Base Classes)
# ============================================================================

class Borrowable(ABC):
    """Interface for items that can be borrowed."""
    
    @abstractmethod
    def calculate_loan_period(self) -> int:
        """Returns maximum loan period in days."""
        pass

# TODO: Implement Reservable interface


# ============================================================================
# SECTION 3: CATALOGUE ITEM HIERARCHY
# ============================================================================

class CatalogueItem(ABC, Borrowable):
    """Abstract base class for all catalogue items."""
    
    def __init__(self, item_id: str, title: str, author: str, 
                 publication_year: int):
        # TODO: Implement with proper encapsulation
        pass

# TODO: Implement PhysicalBook, EBook, Audiobook, AcademicJournal (FR1)


# ============================================================================
# SECTION 4: MEMBER HIERARCHY
# ============================================================================

class Member(ABC):
    """Abstract base class for library members."""
    
    def __init__(self, member_id: str, name: str, email: str, 
                 join_date: date):
        # TODO: Implement with proper encapsulation
        pass

# TODO: Implement StandardMember, PremiumMember, AcademicMember (FR2)


# ============================================================================
# SECTION 5: DESIGN PATTERNS
# ============================================================================

# --- Singleton Pattern ---
class RegistryMeta(type):
    """Metaclass for implementing Singleton pattern."""
    _instances: Dict[type, object] = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

# TODO: Implement LibraryRegistry using RegistryMeta (FR4)


# --- Factory Pattern ---
# TODO: Implement CatalogueItemFactory (FR4)


# --- Adapter Pattern ---
# TODO: Implement LegacyCatalogueAdapter (FR4)


# --- Observer Pattern ---
# TODO: Implement observer notification system (FR4)


# ============================================================================
# SECTION 6: TRANSACTION MANAGEMENT
# ============================================================================

class Transaction:
    """Represents a borrowing transaction."""
    
    def __init__(self, member: 'Member', item: 'CatalogueItem', 
                 borrow_date: date):
        # TODO: Implement
        pass

# TODO: Implement borrowing system methods (FR5)


# ============================================================================
# SECTION 7: RESERVATION SYSTEM
# ============================================================================

# TODO: Implement reservation queue with waitlist (FR6)


# ============================================================================
# SECTION 8: MAIN DEMONSTRATION
# ============================================================================

def main():
    """Demonstrate the library management system functionality."""
    print("=" * 60)
    print("BookHaven Library Management System - Demonstration")
    print("=" * 60)
    
    # TODO: Add demonstration code showing:
    # 1. Creating items using factory
    # 2. Creating members of different types
    # 3. Borrowing and returning items
    # 4. Fine calculation
    # 5. Reservation system
    # 6. Observer notifications
    # 7. Legacy data adaptation
    # 8. Exception handling


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

1. **Start with the Exception Hierarchy** - It's quick to implement and sets up error handling for everything else.

2. **Use AI Strategically** - Ask for:
   - Design pattern implementations
   - Complex business logic validation
   - Docstring generation
   - Debugging help

3. **Focus on Core Functionality First** - Get basic classes working before adding all business rules.

4. **Test Incrementally** - Add print statements or small test cases as you go.

5. **Don't Neglect the Reflection** - It's worth 5 marks and shows your understanding.

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
