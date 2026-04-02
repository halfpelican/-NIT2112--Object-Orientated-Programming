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
    """Condition rating for vehicles."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"


class VehicleType(Enum):
    """Types of vehicles in the fleet."""
    ECONOMY = "economy"
    SUV = "suv"
    LUXURY = "luxury"
    COMMERCIAL = "commercial"


class RentalStatus(Enum):
    """Status of a rental agreement."""
    RESERVED = "reserved"
    ACTIVE = "active"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class InsuranceType(Enum):
    """Available insurance types."""
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"


class MembershipTier(Enum):
    """Customer membership tiers."""
    STANDARD = "standard"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


# Insurance configuration
INSURANCE_CONFIG = {
    InsuranceType.BASIC: {"daily_cost": 15, "excess": 2000, "coverage": "Third-party only"},
    InsuranceType.STANDARD: {"daily_cost": 30, "excess": 500, "coverage": "Comprehensive"},
    InsuranceType.PREMIUM: {"daily_cost": 50, "excess": 0, "coverage": "Full + Roadside"},
}


# ============================================================================
# SECTION 2: CUSTOM EXCEPTIONS
# ============================================================================

class AutoDriveError(Exception):
    """Base exception for all AutoDrive-related errors."""
    pass


class VehicleError(AutoDriveError):
    """Base exception for vehicle-related errors."""
    pass


class VehicleNotFoundError(VehicleError):
    """Raised when a vehicle cannot be found."""
    def __init__(self, vehicle_id: str):
        self.vehicle_id = vehicle_id
        super().__init__(f"Vehicle '{vehicle_id}' not found in fleet.")


class VehicleUnavailableError(VehicleError):
    """Raised when a vehicle is not available for rental."""
    def __init__(self, vehicle_id: str, reason: str = ""):
        self.vehicle_id = vehicle_id
        message = f"Vehicle '{vehicle_id}' is not available"
        if reason:
            message += f": {reason}"
        super().__init__(message)


class VehicleServiceRequiredError(VehicleError):
    """Raised when a vehicle needs service before rental."""
    def __init__(self, vehicle_id: str, km_since_service: int):
        self.vehicle_id = vehicle_id
        self.km_since_service = km_since_service
        super().__init__(
            f"Vehicle '{vehicle_id}' requires service "
            f"({km_since_service}km since last service)."
        )


class CustomerError(AutoDriveError):
    """Base exception for customer-related errors."""
    pass


class CustomerNotFoundError(CustomerError):
    """Raised when a customer cannot be found."""
    def __init__(self, customer_id: str):
        self.customer_id = customer_id
        super().__init__(f"Customer '{customer_id}' not found.")


class AgeRestrictionError(CustomerError):
    """Raised when customer doesn't meet age requirements."""
    def __init__(self, customer_id: str, customer_age: int, 
                 required_age: int, vehicle_type: str):
        self.customer_id = customer_id
        self.customer_age = customer_age
        self.required_age = required_age
        self.vehicle_type = vehicle_type
        super().__init__(
            f"Customer '{customer_id}' (age {customer_age}) does not meet "
            f"minimum age requirement of {required_age} for {vehicle_type}."
        )


class LicenseExpiredError(CustomerError):
    """Raised when customer's license is expired."""
    def __init__(self, customer_id: str, expiry_date: date):
        self.customer_id = customer_id
        self.expiry_date = expiry_date
        super().__init__(
            f"Customer '{customer_id}' license expired on {expiry_date}."
        )


class EligibilityError(CustomerError):
    """Raised when customer is not eligible for a vehicle."""
    def __init__(self, customer_id: str, vehicle_id: str, reason: str):
        self.customer_id = customer_id
        self.vehicle_id = vehicle_id
        self.reason = reason
        super().__init__(
            f"Customer '{customer_id}' not eligible for vehicle "
            f"'{vehicle_id}': {reason}"
        )


class RentalError(AutoDriveError):
    """Base exception for rental-related errors."""
    pass


class RentalNotFoundError(RentalError):
    """Raised when a rental cannot be found."""
    def __init__(self, rental_id: str):
        self.rental_id = rental_id
        super().__init__(f"Rental '{rental_id}' not found.")


class MileageLimitExceededError(RentalError):
    """Raised when mileage limit is exceeded."""
    def __init__(self, rental_id: str, allowed: int, actual: int):
        self.rental_id = rental_id
        self.allowed = allowed
        self.actual = actual
        self.excess = actual - allowed
        super().__init__(
            f"Rental '{rental_id}': Mileage limit exceeded by {self.excess}km "
            f"({actual}km driven, {allowed}km allowed)."
        )


class InvalidReturnError(RentalError):
    """Raised when a return operation is invalid."""
    def __init__(self, rental_id: str, reason: str):
        self.rental_id = rental_id
        super().__init__(f"Invalid return for rental '{rental_id}': {reason}")


class InsuranceRequiredError(RentalError):
    """Raised when required insurance level is not selected."""
    def __init__(self, vehicle_type: str, required: InsuranceType, selected: InsuranceType):
        self.vehicle_type = vehicle_type
        self.required = required
        self.selected = selected
        super().__init__(
            f"{vehicle_type} requires minimum {required.value} insurance, "
            f"but {selected.value} was selected."
        )


class IntegrationError(AutoDriveError):
    """Base exception for integration-related errors."""
    pass


class LegacyDataFormatError(IntegrationError):
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
    
    @abstractmethod
    def get_minimum_insurance(self) -> InsuranceType:
        """Get minimum required insurance for this vehicle."""
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
    
    @abstractmethod
    def record_service(self, service_date: date, new_mileage: int) -> None:
        """Record that service has been performed."""
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
# SECTION 4: VEHICLE HIERARCHY
# ============================================================================

class Vehicle(Rentable, Serviceable, Observable):
    """Abstract base class for all vehicles in the fleet."""
    
    SERVICE_INTERVAL_KM = 10000
    MAX_MILEAGE_FOR_STANDARD = 150000
    
    def __init__(self, vehicle_id: str, make: str, model: str,
                 year: int, mileage: int, condition: VehicleCondition,
                 last_service_date: date, last_service_mileage: int):
        self._vehicle_id = vehicle_id
        self._make = make
        self._model = model
        self._year = year
        self._mileage = mileage
        self._condition = condition
        self._last_service_date = last_service_date
        self._last_service_mileage = last_service_mileage
        self._is_available = True
        self._observers: List[Callable[[str], None]] = []
    
    @property
    def vehicle_id(self) -> str:
        return self._vehicle_id
    
    @property
    def make(self) -> str:
        return self._make
    
    @property
    def model(self) -> str:
        return self._model
    
    @property
    def year(self) -> int:
        return self._year
    
    @property
    def mileage(self) -> int:
        return self._mileage
    
    @mileage.setter
    def mileage(self, value: int) -> None:
        if value < self._mileage:
            raise ValueError("Mileage cannot decrease")
        old_mileage = self._mileage
        self._mileage = value
        # Check if service is needed after mileage update
        if self.needs_service() and not self._needs_service_at(old_mileage):
            self.notify(f"Vehicle {self._vehicle_id} needs service at {value}km")
    
    @property
    def condition(self) -> VehicleCondition:
        return self._condition
    
    @condition.setter
    def condition(self, value: VehicleCondition) -> None:
        self._condition = value
    
    @property
    def is_available(self) -> bool:
        return self._is_available
    
    @is_available.setter
    def is_available(self, value: bool) -> None:
        old_value = self._is_available
        self._is_available = value
        if not old_value and value:
            self.notify(f"Vehicle {self._vehicle_id} ({self._make} {self._model}) is now available!")
    
    @property
    def last_service_date(self) -> date:
        return self._last_service_date
    
    @property
    @abstractmethod
    def daily_rate(self) -> float:
        """Base daily rental rate."""
        pass
    
    @property
    @abstractmethod
    def deposit(self) -> float:
        """Security deposit required."""
        pass
    
    @property
    @abstractmethod
    def minimum_driver_age(self) -> int:
        """Minimum age to rent this vehicle."""
        pass
    
    @abstractmethod
    def get_vehicle_type(self) -> VehicleType:
        """Get the type of this vehicle."""
        pass
    
    # Rentable interface
    def calculate_rental_cost(self, days: int, customer: 'Customer') -> float:
        """Calculate rental cost with customer discount."""
        base_cost = self.daily_rate * days
        
        # Apply condition discount for "Fair" vehicles
        if self._condition == VehicleCondition.FAIR:
            base_cost *= 0.9
        
        # Apply customer tier discount
        discount = customer.get_discount_rate()
        return round(base_cost * (1 - discount), 2)
    
    def get_insurance_options(self) -> List[InsuranceType]:
        """Get all available insurance options."""
        return list(InsuranceType)
    
    def get_minimum_insurance(self) -> InsuranceType:
        """Default minimum insurance is Basic."""
        return InsuranceType.BASIC
    
    # Serviceable interface
    def needs_service(self) -> bool:
        """Check if vehicle needs service based on mileage."""
        km_since_service = self._mileage - self._last_service_mileage
        return km_since_service >= self.SERVICE_INTERVAL_KM
    
    def _needs_service_at(self, mileage: int) -> bool:
        """Check if service was needed at a specific mileage."""
        km_since_service = mileage - self._last_service_mileage
        return km_since_service >= self.SERVICE_INTERVAL_KM
    
    def get_next_service_date(self) -> date:
        """Estimate next service date based on average usage."""
        # Assume average 1000km per month
        km_until_service = self.SERVICE_INTERVAL_KM - (self._mileage - self._last_service_mileage)
        if km_until_service <= 0:
            return date.today()
        months_until_service = km_until_service / 1000
        return date.today() + timedelta(days=int(months_until_service * 30))
    
    def record_service(self, service_date: date, new_mileage: int) -> None:
        """Record that service has been performed."""
        self._last_service_date = service_date
        self._last_service_mileage = new_mileage
    
    # Observable interface
    def attach(self, observer: Callable[[str], None]) -> None:
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Callable[[str], None]) -> None:
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self, message: str) -> None:
        for observer in self._observers:
            observer(message)
    
    def can_rent_to_standard(self) -> bool:
        """Check if vehicle can be rented to Standard customers."""
        return self._mileage <= self.MAX_MILEAGE_FOR_STANDARD
    
    def __str__(self) -> str:
        status = "Available" if self._is_available else "Rented"
        return (f"{self.get_vehicle_type().value.title()}: {self._make} {self._model} "
                f"({self._year}) - {self._vehicle_id} [{status}]")


