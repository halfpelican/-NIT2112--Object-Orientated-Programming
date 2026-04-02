# NIT2112 Object-Oriented Programming
## Practical Test: AutoDrive Vehicle Rental System

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

### Scenario: AutoDrive Vehicle Rental System

**AutoDrive** is a premium vehicle rental company operating a diverse fleet including economy cars, SUVs, luxury vehicles, and commercial vans. They need a comprehensive rental management system to handle their fleet, customer tiers, rental agreements, and damage claims.

The company offers different customer membership tiers (Standard, Silver, Gold, Platinum), each with varying rental rates, insurance options, and vehicle access privileges. They maintain strict eligibility requirements based on age and driving history for certain vehicle categories.

AutoDrive is also integrating data from a recently acquired rental company that uses a legacy system format.

Your task is to design and implement the core OOP architecture for this vehicle rental system.

---

### Functional Requirements

#### FR1: Vehicle Hierarchy (20 marks)

Design and implement an abstract base class `Vehicle` with the following concrete subclasses:

| Class | Daily Rate | Min Driver Age | Deposit | Fuel Type |
|-------|------------|----------------|---------|-----------|
| `EconomyCar` | $45 | 21 | $200 | Petrol |
| `SUV` | $85 | 25 | $400 | Petrol/Diesel |
| `LuxuryVehicle` | $180 | 25 | $1000 | Petrol |
| `CommercialVan` | $120 | 25 | $500 | Diesel |

**All Vehicles Must Have:**
- `vehicle_id` (string, unique identifier - registration plate)
- `make` (string, e.g., "Toyota")
- `model` (string, e.g., "Corolla")
- `year` (int)
- `mileage` (int, current odometer reading)
- `is_available` (bool)
- `condition` (Excellent/Good/Fair)
- `last_service_date` (date)

**Specific Attributes:**
- `EconomyCar`: `fuel_efficiency_kmpl` (km per litre), `has_gps` (bool)
- `SUV`: `is_4wd` (bool), `seating_capacity` (5 or 7), `towing_capacity_kg`
- `LuxuryVehicle`: `brand_tier` (Premium/Ultra), `features` (list: leather, sunroof, etc.)
- `CommercialVan`: `cargo_capacity_m3`, `has_refrigeration` (bool), `max_payload_kg`

**Required Interfaces (ABC):**
- `Rentable`: Abstract methods `calculate_rental_cost(days, customer)`, `get_insurance_options()`
- `Serviceable`: Abstract methods `needs_service()`, `get_next_service_date()`

**Business Rules:**
- Vehicles with mileage > 150,000 km cannot be rented to Standard customers
- `LuxuryVehicle` with `brand_tier="Ultra"` requires Gold or Platinum membership
- Vehicles needing service (>10,000 km since last service) cannot be rented
- `CommercialVan` requires customer to have commercial driving endorsement
- Vehicles in "Fair" condition get 10% rate discount

---

#### FR2: Customer Hierarchy (15 marks)

Design a `Customer` base class with the following subclasses:

| Class | Discount | Free Upgrades | Priority Booking | Mileage Limit/Day |
|-------|----------|---------------|------------------|-------------------|
| `StandardCustomer` | 0% | None | No | 200 km |
| `SilverCustomer` | 5% | Economy→SUV | 24hr advance | 350 km |
| `GoldCustomer` | 10% | Any one tier | 72hr advance | 500 km |
| `PlatinumCustomer` | 15% | Any two tiers | 7 days advance | Unlimited |

**All Customers Must Have:**
- `customer_id` (string, unique)
- `name` (string)
- `email` (string)
- `date_of_birth` (date)
- `license_number` (string)
- `license_expiry` (date)
- `has_commercial_endorsement` (bool)
- `rental_history` (list of past rentals)
- `loyalty_points` (int)
- `active_rental` (current Rental, if any)

**Business Rules:**
- Minimum age 21 for any rental, 25 for SUV/Luxury/Commercial
- License must not be expired
- Customers with accident claims in last 12 months cannot rent LuxuryVehicle
- Earn 1 loyalty point per $10 spent; 100 points = free rental day
- Platinum customers get complimentary roadside assistance

---

#### FR3: Custom Exception Hierarchy (10 marks)

Implement a domain-specific exception hierarchy:

```
AutoDriveError (base)
├── VehicleError
│   ├── VehicleNotFoundError
│   ├── VehicleUnavailableError
│   └── VehicleServiceRequiredError
├── CustomerError
│   ├── CustomerNotFoundError
│   ├── AgeRestrictionError
│   ├── LicenseExpiredError
│   └── EligibilityError
├── RentalError
│   ├── RentalNotFoundError
│   ├── MileageLimitExceededError
│   ├── InvalidReturnError
│   └── InsuranceRequiredError
└── IntegrationError
    └── LegacyDataFormatError
```

Each exception should include meaningful error messages with relevant context.

---

#### FR4: Design Patterns (25 marks)

Implement the following design patterns:

##### Factory Pattern (7 marks)
Create a `VehicleFactory` that:
- Creates appropriate vehicle subclass based on a `vehicle_type` parameter ("economy", "suv", "luxury", "commercial")
- Validates registration plate format (e.g., "ABC-123")
- Validates year is within acceptable range (2018-current)
- Raises appropriate exceptions for invalid parameters

##### Adapter Pattern (6 marks)
The legacy rental company system exports vehicle data in this format:
```python
legacy_vehicle = {
    "reg": "XYZ789",
    "car_make": "BMW",
    "car_model": "X5",
    "manufacture_year": 2022,
    "km_reading": 45000,
    "type_code": "S",  # E=Economy, S=SUV, L=Luxury, C=Commercial
    "ready": True,
    "cond": 2,  # 1=Excellent, 2=Good, 3=Fair
    "last_svc": "2024-01-15"  # YYYY-MM-DD string
}
```

Create a `LegacyVehicleAdapter` that converts this format to your modern `Vehicle` objects.

##### Observer Pattern (6 marks)
Implement a notification system where:
- When a popular vehicle becomes available, customers on the waitlist are notified (FIFO)
- When a rental is overdue, management receives an alert
- When a vehicle reaches service threshold, the maintenance team is notified
- When a customer accumulates 100 loyalty points, they receive a notification

##### Singleton Pattern (6 marks)
Create a `FleetRegistry` singleton (using metaclass) that:
- Maintains the central inventory of all vehicles
- Maintains the customer directory
- Tracks all active and completed rentals
- Ensures fleet-wide consistency for availability checks

---

#### FR5: Rental Management System (20 marks)

Implement the core rental functionality:

**Methods Required:**
- `create_rental(customer: Customer, vehicle: Vehicle, start_date: date, end_date: date, insurance_type: str) -> Rental`
- `return_vehicle(rental: Rental, return_date: date, final_mileage: int) -> Invoice`
- `extend_rental(rental: Rental, new_end_date: date) -> float` (returns additional cost)
- `apply_damage_claim(rental: Rental, damage_amount: float) -> None`
- `calculate_total_cost(rental: Rental) -> float`

**Rental Class:**
- `rental_id` (auto-generated)
- `customer` (Customer)
- `vehicle` (Vehicle)
- `start_date` (date)
- `end_date` (date)
- `actual_return_date` (date, optional)
- `start_mileage` (int)
- `end_mileage` (int, optional)
- `insurance_type` (Basic/Standard/Premium)
- `status` (Reserved/Active/Completed/Overdue)
- `total_cost` (float)
- `damage_claim` (float, default 0)

**Insurance Types:**
| Type | Daily Cost | Excess | Coverage |
|------|------------|--------|----------|
| Basic | $15 | $2000 | Third-party only |
| Standard | $30 | $500 | Comprehensive |
| Premium | $50 | $0 | Full coverage + roadside |

**Business Rules:**
- Insurance is mandatory (at least Basic)
- `LuxuryVehicle` requires minimum Standard insurance
- Early return: no refund for unused days
- Late return: 150% of daily rate for each extra day
- Mileage exceeded: $0.25 per km over limit
- Damage claims deducted from deposit first, then charged to customer

---

#### FR6: Waitlist and Availability System (10 marks)

Implement a waitlist system for popular vehicles:

**Methods Required:**
- `join_waitlist(customer: Customer, vehicle_type: str, preferred_dates: tuple) -> int` (returns position)
- `leave_waitlist(customer: Customer, vehicle_type: str) -> bool`
- `check_availability(vehicle_type: str, start_date: date, end_date: date) -> List[Vehicle]`
- `process_return(vehicle: Vehicle) -> Optional[Customer]` (notifies next in waitlist)

**Business Rules:**
- Platinum customers get priority in waitlist (jump to front)
- Waitlist entries expire after 7 days
- Customers cannot be on waitlist for multiple vehicle types simultaneously
- When vehicle returned, next customer has 24 hours to confirm booking

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
- Single file: `vehicle_rental.py`
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
Practical Test: AutoDrive Vehicle Rental System

Student Name: ________________________
Student ID:  ________________________
Date:        ________________________

AI Tools Used: ________________________