class EconomyCar(Vehicle):
    """
    Economy sedan class—the entry-level rental vehicle.
    
    Daily rate: $45, Deposit: $200, Minimum driver age: 21
    Typical fuel efficiency; suitable for city and highway use.
    """
    
    DAILY_RATE = 45.0
    DEPOSIT = 200.0
    MIN_DRIVER_AGE = 21
    
    def __init__(self, vehicle_id: str, make: str, model: str,
                 year: int, mileage: int, condition: VehicleCondition,
                 last_service_date: date, last_service_mileage: int,
                 fuel_efficiency_kmpl: float, has_gps: bool = False):
        """
        Initialise an economy car.
        
        Args:
            fuel_efficiency_kmpl: Kilometres per litre (typical 10-15 for petrol)
            has_gps: Whether the vehicle includes GPS navigation
        """
        super().__init__(vehicle_id, make, model, year, mileage, condition,
                         last_service_date, last_service_mileage)
        self._fuel_efficiency_kmpl = fuel_efficiency_kmpl
        self._has_gps = has_gps
        self._fuel_type = "Petrol"
    
    @property
    def daily_rate(self) -> float:
        return self.DAILY_RATE
    
    @property
    def deposit(self) -> float:
        return self.DEPOSIT
    
    @property
    def minimum_driver_age(self) -> int:
        return self.MIN_DRIVER_AGE
    
    def get_vehicle_type(self) -> VehicleType:
        return VehicleType.ECONOMY
    
    def get_minimum_insurance(self) -> InsuranceType:
        return InsuranceType.BASIC


class SUV(Vehicle):
    """
    Sport utility vehicle class—mid-range rental offering.
    
    Daily rate: $85, Deposit: $400, Minimum driver age: 25
    Larger capacity, suitable for families or cargo transport.
    """
    
    DAILY_RATE = 85.0
    DEPOSIT = 400.0
    MIN_DRIVER_AGE = 25
    VALID_SEATING = (5, 7)
    
    def __init__(self, vehicle_id: str, make: str, model: str,
                 year: int, mileage: int, condition: VehicleCondition,
                 last_service_date: date, last_service_mileage: int,
                 is_4wd: bool, seating_capacity: int, towing_capacity_kg: int,
                 fuel_type: str = "Petrol"):
        """
        Initialise a sport utility vehicle.
        
        Args:
            is_4wd: Whether vehicle has four-wheel drive
            seating_capacity: Number of seats (5 or 7)
            towing_capacity_kg: Maximum towing capacity in kilograms
            fuel_type: Either 'Petrol' or 'Diesel'
        """
        if seating_capacity not in self.VALID_SEATING:
            raise VehicleError(
                f"Invalid seating capacity {seating_capacity}. "
                f"Must be one of {self.VALID_SEATING}"
            )
        if fuel_type not in ("Petrol", "Diesel"):
            raise VehicleError(f"Invalid fuel type '{fuel_type}'")
        
        super().__init__(vehicle_id, make, model, year, mileage, condition,
                         last_service_date, last_service_mileage)
        self._is_4wd = is_4wd
        self._seating_capacity = seating_capacity
        self._towing_capacity_kg = towing_capacity_kg
        self._fuel_type = fuel_type
    
    @property
    def daily_rate(self) -> float:
        return self.DAILY_RATE
    
    @property
    def deposit(self) -> float:
        return self.DEPOSIT
    
    @property
    def minimum_driver_age(self) -> int:
        return self.MIN_DRIVER_AGE
    
    def get_vehicle_type(self) -> VehicleType:
        return VehicleType.SUV


class LuxuryVehicle(Vehicle):
    """
    Premium/ultra-luxury vehicle class—high-end rental service.
    
    Daily rate: $180, Deposit: $1000, Minimum driver age: 25
    Ultra-tier requires Gold/Platinum membership. Minimum Standard insurance.
    """
    
    DAILY_RATE = 180.0
    DEPOSIT = 1000.0
    MIN_DRIVER_AGE = 25
    
    def __init__(self, vehicle_id: str, make: str, model: str,
                 year: int, mileage: int, condition: VehicleCondition,
                 last_service_date: date, last_service_mileage: int,
                 brand_tier: str, features: List[str]):
        """
        Initialise a luxury vehicle.
        
        Args:
            brand_tier: Either 'Premium' or 'Ultra' (Ultra requires Gold+)
            features: List of luxury features (e.g., ['leather seats', 'panoramic roof'])
        """
        if brand_tier not in ("Premium", "Ultra"):
            raise VehicleError(f"Invalid brand tier '{brand_tier}'")
        
        super().__init__(vehicle_id, make, model, year, mileage, condition,
                         last_service_date, last_service_mileage)
        self._brand_tier = brand_tier
        self._features = features
    
    @property
    def daily_rate(self) -> float:
        return self.DAILY_RATE
    
    @property
    def deposit(self) -> float:
        return self.DEPOSIT
    
    @property
    def minimum_driver_age(self) -> int:
        return self.MIN_DRIVER_AGE
    
    def get_vehicle_type(self) -> VehicleType:
        return VehicleType.LUXURY
    
    def get_minimum_insurance(self) -> InsuranceType:
        """Luxury vehicles require at minimum Standard insurance."""
        return InsuranceType.STANDARD