Declaration: I declare that this is my own work. I have used AI tools as a
development assistant and have documented my interactions. I can explain 
any part of my code and design decisions.
"""

from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Tuple, Callable
from enum import Enum
import uuid
import re


# ============================================================================
# SECTION 1: ENUMS AND CONSTANTS
# ============================================================================

class VehicleCondition(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"


class RentalStatus(Enum):
    RESERVED = "reserved"
    ACTIVE = "active"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class InsuranceType(Enum):
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"


# ============================================================================
# SECTION 2: CUSTOM EXCEPTIONS
# ============================================================================

class AutoDriveError(Exception):
    """Base exception for all AutoDrive-related errors."""
    pass

# TODO: Implement complete exception hierarchy (FR3)


# ============================================================================
# SECTION 3: INTERFACES (Abstract Base Classes)
# ============================================================================

class Rentable(ABC):
    """Interface for rentable assets."""
    
    @abstractmethod
    def calculate_rental_cost(self, days: int, customer: 'Customer') -> float:
        """Calculate total rental cost for given days and customer."""
        pass
    
    @abstractmethod
    def get_insurance_options(self) -> List[InsuranceType]:
        """Get available insurance options for this vehicle."""
        pass


class Serviceable(ABC):
    """Interface for serviceable vehicles."""
    
    @abstractmethod
    def needs_service(self) -> bool:
        """Check if vehicle needs service."""
        pass
    
    @abstractmethod
    def get_next_service_date(self) -> date:
        """Get the next recommended service date."""
        pass


# ============================================================================
# SECTION 4: VEHICLE HIERARCHY
# ============================================================================

class Vehicle(ABC, Rentable, Serviceable):
    """Abstract base class for all vehicles."""
    
    SERVICE_INTERVAL_KM = 10000
    
    def __init__(self, vehicle_id: str, make: str, model: str,
                 year: int, mileage: int, condition: VehicleCondition,
                 last_service_date: date):
        # TODO: Implement with proper encapsulation
        pass

# TODO: Implement EconomyCar, SUV, LuxuryVehicle, CommercialVan (FR1)


# ============================================================================
# SECTION 5: CUSTOMER HIERARCHY
# ============================================================================

class Customer(ABC):
    """Abstract base class for customers."""
    
    def __init__(self, customer_id: str, name: str, email: str,
                 date_of_birth: date, license_number: str,
                 license_expiry: date):
        # TODO: Implement with proper encapsulation
        pass

# TODO: Implement StandardCustomer, SilverCustomer, GoldCustomer, 
#       PlatinumCustomer (FR2)


# ============================================================================
# SECTION 6: DESIGN PATTERNS
# ============================================================================

# --- Singleton Pattern ---
class RegistryMeta(type):
    """Metaclass for implementing Singleton pattern."""
    _instances: Dict[type, object] = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

# TODO: Implement FleetRegistry using RegistryMeta (FR4)


# --- Factory Pattern ---
# TODO: Implement VehicleFactory (FR4)


# --- Adapter Pattern ---
# TODO: Implement LegacyVehicleAdapter (FR4)


# --- Observer Pattern ---
# TODO: Implement notification system (FR4)


# ============================================================================
# SECTION 7: RENTAL MANAGEMENT
# ============================================================================

class Rental:
    """Represents a vehicle rental agreement."""
    
    def __init__(self, customer: Customer, vehicle: Vehicle,
                 start_date: date, end_date: date, 
                 insurance_type: InsuranceType):
        # TODO: Implement
        pass


class Invoice:
    """Represents a rental invoice."""
    
    def __init__(self, rental: Rental):
        # TODO: Implement
        pass


class RentalService:
    """Manages all rental operations."""
    
    def __init__(self, registry: 'FleetRegistry'):
        # TODO: Implement
        pass

# TODO: Implement rental methods (FR5)


# ============================================================================
# SECTION 8: WAITLIST SYSTEM
# ============================================================================

# TODO: Implement waitlist system (FR6)


# ============================================================================
# SECTION 9: MAIN DEMONSTRATION
# ============================================================================

def main():
    """Demonstrate the vehicle rental system."""
    print("=" * 60)
    print("AutoDrive Vehicle Rental System - Demonstration")
    print("=" * 60)
    
    # TODO: Demonstrate:
    # 1. Singleton verification
    # 2. Creating vehicles using factory
    # 3. Creating customers of different tiers
    # 4. Rental process with eligibility checks
    # 5. Cost calculation with discounts
    # 6. Late return penalties
    # 7. Mileage limit enforcement
    # 8. Waitlist with priority
    # 9. Legacy vehicle adaptation
    # 10. Exception handling


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

1. **Start with Enums and Exceptions** - They're foundational and quick to implement.

2. **Vehicle Before Customer** - Rentals need both, but vehicles define the core business.

3. **Focus on Cost Calculations** - The polymorphic `calculate_rental_cost()` is critical.

4. **Use AI for Complex Rules** - Late fees, mileage penalties, and eligibility checks are good AI prompts.

5. **Test Edge Cases** - Age restrictions, license expiry, service requirements.

---

### Sample Test Scenarios

Test your implementation with these scenarios:

1. **Basic Rental**: StandardCustomer rents EconomyCar successfully
2. **Age Restriction**: 22-year-old tries to rent SUV (should fail - need 25+)
3. **Membership Upgrade**: GoldCustomer gets 10% discount on rental
4. **Late Return**: Vehicle returned 2 days late, verify 150% penalty
5. **Mileage Exceeded**: StandardCustomer exceeds 200km/day limit
6. **Service Check**: Vehicle with 160,000km needing service cannot be rented
7. **Waitlist Priority**: Fill SUV category, PlatinumCustomer joins waitlist and gets priority
8. **Legacy Conversion**: Convert legacy "S" type vehicle to modern SUV object

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