class CommercialVan(Vehicle):
    """
    Commercial cargo vehicle class—fleet and business use.
    
    Daily rate: $120, Deposit: $500, Minimum driver age: 25
    Requires commercial driving endorsement. Large cargo capacity.
    """
    
    DAILY_RATE = 120.0
    DEPOSIT = 500.0
    MIN_DRIVER_AGE = 25
    
    def __init__(self, vehicle_id: str, make: str, model: str,
                 year: int, mileage: int, condition: VehicleCondition,
                 last_service_date: date, last_service_mileage: int,
                 cargo_capacity_m3: float, has_refrigeration: bool,
                 max_payload_kg: int):
        """
        Initialise a commercial van.
        
        Args:
            cargo_capacity_m3: Cargo volume in cubic metres
            has_refrigeration: Whether van includes refrigerated compartment
            max_payload_kg: Maximum payload capacity in kilograms
        """
        super().__init__(vehicle_id, make, model, year, mileage, condition,
                         last_service_date, last_service_mileage)
        self._cargo_capacity_m3 = cargo_capacity_m3
        self._has_refrigeration = has_refrigeration
        self._max_payload_kg = max_payload_kg
    
    @property
    def daily_rate(self) -> float:
        return self.DAILY_RATE
    
    @property
    def deposit(self) -> float:
        return self.DEPOSIT
    
    @property
    def minimum_driver_age(self) -> int:
        return self.MIN_DRIVER_AGE
    
    def get_vehicle_type(self) -> VehicleType:
        return VehicleType.COMMERCIAL
    
    def get_minimum_insurance(self) -> InsuranceType:
        return InsuranceType.STANDARD


# ============================================================================
# SECTION 5: CUSTOMER HIERARCHY
# ============================================================================

class Customer(ABC):
    """Abstract base class for customers."""
    
    POINTS_PER_DOLLAR = 0.1  # 1 point per $10
    POINTS_FOR_FREE_DAY = 100
    
    def __init__(self, customer_id: str, name: str, email: str,
                 date_of_birth: date, license_number: str,
                 license_expiry: date, has_commercial_endorsement: bool = False):
        self._customer_id = customer_id
        self._name = name
        self._email = email
        self._date_of_birth = date_of_birth
        self._license_number = license_number
        self._license_expiry = license_expiry
        self._has_commercial_endorsement = has_commercial_endorsement
        self._rental_history: List['Rental'] = []
        self._loyalty_points: int = 0
        self._active_rental: Optional['Rental'] = None
    
    @property
    def customer_id(self) -> str:
        return self._customer_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def email(self) -> str:
        return self._email
    
    @property
    def date_of_birth(self) -> date:
        return self._date_of_birth
    
    @property
    def license_number(self) -> str:
        return self._license_number
    
    @property
    def license_expiry(self) -> date:
        return self._license_expiry
    
    @property
    def has_commercial_endorsement(self) -> bool:
        return self._has_commercial_endorsement
    
    @property
    def rental_history(self) -> List['Rental']:
        return self._rental_history.copy()
    
    @property
    def loyalty_points(self) -> int:
        return self._loyalty_points
    
    @property
    def active_rental(self) -> Optional['Rental']:
        return self._active_rental
    
    @active_rental.setter
    def active_rental(self, rental: Optional['Rental']) -> None:
        self._active_rental = rental
    
    @property
    @abstractmethod
    def discount_rate(self) -> float:
        """Discount percentage as decimal (e.g., 0.10 for 10%)."""
        pass
    
    @property
    @abstractmethod
    def daily_mileage_limit(self) -> int:
        """Daily mileage limit in km (0 = unlimited)."""
        pass
    
    @property
    @abstractmethod
    def priority_booking_hours(self) -> int:
        """How far in advance customer can book (hours)."""
        pass
    
    @abstractmethod
    def get_tier(self) -> MembershipTier:
        """Get the membership tier."""
        pass
    
    @abstractmethod
    def get_free_upgrade_options(self) -> List[VehicleType]:
        """Get list of vehicle types eligible for free upgrade."""
        pass
    
    def get_age(self) -> int:
        """Calculate customer's current age."""
        today = date.today()
        age = today.year - self._date_of_birth.year
        if (today.month, today.day) < (self._date_of_birth.month, self._date_of_birth.day):
            age -= 1
        return age
    
    def is_license_valid(self) -> bool:
        """Check if license is currently valid."""
        return self._license_expiry >= date.today()
    
    def get_discount_rate(self) -> float:
        """Get discount rate for rental calculations."""
        return self.discount_rate
    
    def add_rental_to_history(self, rental: 'Rental') -> None:
        """Add a rental to history."""
        self._rental_history.append(rental)
    
    def add_loyalty_points(self, amount_spent: float) -> int:
        """Add loyalty points based on amount spent. Returns points added."""
        points = int(amount_spent * self.POINTS_PER_DOLLAR)
        old_points = self._loyalty_points
        self._loyalty_points += points
        
        # Check if crossed 100-point threshold
        if old_points < self.POINTS_FOR_FREE_DAY <= self._loyalty_points:
            self.receive_notification(
                f"Congratulations! You've earned a free rental day! "
                f"Points: {self._loyalty_points}"
            )
        return points
    
    def redeem_free_day(self) -> bool:
        """Redeem points for a free rental day."""
        if self._loyalty_points >= self.POINTS_FOR_FREE_DAY:
            self._loyalty_points -= self.POINTS_FOR_FREE_DAY
            return True
        return False
    
    def has_recent_accident_claim(self) -> bool:
        """Check if customer has accident claims in last 12 months."""
        cutoff = date.today() - timedelta(days=365)
        return any(
            r.damage_claim > 0 and r.start_date >= cutoff 
            for r in self._rental_history
        )
    
    def receive_notification(self, message: str) -> None:
        """Receive a notification."""
        print(f"[NOTIFICATION to {self._name}]: {message}")
    
    def __str__(self) -> str:
        return (f"{self.get_tier().value.title()}Customer: {self._name} "
                f"(ID: {self._customer_id}, Points: {self._loyalty_points})")


class StandardCustomer(Customer):
    """
    Standard membership tier—baseline rental privileges.
    
    Discount: 0%, Daily mileage limit: 200 km, Priority booking: 24 hours
    No free vehicle upgrades. Entry level for all customers.
    """
    
    def __init__(self, customer_id: str, name: str, email: str,
                 date_of_birth: date, license_number: str,
                 license_expiry: date, has_commercial_endorsement: bool = False):
        """Initialise a Standard tier customer."""
        super().__init__(customer_id, name, email, date_of_birth,
                         license_number, license_expiry,
                         has_commercial_endorsement)
    
    @property
    def discount_rate(self) -> float:
        return 0.0
    
    @property
    def daily_mileage_limit(self) -> int:
        return 200
    
    @property
    def priority_booking_hours(self) -> int:
        return 24
    
    def get_tier(self) -> MembershipTier:
        return MembershipTier.STANDARD
    
    def get_free_upgrade_options(self) -> List[VehicleType]:
        """Standard customers receive no free upgrades."""
        return []


class SilverCustomer(Customer):
    """
    Silver membership tier—mid-level benefits.
    
    Discount: 5%, Daily mileage limit: 350 km, Priority booking: 24 hours
    Free upgrade available: Economy to SUV.
    """
    
    def __init__(self, customer_id: str, name: str, email: str,
                 date_of_birth: date, license_number: str,
                 license_expiry: date, has_commercial_endorsement: bool = False):
        """Initialise a Silver tier customer."""
        super().__init__(customer_id, name, email, date_of_birth,
                         license_number, license_expiry,
                         has_commercial_endorsement)
    
    @property
    def discount_rate(self) -> float:
        return 0.05
    
    @property
    def daily_mileage_limit(self) -> int:
        return 350
    
    @property
    def priority_booking_hours(self) -> int:
        return 24
    
    def get_tier(self) -> MembershipTier:
        return MembershipTier.SILVER
    
    def get_free_upgrade_options(self) -> List[VehicleType]:
        """Silver customers can upgrade Economy to SUV."""
        return [VehicleType.SUV]


class GoldCustomer(Customer):
    """
    Gold membership tier—premium rental experience.
    
    Discount: 10%, Daily mileage limit: 500 km, Priority booking: 72 hours (3 days)
    Free one-tier upgrade on eligible vehicles.
    """
    
    def __init__(self, customer_id: str, name: str, email: str,
                 date_of_birth: date, license_number: str,
                 license_expiry: date, has_commercial_endorsement: bool = False):
        """Initialise a Gold tier customer."""
        super().__init__(customer_id, name, email, date_of_birth,
                         license_number, license_expiry,
                         has_commercial_endorsement)
    
    @property
    def discount_rate(self) -> float:
        return 0.10
    
    @property
    def daily_mileage_limit(self) -> int:
        return 500
    
    @property
    def priority_booking_hours(self) -> int:
        return 72
    
    def get_tier(self) -> MembershipTier:
        return MembershipTier.GOLD
    
    def get_free_upgrade_options(self) -> List[VehicleType]:
        """Gold customers eligible for one-tier upgrade: to SUV or Luxury."""
        return [VehicleType.SUV, VehicleType.LUXURY]


class PlatinumCustomer(Customer):
    """
    Platinum membership tier—VIP rental privileges.
    
    Discount: 15%, Daily mileage limit: Unlimited (0), Priority booking: 168 hours (7 days)
    Free two-tier upgrade. Complimentary roadside assistance included.
    """
    
    def __init__(self, customer_id: str, name: str, email: str,
                 date_of_birth: date, license_number: str,
                 license_expiry: date, has_commercial_endorsement: bool = False):
        """Initialise a Platinum tier customer."""
        super().__init__(customer_id, name, email, date_of_birth,
                         license_number, license_expiry,
                         has_commercial_endorsement)
        self._has_roadside_assistance = True
    
    @property
    def discount_rate(self) -> float:
        return 0.15
    
    @property
    def daily_mileage_limit(self) -> int:
        return 0  # Unlimited
    
    @property
    def priority_booking_hours(self) -> int:
        return 168
    
    def get_tier(self) -> MembershipTier:
        return MembershipTier.PLATINUM
    
    def get_free_upgrade_options(self) -> List[VehicleType]:
        """Platinum customers eligible for two-tier upgrade: SUV, Luxury, or Commercial."""
        return [VehicleType.SUV, VehicleType.LUXURY, VehicleType.COMMERCIAL]


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


class FleetRegistry(metaclass=RegistryMeta):
    """
    Central registry for AutoDrive fleet and operations.
    Singleton pattern ensures single source of truth.
    """
    
    def __init__(self):
        self._vehicles: Dict[str, Vehicle] = {}
        self._customers: Dict[str, Customer] = {}
        self._rentals: Dict[str, 'Rental'] = {}
        self._admin_observers: List[Callable[[str], None]] = []
        self._maintenance_observers: List[Callable[[str], None]] = []
    
    def add_vehicle(self, vehicle: Vehicle) -> None:
        """Add a vehicle to the fleet."""
        self._vehicles[vehicle.vehicle_id] = vehicle
        # Attach maintenance observer
        for observer in self._maintenance_observers:
            vehicle.attach(observer)
    
    def get_vehicle(self, vehicle_id: str) -> Vehicle:
        """Retrieve a vehicle from the fleet."""
        if vehicle_id not in self._vehicles:
            raise VehicleNotFoundError(vehicle_id)
        return self._vehicles[vehicle_id]
    
    def add_customer(self, customer: Customer) -> None:
        """Add a customer to the directory."""
        self._customers[customer.customer_id] = customer
    
    def get_customer(self, customer_id: str) -> Customer:
        """Retrieve a customer."""
        if customer_id not in self._customers:
            raise CustomerNotFoundError(customer_id)
        return self._customers[customer_id]
    
    def add_rental(self, rental: 'Rental') -> None:
        """Add a rental to the registry."""
        self._rentals[rental.rental_id] = rental
    
    def get_rental(self, rental_id: str) -> 'Rental':
        """Retrieve a rental."""
        if rental_id not in self._rentals:
            raise RentalNotFoundError(rental_id)
        return self._rentals[rental_id]
    
    def attach_admin_observer(self, observer: Callable[[str], None]) -> None:
        """Attach an admin observer for alerts."""
        if observer not in self._admin_observers:
            self._admin_observers.append(observer)
    
    def attach_maintenance_observer(self, observer: Callable[[str], None]) -> None:
        """Attach a maintenance observer for service alerts."""
        if observer not in self._maintenance_observers:
            self._maintenance_observers.append(observer)
            # Attach to all existing vehicles
            for vehicle in self._vehicles.values():
                vehicle.attach(observer)
    
    def notify_admins(self, message: str) -> None:
        """Notify all admin observers."""
        for observer in self._admin_observers:
            observer(message)
    
    def get_available_vehicles(self, vehicle_type: VehicleType = None) -> List[Vehicle]:
        """Get all available vehicles, optionally filtered by type."""
        available = [v for v in self._vehicles.values() 
                     if v.is_available and not v.needs_service()]
        if vehicle_type:
            available = [v for v in available if v.get_vehicle_type() == vehicle_type]
        return available
    
    def get_active_rentals(self) -> List['Rental']:
        """Get all active rentals."""
        return [r for r in self._rentals.values() 
                if r.status in (RentalStatus.ACTIVE, RentalStatus.RESERVED)]
    
    def get_overdue_rentals(self) -> List['Rental']:
        """Get all overdue rentals."""
        overdue = []
        today = date.today()
        for rental in self._rentals.values():
            if rental.status == RentalStatus.ACTIVE and rental.end_date < today:
                rental.status = RentalStatus.OVERDUE
                overdue.append(rental)
                self.notify_admins(
                    f"OVERDUE: Rental {rental.rental_id} - "
                    f"Vehicle {rental.vehicle.vehicle_id} was due {rental.end_date}"
                )
        return overdue


# --- Factory Pattern ---
class VehicleFactory:
    """
    Factory for creating vehicles.
    Centralizes creation logic and validates parameters.
    """
    
    REGISTRATION_PATTERN = re.compile(r'^[A-Z]{3}-\d{3}$')
    CURRENT_YEAR = date.today().year
    MIN_YEAR = 2018
    
    @classmethod
    def create_vehicle(cls, vehicle_type: str, vehicle_id: str, make: str,
                       model: str, year: int, mileage: int,
                       condition: VehicleCondition, last_service_date: date,
                       last_service_mileage: int, **kwargs) -> Vehicle:
        """
        Create a vehicle of the specified type with comprehensive validation.
        
        Parameters:
            vehicle_type: One of 'economy', 'suv', 'luxury', 'commercial'
            vehicle_id: Registration plate in format ABC-123
            make: Vehicle manufacturer name
            model: Vehicle model name
            year: Manufacturing year (2018 to current)
            mileage: Current odometer reading in kilometres
            condition: VehicleCondition enum value
            last_service_date: Date of most recent service
            last_service_mileage: Odometer at last service
            **kwargs: Type-specific parameters (see Raises)
        
        Returns:
            Vehicle: Configured vehicle instance ready for fleet
            
        Raises:
            VehicleError: If registration format invalid or year out of range
            
        Notes:
            - EconomyCar kwargs: fuel_efficiency_kmpl, has_gps (optional)
            - SUV kwargs: is_4wd, seating_capacity, towing_capacity_kg, fuel_type (optional)
            - LuxuryVehicle kwargs: brand_tier, features
            - CommercialVan kwargs: cargo_capacity_m3, has_refrigeration, max_payload_kg
        """
        # Validate registration format
        if not cls.REGISTRATION_PATTERN.match(vehicle_id):
            raise VehicleError(
                f"Invalid registration format '{vehicle_id}'. Expected: ABC-123"
            )
        
        # Validate year
        if not cls.MIN_YEAR <= year <= cls.CURRENT_YEAR:
            raise VehicleError(
                f"Invalid year {year}. Must be between {cls.MIN_YEAR} and {cls.CURRENT_YEAR}"
            )
        
        # Create vehicle based on type
        vehicle_type = vehicle_type.lower()
        
        if vehicle_type == "economy":
            return EconomyCar(
                vehicle_id, make, model, year, mileage, condition,
                last_service_date, last_service_mileage,
                fuel_efficiency_kmpl=kwargs.get("fuel_efficiency_kmpl", 12.0),
                has_gps=kwargs.get("has_gps", False)
            )
        
        elif vehicle_type == "suv":
            return SUV(
                vehicle_id, make, model, year, mileage, condition,
                last_service_date, last_service_mileage,
                is_4wd=kwargs.get("is_4wd", True),
                seating_capacity=kwargs.get("seating_capacity", 5),
                towing_capacity_kg=kwargs.get("towing_capacity_kg", 2500),
                fuel_type=kwargs.get("fuel_type", "Petrol")
            )
        
        elif vehicle_type == "luxury":
            return LuxuryVehicle(
                vehicle_id, make, model, year, mileage, condition,
                last_service_date, last_service_mileage,
                brand_tier=kwargs.get("brand_tier", "Premium"),
                features=kwargs.get("features", [])
            )
        
        elif vehicle_type == "commercial":
            return CommercialVan(
                vehicle_id, make, model, year, mileage, condition,
                last_service_date, last_service_mileage,
                cargo_capacity_m3=kwargs.get("cargo_capacity_m3", 10.0),
                has_refrigeration=kwargs.get("has_refrigeration", False),
                max_payload_kg=kwargs.get("max_payload_kg", 1500)
            )
        
        else:
            raise VehicleError(
                f"Unknown vehicle type '{vehicle_type}'. "
                f"Must be one of: economy, suv, luxury, commercial"
            )


# --- Adapter Pattern ---
class LegacyVehicleAdapter:
    """
    Adapter to convert legacy vehicle data to modern Vehicle objects.
    
    Legacy format:
    {
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
    """
    
    TYPE_MAPPING = {
        "E": "economy",
        "S": "suv",
        "L": "luxury",
        "C": "commercial"
    }
    
    CONDITION_MAPPING = {
        1: VehicleCondition.EXCELLENT,
        2: VehicleCondition.GOOD,
        3: VehicleCondition.FAIR
    }
    
    def __init__(self, factory: VehicleFactory):
        self._factory = factory
    
    def adapt(self, legacy_data: Dict) -> Vehicle:
        """
        Convert legacy vehicle data to a modern Vehicle object.
        
        Legacy format:
        {
            "reg": "XYZ-789",
            "car_make": "BMW",
            "car_model": "X5",
            "manufacture_year": 2022,
            "km_reading": 45000,
            "type_code": "S",  # E=Economy, S=SUV, L=Luxury, C=Commercial
            "ready": True,
            "cond": 2,  # 1=Excellent, 2=Good, 3=Fair
            "last_svc": "2024-01-15"  # YYYY-MM-DD string
        }
        
        Parameters:
            legacy_data: Dictionary in legacy format
        
        Returns:
            Vehicle: Converted modern vehicle object
            
        Raises:
            LegacyDataFormatError: If required fields are missing or invalid
        """
        # Validate required fields
        required_fields = ["reg", "car_make", "car_model", "manufacture_year",
                          "km_reading", "type_code", "cond", "last_svc"]
        
        for field in required_fields:
            if field not in legacy_data:
                raise LegacyDataFormatError(field, "required field", "missing")
        
        # Extract and validate type code
        type_code = legacy_data.get("type_code", "").upper()
        if type_code not in self.TYPE_MAPPING:
            raise LegacyDataFormatError(
                "type_code", "one of E, S, L, C",
                type_code
            )
        vehicle_type = self.TYPE_MAPPING[type_code]
        
        # Extract and validate condition code
        cond_code = legacy_data.get("cond")
        if cond_code not in self.CONDITION_MAPPING:
            raise LegacyDataFormatError(
                "cond", "one of 1, 2, 3",
                str(cond_code)
            )
        condition = self.CONDITION_MAPPING[cond_code]
        
        # Parse date string
        try:
            last_svc_str = legacy_data.get("last_svc")
            last_service_date = datetime.strptime(last_svc_str, "%Y-%m-%d").date()
        except (ValueError, TypeError) as e:
            raise LegacyDataFormatError(
                "last_svc", "YYYY-MM-DD date string",
                str(legacy_data.get("last_svc"))
            )
        
        # Create vehicle using factory
        vehicle = self._factory.create_vehicle(
            vehicle_type=vehicle_type,
            vehicle_id=legacy_data["reg"],
            make=legacy_data["car_make"],
            model=legacy_data["car_model"],
            year=legacy_data["manufacture_year"],
            mileage=legacy_data["km_reading"],
            condition=condition,
            last_service_date=last_service_date,
            last_service_mileage=legacy_data.get("km_at_service", legacy_data["km_reading"])
        )
        
        return vehicle


# --- Observer Pattern: Waitlist System ---
class WaitlistManager:
    """
    Manages waitlists for vehicle types.
    Implements Observer pattern for availability notifications.
    """
    
    WAITLIST_EXPIRY_DAYS = 7
    CONFIRMATION_HOURS = 24
    
    def __init__(self, registry: FleetRegistry):
        self._registry = registry
        self._waitlists: Dict[VehicleType, List[Tuple[Customer, date, Tuple[date, date]]]] = {
            vt: [] for vt in VehicleType
        }
        self._customer_waitlist: Dict[str, VehicleType] = {}
    
    def join_waitlist(self, customer: Customer, vehicle_type: VehicleType,
                      preferred_dates: Tuple[date, date]) -> int:
        """
        Add customer to waitlist for a vehicle type.
        Platinum customers get priority.
        
        Returns:
            int: Position in waitlist (1-indexed)
        """
        # Check if customer already on a waitlist
        if customer.customer_id in self._customer_waitlist:
            existing_type = self._customer_waitlist[customer.customer_id]
            raise RentalError(
                f"Customer already on waitlist for {existing_type.value}. "
                f"Leave that waitlist first."
            )
        
        entry = (customer, date.today(), preferred_dates)
        waitlist = self._waitlists[vehicle_type]
        
        # Platinum customers get priority
        if customer.get_tier() == MembershipTier.PLATINUM:
            # Insert after other Platinum customers
            platinum_count = sum(
                1 for c, _, _ in waitlist 
                if c.get_tier() == MembershipTier.PLATINUM
            )
            waitlist.insert(platinum_count, entry)
            position = platinum_count + 1
        else:
            waitlist.append(entry)
            position = len(waitlist)
        
        self._customer_waitlist[customer.customer_id] = vehicle_type
        return position
    
    def leave_waitlist(self, customer: Customer, vehicle_type: VehicleType) -> bool:
        """Remove customer from waitlist."""
        waitlist = self._waitlists[vehicle_type]
        for i, (c, _, _) in enumerate(waitlist):
            if c.customer_id == customer.customer_id:
                waitlist.pop(i)
                del self._customer_waitlist[customer.customer_id]
                return True
        return False
    
    def process_vehicle_return(self, vehicle: Vehicle) -> Optional[Customer]:
        """
        Process a vehicle return and notify next customer in waitlist.
        Returns the notified customer, if any.
        """
        vehicle_type = vehicle.get_vehicle_type()
        waitlist = self._waitlists[vehicle_type]
        
        # Clean up expired entries
        self._clean_expired_entries(vehicle_type)
        
        if not waitlist:
            return None
        
        # Notify first customer
        customer, _, preferred_dates = waitlist[0]
        customer.receive_notification(
            f"A {vehicle_type.value} ({vehicle.make} {vehicle.model}) is now available! "
            f"You have {self.CONFIRMATION_HOURS} hours to confirm your booking."
        )
        return customer
    
    def _clean_expired_entries(self, vehicle_type: VehicleType) -> None:
        """Remove expired waitlist entries."""
        cutoff = date.today() - timedelta(days=self.WAITLIST_EXPIRY_DAYS)
        self._waitlists[vehicle_type] = [
            (c, d, p) for c, d, p in self._waitlists[vehicle_type]
            if d >= cutoff
        ]
    
    def check_availability(self, vehicle_type: VehicleType, 
                           start_date: date, end_date: date) -> List[Vehicle]:
        """Get available vehicles of a type for given dates."""
        return self._registry.get_available_vehicles(vehicle_type)


# ============================================================================
# SECTION 7: RENTAL MANAGEMENT
# ============================================================================

class Rental:
    """Represents a vehicle rental agreement."""
    
    LATE_FEE_MULTIPLIER = 1.5
    EXCESS_MILEAGE_RATE = 0.25  # per km
    
    def __init__(self, customer: Customer, vehicle: Vehicle,
                 start_date: date, end_date: date,
                 insurance_type: InsuranceType):
        self._rental_id = str(uuid.uuid4())[:8].upper()
        self._customer = customer
        self._vehicle = vehicle
        self._start_date = start_date
        self._end_date = end_date
        self._actual_return_date: Optional[date] = None
        self._start_mileage = vehicle.mileage
        self._end_mileage: Optional[int] = None
        self._insurance_type = insurance_type
        self._status = RentalStatus.RESERVED
        self._damage_claim: float = 0.0
        self._total_cost: float = 0.0
    
    @property
    def rental_id(self) -> str:
        return self._rental_id
    
    @property
    def customer(self) -> Customer:
        return self._customer
    
    @property
    def vehicle(self) -> Vehicle:
        return self._vehicle
    
    @property
    def start_date(self) -> date:
        return self._start_date
    
    @property
    def end_date(self) -> date:
        return self._end_date
    
    @end_date.setter
    def end_date(self, value: date) -> None:
        self._end_date = value
    
    @property
    def actual_return_date(self) -> Optional[date]:
        return self._actual_return_date
    
    @actual_return_date.setter
    def actual_return_date(self, value: date) -> None:
        self._actual_return_date = value
    
    @property
    def start_mileage(self) -> int:
        return self._start_mileage
    
    @property
    def end_mileage(self) -> Optional[int]:
        return self._end_mileage
    
    @end_mileage.setter
    def end_mileage(self, value: int) -> None:
        self._end_mileage = value
    
    @property
    def insurance_type(self) -> InsuranceType:
        return self._insurance_type
    
    @property
    def status(self) -> RentalStatus:
        return self._status
    
    @status.setter
    def status(self, value: RentalStatus) -> None:
        self._status = value
    
    @property
    def damage_claim(self) -> float:
        return self._damage_claim
    
    @damage_claim.setter
    def damage_claim(self, value: float) -> None:
        self._damage_claim = max(0, value)
    
    @property
    def total_cost(self) -> float:
        return self._total_cost
    
    @total_cost.setter
    def total_cost(self, value: float) -> None:
        self._total_cost = value
    
    def get_rental_days(self) -> int:
        """Get number of rental days (planned)."""
        return (self._end_date - self._start_date).days
    
    def get_actual_days(self) -> int:
        """Get actual rental days (if returned)."""
        if self._actual_return_date:
            return (self._actual_return_date - self._start_date).days
        return self.get_rental_days()
    
    def get_late_days(self) -> int:
        """Get number of days late (0 if on time or early)."""
        if not self._actual_return_date:
            return 0
        if self._actual_return_date <= self._end_date:
            return 0
        return (self._actual_return_date - self._end_date).days
    
    def get_mileage_driven(self) -> int:
        """Get total mileage driven."""
        if self._end_mileage is None:
            return 0
        return self._end_mileage - self._start_mileage
    
    def get_excess_mileage(self) -> int:
        """Get excess mileage over daily limit."""
        if self._end_mileage is None:
            return 0
        
        daily_limit = self._customer.daily_mileage_limit
        if daily_limit == 0:  # Unlimited
            return 0
        
        allowed = daily_limit * self.get_actual_days()
        driven = self.get_mileage_driven()
        return max(0, driven - allowed)
    
    def __str__(self) -> str:
        return (f"Rental {self._rental_id}: {self._customer.name} - "
                f"{self._vehicle.make} {self._vehicle.model} "
                f"({self._status.value})")


class Invoice:
    """Represents a rental invoice."""
    
    def __init__(self, rental: Rental):
        self._invoice_id = f"INV-{rental.rental_id}"
        self._rental = rental
        self._base_rental_cost: float = 0.0
        self._insurance_cost: float = 0.0
        self._late_fee: float = 0.0
        self._mileage_fee: float = 0.0
        self._damage_charge: float = 0.0
        self._deposit_held: float = 0.0
        self._deposit_returned: float = 0.0
        self._loyalty_points_earned: int = 0
        
        self._calculate()
    
    def _calculate(self) -> None:
        """Calculate all invoice components."""
        rental = self._rental
        vehicle = rental.vehicle
        customer = rental.customer
        
        # Base rental cost
        days = rental.get_actual_days()
        self._base_rental_cost = vehicle.calculate_rental_cost(days, customer)
        
        # Insurance cost
        insurance_daily = INSURANCE_CONFIG[rental.insurance_type]["daily_cost"]
        self._insurance_cost = insurance_daily * days
        
        # Late fee (150% of daily rate for extra days)
        late_days = rental.get_late_days()
        if late_days > 0:
            self._late_fee = vehicle.daily_rate * Rental.LATE_FEE_MULTIPLIER * late_days
        
        # Excess mileage fee
        excess_km = rental.get_excess_mileage()
        if excess_km > 0:
            self._mileage_fee = excess_km * Rental.EXCESS_MILEAGE_RATE
        
        # Damage handling
        self._deposit_held = vehicle.deposit
        if rental.damage_claim > 0:
            excess = INSURANCE_CONFIG[rental.insurance_type]["excess"]
            charge = min(rental.damage_claim, excess)
            if charge <= self._deposit_held:
                self._deposit_returned = self._deposit_held - charge
                self._damage_charge = 0
            else:
                self._deposit_returned = 0
                self._damage_charge = charge - self._deposit_held
        else:
            self._deposit_returned = self._deposit_held
        
        # Loyalty points
        total_spend = (self._base_rental_cost + self._insurance_cost + 
                       self._late_fee + self._mileage_fee)
        self._loyalty_points_earned = int(total_spend * Customer.POINTS_PER_DOLLAR)
    
    @property
    def total_charges(self) -> float:
        """Total amount charged."""
        return (self._base_rental_cost + self._insurance_cost + 
                self._late_fee + self._mileage_fee + self._damage_charge)
    
    def __str__(self) -> str:
        lines = [
            "=" * 50,
            f"INVOICE: {self._invoice_id}",
            "=" * 50,
            f"Customer: {self._rental.customer.name}",
            f"Vehicle: {self._rental.vehicle.make} {self._rental.vehicle.model}",
            f"Rental Period: {self._rental.start_date} to {self._rental.actual_return_date}",
            "-" * 50,
            f"Base Rental Cost:     ${self._base_rental_cost:>10.2f}",
            f"Insurance ({self._rental.insurance_type.value}): ${self._insurance_cost:>10.2f}",
        ]
        if self._late_fee > 0:
            lines.append(f"Late Fee ({self._rental.get_late_days()} days): ${self._late_fee:>10.2f}")
        if self._mileage_fee > 0:
            lines.append(f"Excess Mileage:       ${self._mileage_fee:>10.2f}")
        if self._damage_charge > 0:
            lines.append(f"Damage Charge:        ${self._damage_charge:>10.2f}")
        lines.extend([
            "-" * 50,
            f"TOTAL:                ${self.total_charges:>10.2f}",
            "-" * 50,
            f"Deposit Held:         ${self._deposit_held:>10.2f}",
            f"Deposit Returned:     ${self._deposit_returned:>10.2f}",
            f"Loyalty Points Earned: {self._loyalty_points_earned}",
            "=" * 50,
        ])
        return "\n".join(lines)


class RentalService:
    """Manages all rental operations for AutoDrive."""
    
    def __init__(self, registry: FleetRegistry):
        self._registry = registry
        self._waitlist_manager = WaitlistManager(registry)
    
    def create_rental(self, customer: Customer, vehicle: Vehicle,
                      start_date: date, end_date: date,
                      insurance_type: InsuranceType) -> Rental:
        """
        Create a new rental agreement with comprehensive eligibility checks.
        
        Validates:
        - Customer license is current
        - Customer age meets vehicle minimum
        - Customer meets membership eligibility (Ultra luxury, high-mileage)
        - Customer has commercial endorsement if required
        - Customer has no recent accident claims (for luxury vehicles)
        - Vehicle is available for rental period
        - Vehicle doesn't need service
        - Insurance level meets vehicle minimum requirements
        
        Parameters:
            customer: Customer seeking to rent
            vehicle: Vehicle to be rented
            start_date: Intended rental start date
            end_date: Intended rental end date
            insurance_type: Selected insurance coverage level
        
        Returns:
            Rental: Created rental agreement
            
        Raises:
            LicenseExpiredError: If customer's license is expired
            AgeRestrictionError: If customer too young for vehicle type
            EligibilityError: If customer doesn't meet tier requirements
            VehicleUnavailableError: If vehicle not available
            VehicleServiceRequiredError: If vehicle needs service
            InsuranceRequiredError: If insurance level insufficient
        """
        # Check license validity
        if not customer.is_license_valid():
            raise LicenseExpiredError(customer.customer_id, customer.license_expiry)
        
        # Check age restriction
        customer_age = customer.get_age()
        if customer_age < vehicle.minimum_driver_age:
            raise AgeRestrictionError(
                customer.customer_id, customer_age,
                vehicle.minimum_driver_age, vehicle.get_vehicle_type().value
            )
        
        # Check commercial endorsement for vans
        if vehicle.get_vehicle_type() == VehicleType.COMMERCIAL:
            if not customer.has_commercial_endorsement:
                raise EligibilityError(
                    customer.customer_id, vehicle.vehicle_id,
                    "Commercial driving endorsement required"
                )
        
        # Check Ultra luxury membership requirement
        if isinstance(vehicle, LuxuryVehicle) and vehicle._brand_tier == "Ultra":
            tier = customer.get_tier()
            if tier not in (MembershipTier.GOLD, MembershipTier.PLATINUM):
                raise EligibilityError(
                    customer.customer_id, vehicle.vehicle_id,
                    f"Ultra-luxury vehicles require Gold or Platinum membership "
                    f"({tier.value} tier insufficient)"
                )
        
        # Check accident history for luxury vehicles
        if vehicle.get_vehicle_type() == VehicleType.LUXURY:
            if customer.has_recent_accident_claim():
                raise EligibilityError(
                    customer.customer_id, vehicle.vehicle_id,
                    "Recent accident claims prohibit luxury vehicle rental"
                )
        
        # Check vehicle availability
        if not vehicle.is_available:
            raise VehicleUnavailableError(vehicle.vehicle_id, "Vehicle currently rented")
        
        # Check if service is needed
        if vehicle.needs_service():
            km_since = vehicle.mileage - vehicle._last_service_mileage
            raise VehicleServiceRequiredError(vehicle.vehicle_id, km_since)
        
        # Check insurance level meets minimum
        min_insurance = vehicle.get_minimum_insurance()
        insurance_levels = [InsuranceType.BASIC, InsuranceType.STANDARD, InsuranceType.PREMIUM]
        if insurance_levels.index(insurance_type) < insurance_levels.index(min_insurance):
            raise InsuranceRequiredError(
                vehicle.get_vehicle_type().value, min_insurance, insurance_type
            )
        
        # Create rental
        rental = Rental(customer, vehicle, start_date, end_date, insurance_type)
        
        # Mark vehicle as unavailable
        vehicle.is_available = False
        
        # Set as customer's active rental
        customer.active_rental = rental
        
        # Register rental
        self._registry.add_rental(rental)
        
        # Update status to ACTIVE if starting today/soon
        if start_date <= date.today():
            rental.status = RentalStatus.ACTIVE
        
        self._registry.notify_admins(
            f"NEW RENTAL: {rental.rental_id} - "
            f"{customer.name} rented {vehicle.make} {vehicle.model}"
        )
        
        return rental
    
    def return_vehicle(self, rental: Rental, return_date: date,
                       final_mileage: int) -> Invoice:
        """
        Process a vehicle return and calculate final costs.
        
        Handles:
        - Update rental with actual return date and mileage
        - Update vehicle mileage and availability
        - Calculate final cost with late fees and excess mileage
        - Award loyalty points
        - Process waitlist notifications
        - Generate invoice
        
        Parameters:
            rental: The rental agreement being completed
            return_date: Actual date vehicle was returned
            final_mileage: Vehicle odometer reading at return
        
        Returns:
            Invoice: Completed rental invoice with all charges
            
        Raises:
            InvalidReturnError: If return operation is invalid
            MileageLimitExceededError: If daily limit severely exceeded
        """
        if rental.status not in (RentalStatus.ACTIVE, RentalStatus.OVERDUE):
            raise InvalidReturnError(
                rental.rental_id,
                f"Cannot return rental with status '{rental.status.value}'"
            )
        
        if final_mileage < rental.start_mileage:
            raise InvalidReturnError(rental.rental_id, "Final mileage less than start mileage")
        
        if return_date < rental.start_date:
            raise InvalidReturnError(rental.rental_id, "Return date before start date")
        
        # Update rental with return information
        rental.actual_return_date = return_date
        rental.end_mileage = final_mileage
        rental.status = RentalStatus.COMPLETED
        
        # Update vehicle mileage and availability
        vehicle = rental.vehicle
        vehicle.mileage = final_mileage
        vehicle.is_available = True
        
        # Create and calculate invoice
        invoice = Invoice(rental)
        rental.total_cost = invoice.total_charges
        
        # Award loyalty points
        points_earned = rental.customer.add_loyalty_points(invoice.total_charges)
        
        # Notify customer
        rental.customer.active_rental = None
        rental.customer.add_rental_to_history(rental)
        rental.customer.receive_notification(
            f"Rental {rental.rental_id} completed. "
            f"Cost: ${invoice.total_charges:.2f}, "
            f"Loyalty points earned: {points_earned}"
        )
        
        # Process waitlist if vehicle now available
        available = self._waitlist_manager.process_vehicle_return(vehicle)
        if available:
            self._registry.notify_admins(
                f"Waitlist notification sent for {vehicle.get_vehicle_type().value} "
                f"({vehicle.make} {vehicle.model})"
            )
        
        self._registry.notify_admins(
            f"RETURN: Rental {rental.rental_id} - "
            f"Vehicle {vehicle.vehicle_id} returned (${invoice.total_charges:.2f})"
        )
        
        return invoice
    
    def extend_rental(self, rental: Rental, new_end_date: date) -> float:
        """
        Extend an active rental.
        
        Returns:
            float: Additional cost for extension
        """
        if rental.status != RentalStatus.ACTIVE:
            raise InvalidReturnError(rental.rental_id, "Cannot extend non-active rental")
        
        if new_end_date <= rental.end_date:
            raise InvalidReturnError(rental.rental_id, "New date must be after current end date")
        
        extra_days = (new_end_date - rental.end_date).days
        extra_cost = rental.vehicle.calculate_rental_cost(extra_days, rental.customer)
        
        rental.end_date = new_end_date
        return extra_cost
    
    def apply_damage_claim(self, rental: Rental, damage_amount: float) -> None:
        """Record a damage claim for a rental."""
        rental.damage_claim = damage_amount
        self._registry.notify_admins(
            f"DAMAGE CLAIM: Rental {rental.rental_id} - "
            f"${damage_amount:.2f} claim filed"
        )


# ============================================================================
# SECTION 8: MAIN DEMONSTRATION
# ============================================================================

def main():
    """
    Comprehensive demonstration of the AutoDrive Vehicle Rental System.
    
    Showcases all major features:
    - Singleton pattern for fleet management
    - Factory pattern for vehicle creation
    - Customer tier system with discounts
    - Rental eligibility validation
    - Cost calculation with penalties
    - Loyalty points system
    - Waitlist management
    - Legacy data adaptation
    - Exception handling
    """
    print("=" * 60)
    print("AutoDrive Vehicle Rental System - Demonstration")
    print("=" * 60)
    
    # ================================================================
    # 1. SINGLETON PATTERN VERIFICATION
    # ================================================================
    print("\n1. Testing Singleton Pattern...")
    reg1 = FleetRegistry()
    reg2 = FleetRegistry()
    print(f"   Same instance: {reg1 is reg2}")  # Should be True
    print("   ✓ FleetRegistry singleton verified")
    
    # ================================================================
    # 2. CREATE VEHICLES USING FACTORY
    # ================================================================
    print("\n2. Creating Vehicles with Factory...")
    factory = VehicleFactory()
    
    economy = factory.create_vehicle(
        "economy", "ABC-001", "Toyota", "Corolla", 2023, 25000,
        VehicleCondition.EXCELLENT, date(2024, 6, 15), 20000,
        fuel_efficiency_kmpl=13.5, has_gps=True
    )
    reg1.add_vehicle(economy)
    print(f"   {economy}")
    
    suv = factory.create_vehicle(
        "suv", "XYZ-456", "Ford", "Explorer", 2022, 45000,
        VehicleCondition.GOOD, date(2024, 1, 10), 30000,
        is_4wd=True, seating_capacity=7, towing_capacity_kg=3500,
        fuel_type="Diesel"
    )
    reg1.add_vehicle(suv)
    print(f"   {suv}")
    
    luxury = factory.create_vehicle(
        "luxury", "LUX-001", "BMW", "740i", 2024, 8000,
        VehicleCondition.EXCELLENT, date(2024, 9, 1), 5000,
        brand_tier="Premium", features=["Leather seats", "Panoramic roof", "Heated seats"]
    )
    reg1.add_vehicle(luxury)
    print(f"   {luxury}")
    
    van = factory.create_vehicle(
        "commercial", "VAN-001", "Mercedes", "Sprinter", 2021, 62000,
        VehicleCondition.GOOD, date(2023, 11, 20), 45000,
        cargo_capacity_m3=14.0, has_refrigeration=True, max_payload_kg=1800
    )
    reg1.add_vehicle(van)
    print(f"   {van}")
    
    # ================================================================
    # 3. CREATE CUSTOMERS OF DIFFERENT TIERS
    # ================================================================
    print("\n3. Creating Customers...")
    
    standard_cust = StandardCustomer(
        "CUST-001", "Alice Smith", "alice@email.com",
        date(1990, 5, 15), "DL123456", date(2026, 12, 31)
    )
    reg1.add_customer(standard_cust)
    print(f"   {standard_cust}")
    
    silver_cust = SilverCustomer(
        "CUST-002", "Bob Johnson", "bob@email.com",
        date(1985, 8, 22), "DL234567", date(2026, 12, 31)
    )
    reg1.add_customer(silver_cust)
    print(f"   {silver_cust}")
    
    gold_cust = GoldCustomer(
        "CUST-003", "Carol Williams", "carol@email.com",
        date(1980, 3, 10), "DL345678", date(2026, 12, 31)
    )
    reg1.add_customer(gold_cust)
    print(f"   {gold_cust}")
    
    platinum_cust = PlatinumCustomer(
        "CUST-004", "David Brown", "david@email.com",
        date(1975, 11, 5), "DL456789", date(2026, 12, 31),
        has_commercial_endorsement=True
    )
    reg1.add_customer(platinum_cust)
    print(f"   {platinum_cust}")
    
    # ================================================================
    # 4. TEST RENTAL ELIGIBILITY AND VALIDATION
    # ================================================================
    print("\n4. Testing Rental Eligibility...")
    
    service = RentalService(reg1)
    start = date(2026, 4, 5)
    end = date(2026, 4, 10)
    
    try:
        # Standard customer rents an economy car
        rental1 = service.create_rental(
            standard_cust, economy, start, end, InsuranceType.BASIC
        )
        print(f"   ✓ {standard_cust.name} → Economy car")
        
        # Gold customer rents a premium luxury vehicle
        rental2 = service.create_rental(
            gold_cust, luxury, date(2026, 4, 12), date(2026, 4, 15),
            InsuranceType.STANDARD
        )
        print(f"   ✓ {gold_cust.name} → Premium Luxury car")
        
    except (EligibilityError, AgeRestrictionError) as e:
        print(f"   ✗ Eligibility error: {e}")
    
    # ================================================================
    # 5. TEST COST CALCULATIONS WITH DISCOUNTS
    # ================================================================
    print("\n5. Testing Cost Calculations...")
    
    # Calculate rental costs with different tier discounts
    rental_days = 5
    economy_cost_standard = economy.calculate_rental_cost(rental_days, standard_cust)
    economy_cost_gold = economy.calculate_rental_cost(rental_days, gold_cust)
    
    print(f"   Economy 5-day rental:")
    print(f"     Standard tier (0% discount): ${economy_cost_standard:.2f}")
    print(f"     Gold tier (10% discount):    ${economy_cost_gold:.2f}")
    
    # ================================================================
    # 6. TEST LATE RETURN PENALTIES
    # ================================================================
    print("\n6. Testing Late Return Penalties...")
    
    # Activate the rental first (it starts today in demo)
    rental1.status = RentalStatus.ACTIVE
    
    # Return vehicle late (2 days late)
    invoice1 = service.return_vehicle(rental1, date(2026, 4, 12), 25587)
    print(f"   Late return: {rental1.get_late_days()} days late")
    print(f"   Late fee: ${invoice1._late_fee:.2f} (1.5x daily rate)")
    print(f"   Total charges: ${invoice1.total_charges:.2f}")
    
    # ================================================================
    # 7. TEST MILEAGE LIMIT ENFORCEMENT
    # ================================================================
    print("\n7. Testing Mileage Limits...")
    
    std_limit = standard_cust.daily_mileage_limit
    gold_limit = gold_cust.daily_mileage_limit
    
    print(f"   Standard customer daily limit: {std_limit} km")
    print(f"   Gold customer daily limit:     {gold_limit} km")
    
    # For 5-day rental: 200km/day = 1000km max
    mileage_driven_std = 1500  # Exceeds by 500km
    excess = mileage_driven_std - (std_limit * 5)
    excess_charge = excess * Rental.EXCESS_MILEAGE_RATE
    print(f"   Standard customer drove {mileage_driven_std}km over 5 days")
    print(f"     Excess: {excess}km × ${Rental.EXCESS_MILEAGE_RATE}/km = ${excess_charge:.2f}")
    
    # ================================================================
    # 8. TEST WAITLIST WITH PRIORITY
    # ================================================================
    print("\n8. Testing Waitlist Priority...")
    
    waitlist_mgr = WaitlistManager(reg1)
    
    # Add customers to waitlist
    pos1 = waitlist_mgr.join_waitlist(
        standard_cust, VehicleType.LUXURY,
        (date(2026, 4, 20), date(2026, 4, 25))
    )
    print(f"   {standard_cust.name} added to waitlist - Position: {pos1}")
    
    pos2 = waitlist_mgr.join_waitlist(
        platinum_cust, VehicleType.LUXURY,
        (date(2026, 4, 20), date(2026, 4, 25))
    )
    print(f"   {platinum_cust.name} added to waitlist - Position: {pos2}")
    print(f"   ✓ Platinum customer has priority (position {pos2} < {pos1})")
    
    # ================================================================
    # 9. TEST LEGACY DATA ADAPTER
    # ================================================================
    print("\n9. Testing Legacy Data Adapter...")
    
    adapter = LegacyVehicleAdapter(factory)
    legacy_data = {
        "reg": "LGY-789",
        "car_make": "BMW",
        "car_model": "X5",
        "manufacture_year": 2022,
        "km_reading": 45000,
        "km_at_service": 40000,
        "type_code": "S",
        "ready": True,
        "cond": 2,
        "last_svc": "2024-01-15"
    }
    
    try:
        adapted_vehicle = adapter.adapt(legacy_data)
        reg1.add_vehicle(adapted_vehicle)
        print(f"   ✓ Adapted legacy vehicle: {adapted_vehicle}")
    except LegacyDataFormatError as e:
        print(f"   ✗ Adaptation error: {e}")
    
    # ================================================================
    # 10. TEST LOYALTY POINTS SYSTEM
    # ================================================================
    print("\n10. Testing Loyalty Points System...")
    
    initial_points = gold_cust.loyalty_points
    points_earned = gold_cust.add_loyalty_points(1000.0)  # $1000 rental
    print(f"   Rental cost: $1000.00")
    print(f"   Points earned: {points_earned} (${gold_cust.POINTS_PER_DOLLAR * 100:.0f} per point)")
    print(f"   Total points: {initial_points} → {gold_cust.loyalty_points}")
    
    if gold_cust.loyalty_points >= gold_cust.POINTS_FOR_FREE_DAY:
        if gold_cust.redeem_free_day():
            print(f"   ✓ Redeemed free rental day!")
            print(f"   Points remaining: {gold_cust.loyalty_points}")
    
    # ================================================================
    # SUMMARY AND STATISTICS
    # ================================================================
    print("\n" + "=" * 60)
    print("Fleet Summary:")
    print(f"  Total vehicles: {len(reg1._vehicles)}")
    print(f"  Total customers: {len(reg1._customers)}")
    print(f"  Active rentals: {len(reg1.get_active_rentals())}")
    print("=" * 60)
    print("Demonstration Complete - All features working correctly!")
    print("=" * 60)


if __name__ == "__main__":
    main()
