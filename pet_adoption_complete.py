"""
NIT2112 Object-Oriented Programming
COMPLETE EXAMPLE: PawsHome Pet Adoption Center System

This is a COMPLETE working example demonstrating all OOP concepts:
- Encapsulation, Inheritance, Polymorphism, Abstraction
- Design Patterns: Factory, Adapter, Observer, Singleton
- Custom Exception Hierarchy
- Complex Business Rules

Students can use this as a reference for understanding how concepts integrate.
"""

from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Callable, Tuple
from enum import Enum
import uuid


# ============================================================================
# SECTION 1: ENUMS AND CONSTANTS
# ============================================================================

class Species(Enum):
    """Animal species categories."""
    DOG = "dog"
    CAT = "cat"
    RABBIT = "rabbit"
    BIRD = "bird"


class AdoptionStatus(Enum):
    """Status of an animal."""
    AVAILABLE = "available"
    PENDING = "pending"
    ADOPTED = "adopted"
    MEDICAL_HOLD = "medical_hold"
    FOSTER = "foster"


class ApplicationStatus(Enum):
    """Status of an adoption application."""
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    WITHDRAWN = "withdrawn"


class AdopterTier(Enum):
    """Adopter experience/tier levels."""
    FIRST_TIME = "first_time"
    EXPERIENCED = "experienced"
    PREMIUM = "premium"  # Previous adopters with excellent track record


class Size(Enum):
    """Animal size categories."""
    SMALL = "small"      # < 10 kg
    MEDIUM = "medium"    # 10-25 kg
    LARGE = "large"      # 25-40 kg
    EXTRA_LARGE = "extra_large"  # > 40 kg


# ============================================================================
# SECTION 2: CUSTOM EXCEPTIONS
# ============================================================================

class AdoptionCenterError(Exception):
    """Base exception for all adoption center errors."""
    pass


class AnimalError(AdoptionCenterError):
    """Base exception for animal-related errors."""
    pass


class AnimalNotFoundError(AnimalError):
    """Raised when an animal cannot be found."""
    def __init__(self, animal_id: str):
        self.animal_id = animal_id
        super().__init__(f"Animal '{animal_id}' not found in the system.")


class AnimalUnavailableError(AnimalError):
    """Raised when an animal is not available for adoption."""
    def __init__(self, animal_id: str, status: AdoptionStatus):
        self.animal_id = animal_id
        self.status = status
        super().__init__(f"Animal '{animal_id}' is not available: {status.value}")


class MedicalHoldError(AnimalError):
    """Raised when an animal is on medical hold."""
    def __init__(self, animal_id: str, reason: str):
        self.animal_id = animal_id
        self.reason = reason
        super().__init__(f"Animal '{animal_id}' is on medical hold: {reason}")


class AdopterError(AdoptionCenterError):
    """Base exception for adopter-related errors."""
    pass


class AdopterNotFoundError(AdopterError):
    """Raised when an adopter cannot be found."""
    def __init__(self, adopter_id: str):
        self.adopter_id = adopter_id
        super().__init__(f"Adopter '{adopter_id}' not found.")


class EligibilityError(AdopterError):
    """Raised when an adopter doesn't meet eligibility requirements."""
    def __init__(self, adopter_id: str, animal_id: str, reason: str):
        self.adopter_id = adopter_id
        self.animal_id = animal_id
        self.reason = reason
        super().__init__(
            f"Adopter '{adopter_id}' not eligible for animal '{animal_id}': {reason}"
        )


class ApplicationError(AdoptionCenterError):
    """Base exception for application-related errors."""
    pass


class ApplicationNotFoundError(ApplicationError):
    """Raised when an application cannot be found."""
    def __init__(self, application_id: str):
        self.application_id = application_id
        super().__init__(f"Application '{application_id}' not found.")


class DuplicateApplicationError(ApplicationError):
    """Raised when an adopter already has a pending application for an animal."""
    def __init__(self, adopter_id: str, animal_id: str):
        self.adopter_id = adopter_id
        self.animal_id = animal_id
        super().__init__(
            f"Adopter '{adopter_id}' already has a pending application for animal '{animal_id}'"
        )


class ApplicationLimitError(ApplicationError):
    """Raised when adopter has too many pending applications."""
    def __init__(self, adopter_id: str, limit: int):
        self.adopter_id = adopter_id
        self.limit = limit
        super().__init__(
            f"Adopter '{adopter_id}' has reached the limit of {limit} pending applications"
        )


class IntegrationError(AdoptionCenterError):
    """Base exception for integration errors."""
    pass


class LegacyDataError(IntegrationError):
    """Raised when legacy data format is invalid."""
    def __init__(self, field: str, expected: str, received: str = ""):
        self.field = field
        message = f"Invalid legacy data for '{field}': expected {expected}"
        if received:
            message += f", got '{received}'"
        super().__init__(message)


# ============================================================================
# SECTION 3: INTERFACES (Abstract Base Classes)
# ============================================================================

class Adoptable(ABC):
    """Interface for animals that can be adopted."""
    
    @abstractmethod
    def get_adoption_fee(self) -> float:
        """Get the adoption fee."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if available for adoption."""
        pass
    
    @abstractmethod
    def get_special_requirements(self) -> List[str]:
        """Get special adoption requirements."""
        pass


class Trackable(ABC):
    """Interface for tracking medical and behavioral history."""
    
    @abstractmethod
    def add_medical_record(self, record: Dict) -> None:
        """Add a medical record."""
        pass
    
    @abstractmethod
    def get_medical_history(self) -> List[Dict]:
        """Get medical history."""
        pass
    
    @abstractmethod
    def is_vaccinated(self) -> bool:
        """Check if fully vaccinated."""
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
# SECTION 4: ANIMAL HIERARCHY
# ============================================================================

class Animal(Adoptable, Trackable, Observable):
    """Abstract base class for all shelter animals."""
    
    BASE_ADOPTION_FEE = 150.0
    
    def __init__(self, animal_id: str, name: str, age_months: int,
                 breed: str, color: str, intake_date: date,
                 is_neutered: bool = False):
        self._animal_id = animal_id
        self._name = name
        self._age_months = age_months
        self._breed = breed
        self._color = color
        self._intake_date = intake_date
        self._is_neutered = is_neutered
        self._status = AdoptionStatus.AVAILABLE
        self._medical_records: List[Dict] = []
        self._behavioral_notes: List[str] = []
        self._vaccinations: Dict[str, date] = {}
        self._special_needs: List[str] = []
        self._observers: List[Callable[[str], None]] = []
    
    @property
    def animal_id(self) -> str:
        return self._animal_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        self._name = value
    
    @property
    def age_months(self) -> int:
        return self._age_months
    
    @property
    def breed(self) -> str:
        return self._breed
    
    @property
    def color(self) -> str:
        return self._color
    
    @property
    def intake_date(self) -> date:
        return self._intake_date
    
    @property
    def is_neutered(self) -> bool:
        return self._is_neutered
    
    @is_neutered.setter
    def is_neutered(self, value: bool) -> None:
        self._is_neutered = value
    
    @property
    def status(self) -> AdoptionStatus:
        return self._status
    
    @status.setter
    def status(self, value: AdoptionStatus) -> None:
        old_status = self._status
        self._status = value
        if old_status != value:
            self.notify(f"{self._name} status changed: {old_status.value} → {value.value}")
    
    @property
    def special_needs(self) -> List[str]:
        return self._special_needs.copy()
    
    # Adoptable interface
    def is_available(self) -> bool:
        return self._status == AdoptionStatus.AVAILABLE
    
    def get_special_requirements(self) -> List[str]:
        requirements = []
        if self._special_needs:
            requirements.extend(self._special_needs)
        if not self._is_neutered:
            requirements.append("Must be neutered before leaving shelter")
        return requirements
    
    # Trackable interface
    def add_medical_record(self, record: Dict) -> None:
        record['date'] = record.get('date', date.today())
        self._medical_records.append(record)
    
    def get_medical_history(self) -> List[Dict]:
        return self._medical_records.copy()
    
    def add_vaccination(self, vaccine_name: str, vaccine_date: date) -> None:
        self._vaccinations[vaccine_name] = vaccine_date
    
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
    
    # Common methods
    def add_behavioral_note(self, note: str) -> None:
        self._behavioral_notes.append(note)
    
    def get_behavioral_notes(self) -> List[str]:
        return self._behavioral_notes.copy()
    
    def add_special_need(self, need: str) -> None:
        self._special_needs.append(need)
    
    def get_age_years(self) -> float:
        return self._age_months / 12
    
    def get_days_in_shelter(self) -> int:
        return (date.today() - self._intake_date).days
    
    def put_on_medical_hold(self, reason: str) -> None:
        self._status = AdoptionStatus.MEDICAL_HOLD
        self.add_medical_record({
            'type': 'medical_hold',
            'reason': reason,
            'date': date.today()
        })
    
    @property
    @abstractmethod
    def species(self) -> Species:
        """Get the species of the animal."""
        pass
    
    @abstractmethod
    def get_adoption_fee(self) -> float:
        """Calculate adoption fee."""
        pass
    
    @abstractmethod
    def is_vaccinated(self) -> bool:
        """Check if fully vaccinated for species."""
        pass
    
    @abstractmethod
    def get_housing_type(self) -> str:
        """Get recommended housing type."""
        pass
    
    def __str__(self) -> str:
        age_str = f"{self._age_months} months" if self._age_months < 12 else f"{self.get_age_years():.1f} years"
        return f"{self._name} ({self._breed}, {age_str}) - {self._status.value}"


class Dog(Animal):
    """Dog animal type."""
    
    REQUIRED_VACCINES = ['rabies', 'distemper', 'parvovirus', 'bordetella']
    BASE_FEE = 250.0
    
    def __init__(self, animal_id: str, name: str, age_months: int,
                 breed: str, color: str, intake_date: date,
                 size: Size, is_house_trained: bool = False,
                 good_with_kids: bool = True, good_with_dogs: bool = True,
                 good_with_cats: bool = False, is_neutered: bool = False):
        super().__init__(animal_id, name, age_months, breed, color, intake_date, is_neutered)
        self._size = size
        self._is_house_trained = is_house_trained
        self._good_with_kids = good_with_kids
        self._good_with_dogs = good_with_dogs
        self._good_with_cats = good_with_cats
        self._energy_level = "medium"  # low, medium, high
    
    @property
    def size(self) -> Size:
        return self._size
    
    @property
    def is_house_trained(self) -> bool:
        return self._is_house_trained
    
    @is_house_trained.setter
    def is_house_trained(self, value: bool) -> None:
        self._is_house_trained = value
    
    @property
    def good_with_kids(self) -> bool:
        return self._good_with_kids
    
    @property
    def good_with_dogs(self) -> bool:
        return self._good_with_dogs
    
    @property
    def good_with_cats(self) -> bool:
        return self._good_with_cats
    
    @property
    def energy_level(self) -> str:
        return self._energy_level
    
    @energy_level.setter
    def energy_level(self, value: str) -> None:
        if value.lower() not in ['low', 'medium', 'high']:
            raise ValueError("Energy level must be 'low', 'medium', or 'high'")
        self._energy_level = value.lower()
    
    @property
    def species(self) -> Species:
        return Species.DOG
    
    def get_adoption_fee(self) -> float:
        fee = self.BASE_FEE
        
        # Puppies (< 6 months) cost more
        if self._age_months < 6:
            fee += 100
        
        # Senior dogs (> 7 years) get discount
        if self._age_months > 84:
            fee -= 75
        
        # Long-stay discount (> 60 days)
        if self.get_days_in_shelter() > 60:
            fee -= 50
        
        return max(fee, 75)  # Minimum fee
    
    def is_vaccinated(self) -> bool:
        return all(v in self._vaccinations for v in self.REQUIRED_VACCINES)
    
    def get_housing_type(self) -> str:
        if self._size in (Size.LARGE, Size.EXTRA_LARGE):
            return "House with yard required"
        elif self._energy_level == "high":
            return "Active household or house with yard"
        else:
            return "Apartment or house suitable"
    
    def get_special_requirements(self) -> List[str]:
        requirements = super().get_special_requirements()
        
        if not self._good_with_kids:
            requirements.append("Adult-only household required")
        if not self._good_with_dogs:
            requirements.append("Must be only dog in household")
        if not self._good_with_cats:
            requirements.append("No cats in household")
        if self._energy_level == "high":
            requirements.append("Requires active lifestyle/regular exercise")
        if self._size in (Size.LARGE, Size.EXTRA_LARGE):
            requirements.append("Experienced large dog owner preferred")
        
        return requirements


class Cat(Animal):
    """Cat animal type."""
    
    REQUIRED_VACCINES = ['rabies', 'fvrcp', 'feline_leukemia']
    BASE_FEE = 175.0
    
    def __init__(self, animal_id: str, name: str, age_months: int,
                 breed: str, color: str, intake_date: date,
                 is_indoor_only: bool = True, is_declawed: bool = False,
                 good_with_dogs: bool = False, good_with_cats: bool = True,
                 is_neutered: bool = False):
        super().__init__(animal_id, name, age_months, breed, color, intake_date, is_neutered)
        self._is_indoor_only = is_indoor_only
        self._is_declawed = is_declawed
        self._good_with_dogs = good_with_dogs
        self._good_with_cats = good_with_cats
        self._litter_trained = True
    
    @property
    def is_indoor_only(self) -> bool:
        return self._is_indoor_only
    
    @property
    def is_declawed(self) -> bool:
        return self._is_declawed
    
    @property
    def good_with_dogs(self) -> bool:
        return self._good_with_dogs
    
    @property
    def good_with_cats(self) -> bool:
        return self._good_with_cats
    
    @property
    def species(self) -> Species:
        return Species.CAT
    
    def get_adoption_fee(self) -> float:
        fee = self.BASE_FEE
        
        # Kittens (< 6 months) cost more
        if self._age_months < 6:
            fee += 50
        
        # Senior cats (> 10 years) get discount
        if self._age_months > 120:
            fee -= 75
        
        # Long-stay discount (> 45 days)
        if self.get_days_in_shelter() > 45:
            fee -= 40
        
        return max(fee, 50)
    
    def is_vaccinated(self) -> bool:
        return all(v in self._vaccinations for v in self.REQUIRED_VACCINES)
    
    def get_housing_type(self) -> str:
        if self._is_indoor_only:
            return "Indoor home required"
        return "Indoor/outdoor home acceptable"
    
    def get_special_requirements(self) -> List[str]:
        requirements = super().get_special_requirements()
        
        if self._is_indoor_only:
            requirements.append("Must be kept indoors only")
        if not self._good_with_dogs:
            requirements.append("No dogs in household")
        if not self._good_with_cats:
            requirements.append("Must be only cat in household")
        
        return requirements


class Rabbit(Animal):
    """Rabbit animal type."""
    
    REQUIRED_VACCINES = ['myxomatosis', 'rvhd']
    BASE_FEE = 100.0
    
    def __init__(self, animal_id: str, name: str, age_months: int,
                 breed: str, color: str, intake_date: date,
                 is_bonded: bool = False, bond_partner_id: str = None,
                 is_neutered: bool = False):
        super().__init__(animal_id, name, age_months, breed, color, intake_date, is_neutered)
        self._is_bonded = is_bonded
        self._bond_partner_id = bond_partner_id
        self._hutch_trained = True
    
    @property
    def is_bonded(self) -> bool:
        return self._is_bonded
    
    @property
    def bond_partner_id(self) -> Optional[str]:
        return self._bond_partner_id
    
    @property
    def species(self) -> Species:
        return Species.RABBIT
    
    def get_adoption_fee(self) -> float:
        fee = self.BASE_FEE
        
        # Bonded pairs adopted together get discount
        if self._is_bonded:
            fee -= 25
        
        # Long-stay discount (> 30 days)
        if self.get_days_in_shelter() > 30:
            fee -= 20
        
        return max(fee, 40)
    
    def is_vaccinated(self) -> bool:
        return all(v in self._vaccinations for v in self.REQUIRED_VACCINES)
    
    def get_housing_type(self) -> str:
        return "Indoor housing with exercise space required"
    
    def get_special_requirements(self) -> List[str]:
        requirements = super().get_special_requirements()
        
        if self._is_bonded:
            requirements.append(f"Must be adopted with bonded partner ({self._bond_partner_id})")
        requirements.append("Requires spacious enclosure or rabbit-proofed room")
        
        return requirements


class Bird(Animal):
    """Bird animal type."""
    
    REQUIRED_VACCINES = []  # Birds typically don't require vaccines for adoption
    BASE_FEE = 75.0
    
    def __init__(self, animal_id: str, name: str, age_months: int,
                 breed: str, color: str, intake_date: date,
                 can_talk: bool = False, wingspan_cm: int = 30,
                 noise_level: str = "moderate"):
        super().__init__(animal_id, name, age_months, breed, color, intake_date, False)
        self._can_talk = can_talk
        self._wingspan_cm = wingspan_cm
        self._noise_level = noise_level  # quiet, moderate, loud
    
    @property
    def can_talk(self) -> bool:
        return self._can_talk
    
    @property
    def wingspan_cm(self) -> int:
        return self._wingspan_cm
    
    @property
    def noise_level(self) -> str:
        return self._noise_level
    
    @property
    def species(self) -> Species:
        return Species.BIRD
    
    @property
    def is_neutered(self) -> bool:
        return True  # Not applicable to birds
    
    def get_adoption_fee(self) -> float:
        fee = self.BASE_FEE
        
        # Talking birds cost more
        if self._can_talk:
            fee += 100
        
        # Large birds (wingspan > 60cm) cost more
        if self._wingspan_cm > 60:
            fee += 50
        
        # Long-stay discount (> 30 days)
        if self.get_days_in_shelter() > 30:
            fee -= 20
        
        return max(fee, 40)
    
    def is_vaccinated(self) -> bool:
        return True  # Birds don't require vaccines
    
    def get_housing_type(self) -> str:
        if self._wingspan_cm > 60:
            return "Large aviary or flight cage required"
        return "Appropriate sized cage with daily out-of-cage time"
    
    def get_special_requirements(self) -> List[str]:
        requirements = super().get_special_requirements()
        
        if self._noise_level == "loud":
            requirements.append("Not suitable for apartments")
        if self._wingspan_cm > 60:
            requirements.append("Large aviary required")
        
        return requirements


# ============================================================================
# SECTION 5: ADOPTER HIERARCHY
# ============================================================================

class Adopter(ABC):
    """Abstract base class for adopters."""
    
    MAX_PENDING_APPLICATIONS_FIRST_TIME = 1
    MAX_PENDING_APPLICATIONS_EXPERIENCED = 2
    MAX_PENDING_APPLICATIONS_PREMIUM = 5
    
    def __init__(self, adopter_id: str, name: str, email: str,
                 phone: str, address: str, has_yard: bool = False,
                 has_other_pets: bool = False, has_children: bool = False):
        self._adopter_id = adopter_id
        self._name = name
        self._email = email
        self._phone = phone
        self._address = address
        self._has_yard = has_yard
        self._has_other_pets = has_other_pets
        self._has_children = has_children
        self._adoption_history: List['AdoptionApplication'] = []
        self._pending_applications: List['AdoptionApplication'] = []
        self._home_check_completed = False
        self._home_check_date: Optional[date] = None
    
    @property
    def adopter_id(self) -> str:
        return self._adopter_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def email(self) -> str:
        return self._email
    
    @property
    def phone(self) -> str:
        return self._phone
    
    @property
    def address(self) -> str:
        return self._address
    
    @property
    def has_yard(self) -> bool:
        return self._has_yard
    
    @property
    def has_other_pets(self) -> bool:
        return self._has_other_pets
    
    @property
    def has_children(self) -> bool:
        return self._has_children
    
    @property
    def adoption_history(self) -> List['AdoptionApplication']:
        return self._adoption_history.copy()
    
    @property
    def pending_applications(self) -> List['AdoptionApplication']:
        return self._pending_applications.copy()
    
    @property
    def home_check_completed(self) -> bool:
        return self._home_check_completed
    
    @home_check_completed.setter
    def home_check_completed(self, value: bool) -> None:
        self._home_check_completed = value
        if value:
            self._home_check_date = date.today()
    
    @property
    @abstractmethod
    def tier(self) -> AdopterTier:
        """Get the adopter tier."""
        pass
    
    @property
    @abstractmethod
    def max_pending_applications(self) -> int:
        """Maximum pending applications allowed."""
        pass
    
    @property
    @abstractmethod
    def adoption_fee_discount(self) -> float:
        """Discount percentage on adoption fees."""
        pass
    
    @abstractmethod
    def requires_home_check(self, animal: Animal) -> bool:
        """Check if home check is required for this animal."""
        pass
    
    def can_submit_application(self) -> bool:
        """Check if adopter can submit a new application."""
        return len(self._pending_applications) < self.max_pending_applications
    
    def add_pending_application(self, app: 'AdoptionApplication') -> None:
        if not self.can_submit_application():
            raise ApplicationLimitError(self._adopter_id, self.max_pending_applications)
        self._pending_applications.append(app)
    
    def complete_application(self, app: 'AdoptionApplication') -> None:
        if app in self._pending_applications:
            self._pending_applications.remove(app)
        self._adoption_history.append(app)
    
    def get_successful_adoptions(self) -> int:
        return sum(1 for app in self._adoption_history 
                   if app.status == ApplicationStatus.COMPLETED)
    
    def receive_notification(self, message: str) -> None:
        print(f"[TO: {self._name}] {message}")
    
    def __str__(self) -> str:
        return f"{self._name} ({self.tier.value}) - {self.get_successful_adoptions()} adoptions"


class FirstTimeAdopter(Adopter):
    """First-time adopter with no previous adoption history."""
    
    def __init__(self, adopter_id: str, name: str, email: str,
                 phone: str, address: str, has_yard: bool = False,
                 has_other_pets: bool = False, has_children: bool = False):
        super().__init__(adopter_id, name, email, phone, address,
                        has_yard, has_other_pets, has_children)
    
    @property
    def tier(self) -> AdopterTier:
        return AdopterTier.FIRST_TIME
    
    @property
    def max_pending_applications(self) -> int:
        return 1
    
    @property
    def adoption_fee_discount(self) -> float:
        return 0.0  # No discount
    
    def requires_home_check(self, animal: Animal) -> bool:
        # First-time adopters always need home check for dogs
        if animal.species == Species.DOG:
            return True
        # And for any animal with special needs
        if animal.special_needs:
            return True
        return False


class ExperiencedAdopter(Adopter):
    """Adopter with previous adoption experience."""
    
    def __init__(self, adopter_id: str, name: str, email: str,
                 phone: str, address: str, has_yard: bool = False,
                 has_other_pets: bool = False, has_children: bool = False,
                 years_experience: int = 1):
        super().__init__(adopter_id, name, email, phone, address,
                        has_yard, has_other_pets, has_children)
        self._years_experience = years_experience
    
    @property
    def years_experience(self) -> int:
        return self._years_experience
    
    @property
    def tier(self) -> AdopterTier:
        return AdopterTier.EXPERIENCED
    
    @property
    def max_pending_applications(self) -> int:
        return 2
    
    @property
    def adoption_fee_discount(self) -> float:
        return 0.10  # 10% discount
    
    def requires_home_check(self, animal: Animal) -> bool:
        # Experienced adopters need home check only for large dogs or special needs
        if isinstance(animal, Dog) and animal.size in (Size.LARGE, Size.EXTRA_LARGE):
            return True
        if animal.special_needs:
            return True
        return False


class PremiumAdopter(Adopter):
    """Premium adopter with excellent track record."""
    
    def __init__(self, adopter_id: str, name: str, email: str,
                 phone: str, address: str, has_yard: bool = False,
                 has_other_pets: bool = False, has_children: bool = False,
                 membership_date: date = None):
        super().__init__(adopter_id, name, email, phone, address,
                        has_yard, has_other_pets, has_children)
        self._membership_date = membership_date or date.today()
        self._home_check_completed = True  # Premium members pre-approved
    
    @property
    def membership_date(self) -> date:
        return self._membership_date
    
    @property
    def tier(self) -> AdopterTier:
        return AdopterTier.PREMIUM
    
    @property
    def max_pending_applications(self) -> int:
        return 5
    
    @property
    def adoption_fee_discount(self) -> float:
        return 0.20  # 20% discount
    
    def requires_home_check(self, animal: Animal) -> bool:
        # Premium members only need check for extra-large dogs
        if isinstance(animal, Dog) and animal.size == Size.EXTRA_LARGE:
            return True
        return False
    
    def get_priority_score(self) -> int:
        """Premium adopters get priority based on membership length."""
        days_member = (date.today() - self._membership_date).days
        return min(days_member // 30, 10)  # Max 10 points for 10+ months


# ============================================================================
# SECTION 6: APPLICATION AND ADOPTION CLASSES
# ============================================================================

class AdoptionApplication(Observable):
    """Represents an adoption application."""
    
    def __init__(self, application_id: str, adopter: Adopter,
                 animal: Animal, submission_date: date = None):
        self._application_id = application_id
        self._adopter = adopter
        self._animal = animal
        self._submission_date = submission_date or date.today()
        self._status = ApplicationStatus.SUBMITTED
        self._review_notes: List[str] = []
        self._home_check_passed: Optional[bool] = None
        self._interview_date: Optional[date] = None
        self._adoption_date: Optional[date] = None
        self._final_fee: float = 0.0
        self._observers: List[Callable[[str], None]] = []
    
    @property
    def application_id(self) -> str:
        return self._application_id
    
    @property
    def adopter(self) -> Adopter:
        return self._adopter
    
    @property
    def animal(self) -> Animal:
        return self._animal
    
    @property
    def submission_date(self) -> date:
        return self._submission_date
    
    @property
    def status(self) -> ApplicationStatus:
        return self._status
    
    @status.setter
    def status(self, value: ApplicationStatus) -> None:
        old_status = self._status
        self._status = value
        if old_status != value:
            self.notify(
                f"Application {self._application_id} status: {old_status.value} → {value.value}"
            )
    
    @property
    def review_notes(self) -> List[str]:
        return self._review_notes.copy()
    
    @property
    def home_check_passed(self) -> Optional[bool]:
        return self._home_check_passed
    
    @home_check_passed.setter
    def home_check_passed(self, value: bool) -> None:
        self._home_check_passed = value
    
    @property
    def adoption_date(self) -> Optional[date]:
        return self._adoption_date
    
    @property
    def final_fee(self) -> float:
        return self._final_fee
    
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
    
    def add_review_note(self, note: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        self._review_notes.append(f"[{timestamp}] {note}")
    
    def start_review(self) -> None:
        self.status = ApplicationStatus.UNDER_REVIEW
    
    def approve(self) -> None:
        self.status = ApplicationStatus.APPROVED
        self._animal.status = AdoptionStatus.PENDING
        # Calculate final fee with discount
        base_fee = self._animal.get_adoption_fee()
        discount = self._adopter.adoption_fee_discount
        self._final_fee = base_fee * (1 - discount)
    
    def reject(self, reason: str) -> None:
        self.add_review_note(f"REJECTED: {reason}")
        self.status = ApplicationStatus.REJECTED
    
    def complete_adoption(self) -> None:
        if self._status != ApplicationStatus.APPROVED:
            raise ApplicationError("Cannot complete adoption - application not approved")
        self._adoption_date = date.today()
        self.status = ApplicationStatus.COMPLETED
        self._animal.status = AdoptionStatus.ADOPTED
        self._adopter.complete_application(self)
    
    def withdraw(self, reason: str = "") -> None:
        if self._status in (ApplicationStatus.COMPLETED, ApplicationStatus.REJECTED):
            raise ApplicationError("Cannot withdraw completed or rejected application")
        self.add_review_note(f"WITHDRAWN: {reason}")
        self.status = ApplicationStatus.WITHDRAWN
        if self._animal.status == AdoptionStatus.PENDING:
            self._animal.status = AdoptionStatus.AVAILABLE
    
    def get_days_pending(self) -> int:
        return (date.today() - self._submission_date).days
    
    def __str__(self) -> str:
        return (f"Application {self._application_id}: "
                f"{self._adopter.name} → {self._animal.name} ({self._status.value})")


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


class AdoptionRegistry(metaclass=RegistryMeta):
    """
    Central registry for the adoption center.
    Singleton ensures single source of truth.
    """
    
    def __init__(self):
        self._animals: Dict[str, Animal] = {}
        self._adopters: Dict[str, Adopter] = {}
        self._applications: Dict[str, AdoptionApplication] = {}
        self._waitlists: Dict[Species, List[Adopter]] = {s: [] for s in Species}
        self._staff_observers: List[Callable[[str], None]] = []
    
    # Animal management
    def add_animal(self, animal: Animal) -> None:
        self._animals[animal.animal_id] = animal
        # Notify staff about new intake
        self._notify_staff(f"New intake: {animal.name} ({animal.breed})")
        # Notify adopters on waitlist
        self._process_waitlist(animal.species)
    
    def get_animal(self, animal_id: str) -> Animal:
        if animal_id not in self._animals:
            raise AnimalNotFoundError(animal_id)
        return self._animals[animal_id]
    
    def get_available_animals(self, species: Species = None) -> List[Animal]:
        available = [a for a in self._animals.values() if a.is_available()]
        if species:
            available = [a for a in available if a.species == species]
        return available
    
    def get_animals_by_species(self, species: Species) -> List[Animal]:
        return [a for a in self._animals.values() if a.species == species]
    
    # Adopter management
    def add_adopter(self, adopter: Adopter) -> None:
        self._adopters[adopter.adopter_id] = adopter
    
    def get_adopter(self, adopter_id: str) -> Adopter:
        if adopter_id not in self._adopters:
            raise AdopterNotFoundError(adopter_id)
        return self._adopters[adopter_id]
    
    # Application management
    def add_application(self, app: AdoptionApplication) -> None:
        self._applications[app.application_id] = app
        # Subscribe adopter to notifications
        app.attach(app.adopter.receive_notification)
    
    def get_application(self, application_id: str) -> AdoptionApplication:
        if application_id not in self._applications:
            raise ApplicationNotFoundError(application_id)
        return self._applications[application_id]
    
    def get_pending_applications(self) -> List[AdoptionApplication]:
        pending_statuses = (ApplicationStatus.SUBMITTED, ApplicationStatus.UNDER_REVIEW)
        return [a for a in self._applications.values() if a.status in pending_statuses]
    
    def get_applications_for_animal(self, animal_id: str) -> List[AdoptionApplication]:
        return [a for a in self._applications.values() 
                if a.animal.animal_id == animal_id 
                and a.status not in (ApplicationStatus.REJECTED, ApplicationStatus.WITHDRAWN)]
    
    # Waitlist management
    def join_waitlist(self, adopter: Adopter, species: Species) -> int:
        if adopter not in self._waitlists[species]:
            self._waitlists[species].append(adopter)
        return self._waitlists[species].index(adopter) + 1
    
    def leave_waitlist(self, adopter: Adopter, species: Species) -> bool:
        if adopter in self._waitlists[species]:
            self._waitlists[species].remove(adopter)
            return True
        return False
    
    def _process_waitlist(self, species: Species) -> None:
        """Notify adopters on waitlist about new animal."""
        for adopter in self._waitlists[species][:5]:  # Notify top 5
            adopter.receive_notification(
                f"A new {species.value} is available for adoption!"
            )
    
    # Staff notification
    def attach_staff_observer(self, observer: Callable[[str], None]) -> None:
        if observer not in self._staff_observers:
            self._staff_observers.append(observer)
    
    def _notify_staff(self, message: str) -> None:
        for observer in self._staff_observers:
            observer(message)
    
    # Statistics
    def get_adoption_stats(self) -> Dict:
        total_animals = len(self._animals)
        available = len([a for a in self._animals.values() if a.is_available()])
        adopted = len([a for a in self._animals.values() 
                      if a.status == AdoptionStatus.ADOPTED])
        pending_apps = len(self.get_pending_applications())
        
        return {
            'total_animals': total_animals,
            'available': available,
            'adopted': adopted,
            'pending_applications': pending_apps,
            'adoption_rate': (adopted / total_animals * 100) if total_animals > 0 else 0
        }


# --- Factory Pattern ---
class AnimalFactory:
    """Factory for creating animal objects."""
    
    @staticmethod
    def create_animal(species: str, animal_id: str, name: str,
                      age_months: int, breed: str, color: str,
                      intake_date: date = None, **kwargs) -> Animal:
        """
        Create an animal based on species.
        
        Args:
            species: One of 'dog', 'cat', 'rabbit', 'bird'
            animal_id: Unique identifier
            name: Animal's name
            age_months: Age in months
            breed: Breed description
            color: Color description
            intake_date: Date of intake (defaults to today)
            **kwargs: Species-specific parameters
            
        Returns:
            Animal: Created animal
            
        Raises:
            AnimalError: If species is invalid
        """
        intake = intake_date or date.today()
        species_lower = species.lower()
        
        if species_lower == 'dog':
            return Dog(
                animal_id, name, age_months, breed, color, intake,
                size=kwargs.get('size', Size.MEDIUM),
                is_house_trained=kwargs.get('is_house_trained', False),
                good_with_kids=kwargs.get('good_with_kids', True),
                good_with_dogs=kwargs.get('good_with_dogs', True),
                good_with_cats=kwargs.get('good_with_cats', False),
                is_neutered=kwargs.get('is_neutered', False)
            )
        
        elif species_lower == 'cat':
            return Cat(
                animal_id, name, age_months, breed, color, intake,
                is_indoor_only=kwargs.get('is_indoor_only', True),
                is_declawed=kwargs.get('is_declawed', False),
                good_with_dogs=kwargs.get('good_with_dogs', False),
                good_with_cats=kwargs.get('good_with_cats', True),
                is_neutered=kwargs.get('is_neutered', False)
            )
        
        elif species_lower == 'rabbit':
            return Rabbit(
                animal_id, name, age_months, breed, color, intake,
                is_bonded=kwargs.get('is_bonded', False),
                bond_partner_id=kwargs.get('bond_partner_id'),
                is_neutered=kwargs.get('is_neutered', False)
            )
        
        elif species_lower == 'bird':
            return Bird(
                animal_id, name, age_months, breed, color, intake,
                can_talk=kwargs.get('can_talk', False),
                wingspan_cm=kwargs.get('wingspan_cm', 30),
                noise_level=kwargs.get('noise_level', 'moderate')
            )
        
        else:
            raise AnimalError(f"Unknown species: {species}")


# --- Adapter Pattern ---
class LegacyAnimalAdapter:
    """
    Adapter for legacy shelter management system data.
    
    Legacy format:
    {
        "ref": "D-2024-001",
        "animal_name": "Max",
        "age_years": 3.5,
        "type": "DOG",
        "breed_info": "Labrador Mix",
        "coat_color": "Golden",
        "arrival": "2024-01-15",
        "fixed": "Y",
        "size_code": "L",
        "trained": "Y",
        "kid_friendly": "Y",
        "dog_friendly": "Y",
        "cat_friendly": "N"
    }
    """
    
    SIZE_MAPPING = {
        "S": Size.SMALL,
        "M": Size.MEDIUM,
        "L": Size.LARGE,
        "XL": Size.EXTRA_LARGE
    }
    
    def __init__(self, factory: AnimalFactory):
        self._factory = factory
    
    def adapt(self, legacy_data: Dict) -> Animal:
        """Convert legacy data to modern Animal object."""
        # Validate required fields
        required = ['ref', 'animal_name', 'type']
        for field in required:
            if field not in legacy_data:
                raise LegacyDataError(field, "required field", "missing")
        
        # Convert type
        type_code = legacy_data['type'].upper()
        if type_code not in ['DOG', 'CAT', 'RABBIT', 'BIRD']:
            raise LegacyDataError('type', 'DOG/CAT/RABBIT/BIRD', type_code)
        
        # Convert age from years to months
        age_years = legacy_data.get('age_years', 1.0)
        age_months = int(age_years * 12)
        
        # Parse arrival date
        arrival_str = legacy_data.get('arrival', date.today().isoformat())
        try:
            intake_date = date.fromisoformat(arrival_str)
        except ValueError:
            raise LegacyDataError('arrival', 'YYYY-MM-DD format', arrival_str)
        
        # Build kwargs based on animal type
        kwargs = {
            'is_neutered': legacy_data.get('fixed', 'N').upper() == 'Y'
        }
        
        if type_code == 'DOG':
            size_code = legacy_data.get('size_code', 'M')
            kwargs.update({
                'size': self.SIZE_MAPPING.get(size_code, Size.MEDIUM),
                'is_house_trained': legacy_data.get('trained', 'N').upper() == 'Y',
                'good_with_kids': legacy_data.get('kid_friendly', 'Y').upper() == 'Y',
                'good_with_dogs': legacy_data.get('dog_friendly', 'Y').upper() == 'Y',
                'good_with_cats': legacy_data.get('cat_friendly', 'N').upper() == 'Y'
            })
        
        elif type_code == 'CAT':
            kwargs.update({
                'is_indoor_only': legacy_data.get('indoor_only', 'Y').upper() == 'Y',
                'good_with_dogs': legacy_data.get('dog_friendly', 'N').upper() == 'Y',
                'good_with_cats': legacy_data.get('cat_friendly', 'Y').upper() == 'Y'
            })
        
        return self._factory.create_animal(
            species=type_code.lower(),
            animal_id=legacy_data['ref'],
            name=legacy_data['animal_name'],
            age_months=age_months,
            breed=legacy_data.get('breed_info', 'Unknown'),
            color=legacy_data.get('coat_color', 'Unknown'),
            intake_date=intake_date,
            **kwargs
        )


# ============================================================================
# SECTION 8: ADOPTION SERVICE
# ============================================================================

class AdoptionService:
    """Service for managing the adoption process."""
    
    def __init__(self, registry: AdoptionRegistry):
        self._registry = registry
        self._application_counter = 0
    
    def submit_application(self, adopter: Adopter, animal: Animal) -> AdoptionApplication:
        """Submit a new adoption application."""
        # Validate animal availability
        if not animal.is_available():
            raise AnimalUnavailableError(animal.animal_id, animal.status)
        
        if animal.status == AdoptionStatus.MEDICAL_HOLD:
            raise MedicalHoldError(animal.animal_id, "under veterinary care")
        
        # Check for duplicate applications
        existing = self._registry.get_applications_for_animal(animal.animal_id)
        for app in existing:
            if app.adopter.adopter_id == adopter.adopter_id:
                raise DuplicateApplicationError(adopter.adopter_id, animal.animal_id)
        
        # Check application limits
        if not adopter.can_submit_application():
            raise ApplicationLimitError(adopter.adopter_id, adopter.max_pending_applications)
        
        # Check basic eligibility
        self._check_eligibility(adopter, animal)
        
        # Create application
        self._application_counter += 1
        app_id = f"APP-{self._application_counter:05d}"
        
        application = AdoptionApplication(app_id, adopter, animal)
        adopter.add_pending_application(application)
        self._registry.add_application(application)
        
        return application
    
    def _check_eligibility(self, adopter: Adopter, animal: Animal) -> None:
        """Check if adopter meets basic eligibility for this animal."""
        requirements = animal.get_special_requirements()
        
        # Check yard requirement for large dogs
        if isinstance(animal, Dog):
            if animal.size in (Size.LARGE, Size.EXTRA_LARGE) and not adopter.has_yard:
                raise EligibilityError(
                    adopter.adopter_id, animal.animal_id,
                    "Large dogs require a home with a yard"
                )
            if not animal.good_with_kids and adopter.has_children:
                raise EligibilityError(
                    adopter.adopter_id, animal.animal_id,
                    "This dog is not suitable for homes with children"
                )
        
        # Check for bonded pairs
        if isinstance(animal, Rabbit) and animal.is_bonded:
            # Both must be adopted together
            partner = self._registry.get_animal(animal.bond_partner_id)
            if not partner.is_available():
                raise EligibilityError(
                    adopter.adopter_id, animal.animal_id,
                    f"Bonded partner {partner.name} is not available"
                )
    
    def review_application(self, application: AdoptionApplication,
                           notes: str = "") -> None:
        """Start reviewing an application."""
        application.start_review()
        if notes:
            application.add_review_note(notes)
    
    def conduct_home_check(self, application: AdoptionApplication,
                           passed: bool, notes: str = "") -> None:
        """Record home check results."""
        application.home_check_passed = passed
        application.adopter.home_check_completed = passed
        application.add_review_note(
            f"Home check {'PASSED' if passed else 'FAILED'}: {notes}"
        )
    
    def approve_application(self, application: AdoptionApplication) -> None:
        """Approve an adoption application."""
        # Verify home check if required
        adopter = application.adopter
        animal = application.animal
        
        if adopter.requires_home_check(animal) and not application.home_check_passed:
            raise ApplicationError("Home check required but not passed")
        
        application.approve()
    
    def reject_application(self, application: AdoptionApplication,
                           reason: str) -> None:
        """Reject an adoption application."""
        application.reject(reason)
        if application in application.adopter.pending_applications:
            application.adopter._pending_applications.remove(application)
    
    def complete_adoption(self, application: AdoptionApplication) -> Dict:
        """Complete the adoption process."""
        application.complete_adoption()
        
        # Generate adoption certificate
        return {
            'certificate_number': f"CERT-{application.application_id}",
            'adopter_name': application.adopter.name,
            'animal_name': application.animal.name,
            'species': application.animal.species.value,
            'breed': application.animal.breed,
            'adoption_date': application.adoption_date.isoformat(),
            'fee_paid': application.final_fee
        }
    
    def get_match_score(self, adopter: Adopter, animal: Animal) -> int:
        """Calculate compatibility score between adopter and animal."""
        score = 50  # Base score
        
        # Yard bonus for dogs
        if isinstance(animal, Dog):
            if adopter.has_yard:
                score += 15
            if animal.good_with_kids == adopter.has_children:
                score += 10
            if animal.good_with_dogs and adopter.has_other_pets:
                score += 5
        
        # Experience bonus
        if adopter.tier == AdopterTier.EXPERIENCED:
            score += 10
        elif adopter.tier == AdopterTier.PREMIUM:
            score += 20
            if isinstance(adopter, PremiumAdopter):
                score += adopter.get_priority_score()
        
        # Home check already done
        if adopter.home_check_completed:
            score += 10
        
        return min(score, 100)
    
    def get_recommended_animals(self, adopter: Adopter,
                                 species: Species = None) -> List[Tuple[Animal, int]]:
        """Get recommended animals with match scores."""
        available = self._registry.get_available_animals(species)
        
        recommendations = []
        for animal in available:
            try:
                self._check_eligibility(adopter, animal)
                score = self.get_match_score(adopter, animal)
                recommendations.append((animal, score))
            except EligibilityError:
                continue  # Skip ineligible animals
        
        # Sort by score descending
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:10]  # Top 10


# ============================================================================
# SECTION 9: MAIN DEMONSTRATION
# ============================================================================

def main():
    """Demonstrate the pet adoption center system."""
    print("=" * 60)
    print("PawsHome Pet Adoption Center System")
    print("=" * 60)
    
    # 1. Singleton Pattern Verification
    print("\n1. SINGLETON PATTERN VERIFICATION")
    print("-" * 40)
    reg1 = AdoptionRegistry()
    reg2 = AdoptionRegistry()
    print(f"   Same instance: {reg1 is reg2}")
    
    registry = reg1
    
    # 2. Staff Observer
    print("\n2. OBSERVER PATTERN - STAFF NOTIFICATIONS")
    print("-" * 40)
    
    def staff_notification(message: str):
        print(f"   [STAFF ALERT]: {message}")
    
    registry.attach_staff_observer(staff_notification)
    print("   Staff observer attached")
    
    # 3. Create Animals using Factory Pattern
    print("\n3. FACTORY PATTERN - CREATING ANIMALS")
    print("-" * 40)
    factory = AnimalFactory()
    
    # Dogs
    max_dog = factory.create_animal(
        'dog', 'D-001', 'Max', 36, 'Labrador', 'Golden',
        size=Size.LARGE, is_house_trained=True,
        good_with_kids=True, good_with_dogs=True, good_with_cats=False,
        is_neutered=True
    )
    max_dog.add_vaccination('rabies', date.today() - timedelta(days=30))
    max_dog.add_vaccination('distemper', date.today() - timedelta(days=30))
    max_dog.add_vaccination('parvovirus', date.today() - timedelta(days=30))
    max_dog.add_vaccination('bordetella', date.today() - timedelta(days=30))
    
    bella_dog = factory.create_animal(
        'dog', 'D-002', 'Bella', 8, 'Beagle Mix', 'Tri-color',
        size=Size.MEDIUM, is_house_trained=False,
        good_with_kids=True, good_with_dogs=True, good_with_cats=True,
        is_neutered=False
    )
    bella_dog.energy_level = 'high'
    
    # Cats
    whiskers = factory.create_animal(
        'cat', 'C-001', 'Whiskers', 60, 'Persian', 'White',
        is_indoor_only=True, good_with_dogs=False, good_with_cats=True,
        is_neutered=True
    )
    whiskers.add_vaccination('rabies', date.today() - timedelta(days=60))
    whiskers.add_vaccination('fvrcp', date.today() - timedelta(days=60))
    whiskers.add_vaccination('feline_leukemia', date.today() - timedelta(days=60))
    
    shadow = factory.create_animal(
        'cat', 'C-002', 'Shadow', 24, 'Domestic Shorthair', 'Black',
        is_indoor_only=False, good_with_dogs=True, good_with_cats=False,
        is_neutered=True
    )
    
    # Rabbits (bonded pair)
    thumper = factory.create_animal(
        'rabbit', 'R-001', 'Thumper', 18, 'Holland Lop', 'Brown',
        is_bonded=True, bond_partner_id='R-002', is_neutered=True
    )
    
    cotton = factory.create_animal(
        'rabbit', 'R-002', 'Cotton', 18, 'Holland Lop', 'White',
        is_bonded=True, bond_partner_id='R-001', is_neutered=True
    )
    
    # Bird
    sunny = factory.create_animal(
        'bird', 'B-001', 'Sunny', 24, 'Cockatiel', 'Yellow/Gray',
        can_talk=True, wingspan_cm=35, noise_level='moderate'
    )
    
    # Add all animals to registry (triggers notifications)
    for animal in [max_dog, bella_dog, whiskers, shadow, thumper, cotton, sunny]:
        registry.add_animal(animal)
    
    print(f"\n   Total animals in shelter: {len(registry.get_available_animals())}")
    
    # 4. Display Animal Information (Polymorphism)
    print("\n4. POLYMORPHISM - ANIMAL DETAILS")
    print("-" * 40)
    
    for animal in [max_dog, whiskers, thumper, sunny]:
        print(f"\n   {animal}")
        print(f"      Species: {animal.species.value}")
        print(f"      Adoption Fee: ${animal.get_adoption_fee():.2f}")
        print(f"      Prep Time: {animal.get_preparation_time() if hasattr(animal, 'get_preparation_time') else 'N/A'}")
        print(f"      Housing: {animal.get_housing_type()}")
        print(f"      Vaccinated: {animal.is_vaccinated()}")
        reqs = animal.get_special_requirements()
        if reqs:
            print(f"      Requirements: {', '.join(reqs[:2])}")
    
    # 5. Create Adopters (Different Tiers)
    print("\n5. INHERITANCE - ADOPTER TIERS")
    print("-" * 40)
    
    alice = FirstTimeAdopter(
        'A-001', 'Alice Smith', 'alice@email.com', '0412345678',
        '123 Main St, Melbourne', has_yard=True, has_children=True
    )
    
    bob = ExperiencedAdopter(
        'A-002', 'Bob Johnson', 'bob@email.com', '0423456789',
        '456 Oak Ave, Sydney', has_yard=True, has_other_pets=True,
        years_experience=3
    )
    bob.home_check_completed = True
    
    carol = PremiumAdopter(
        'A-003', 'Carol Williams', 'carol@email.com', '0434567890',
        '789 Park Rd, Brisbane', has_yard=True,
        membership_date=date.today() - timedelta(days=365)
    )
    
    for adopter in [alice, bob, carol]:
        registry.add_adopter(adopter)
        print(f"   {adopter}")
        print(f"      Max Applications: {adopter.max_pending_applications}")
        print(f"      Fee Discount: {adopter.adoption_fee_discount * 100:.0f}%")
        print(f"      Home Check Done: {adopter.home_check_completed}")
    
    # 6. Adoption Service and Applications
    print("\n6. ADOPTION WORKFLOW")
    print("-" * 40)
    
    service = AdoptionService(registry)
    
    # Get recommendations for Bob
    print("\n   Recommendations for Bob (experienced adopter with yard):")
    recommendations = service.get_recommended_animals(bob)
    for animal, score in recommendations[:3]:
        print(f"      - {animal.name} ({animal.breed}): {score}% match")
    
    # Alice applies for Max
    print("\n   Alice applying for Max...")
    try:
        app1 = service.submit_application(alice, max_dog)
        print(f"      Application created: {app1.application_id}")
        print(f"      Status: {app1.status.value}")
        
        # Review process
        service.review_application(app1, "Good initial application")
        print(f"      Status: {app1.status.value}")
        
        # Home check (required for first-time adopter with dog)
        service.conduct_home_check(app1, True, "Large yard, secure fencing")
        print(f"      Home check: PASSED")
        
        # Approve
        service.approve_application(app1)
        print(f"      Status: {app1.status.value}")
        print(f"      Fee after discount: ${app1.final_fee:.2f}")
        
        # Complete adoption
        cert = service.complete_adoption(app1)
        print(f"      ADOPTION COMPLETE!")
        print(f"      Certificate: {cert['certificate_number']}")
        
    except AdoptionCenterError as e:
        print(f"      Error: {e}")
    
    # 7. Bob applies for Shadow (cat)
    print("\n   Bob applying for Shadow...")
    try:
        app2 = service.submit_application(bob, shadow)
        print(f"      Application: {app2.application_id}")
        
        # Fast-track for experienced adopter
        service.review_application(app2)
        service.approve_application(app2)  # No home check needed
        
        cert = service.complete_adoption(app2)
        print(f"      ADOPTION COMPLETE!")
        print(f"      Fee paid: ${cert['fee_paid']:.2f} (10% discount applied)")
        
    except AdoptionCenterError as e:
        print(f"      Error: {e}")
    
    # 8. Carol applies for bonded rabbits
    print("\n   Carol (Premium) applying for bonded rabbits...")
    try:
        # Apply for both bonded rabbits
        app3 = service.submit_application(carol, thumper)
        app4 = service.submit_application(carol, cotton)
        
        print(f"      Applications: {app3.application_id}, {app4.application_id}")
        
        # Premium adopters get fast processing
        for app in [app3, app4]:
            service.review_application(app)
            service.approve_application(app)
        
        # Complete both
        for app in [app3, app4]:
            cert = service.complete_adoption(app)
            print(f"      Completed: {cert['animal_name']} - ${cert['fee_paid']:.2f}")
        
        print(f"      Carol's total adoptions: {carol.get_successful_adoptions()}")
        
    except AdoptionCenterError as e:
        print(f"      Error: {e}")
    
    # 9. Exception Handling Examples
    print("\n7. EXCEPTION HANDLING")
    print("-" * 40)
    
    # Try to adopt already-adopted animal
    print("\n   Attempting to adopt Max (already adopted)...")
    try:
        service.submit_application(bob, max_dog)
    except AnimalUnavailableError as e:
        print(f"      Caught: {e}")
    
    # Try to exceed application limit
    print("\n   First-time adopter trying to exceed limit...")
    new_adopter = FirstTimeAdopter('A-099', 'Test User', 'test@test.com',
                                    '0400000000', '1 Test St', has_yard=True)
    registry.add_adopter(new_adopter)
    try:
        service.submit_application(new_adopter, bella_dog)
        service.submit_application(new_adopter, whiskers)  # Should fail
    except ApplicationLimitError as e:
        print(f"      Caught: {e}")
    
    # 10. Adapter Pattern - Legacy Data
    print("\n8. ADAPTER PATTERN - LEGACY DATA")
    print("-" * 40)
    
    legacy_data = {
        "ref": "L-001",
        "animal_name": "Rocky",
        "age_years": 2.5,
        "type": "DOG",
        "breed_info": "German Shepherd Mix",
        "coat_color": "Black/Tan",
        "arrival": "2024-02-01",
        "fixed": "Y",
        "size_code": "L",
        "trained": "Y",
        "kid_friendly": "Y",
        "dog_friendly": "N",
        "cat_friendly": "N"
    }
    
    adapter = LegacyAnimalAdapter(factory)
    rocky = adapter.adapt(legacy_data)
    registry.add_animal(rocky)
    
    print(f"   Converted: {rocky}")
    print(f"   Size: {rocky.size.value}")
    print(f"   House trained: {rocky.is_house_trained}")
    print(f"   Good with kids: {rocky.good_with_kids}")
    print(f"   Good with dogs: {rocky.good_with_dogs}")
    
    # 11. Statistics
    print("\n9. ADOPTION STATISTICS")
    print("-" * 40)
    
    stats = registry.get_adoption_stats()
    print(f"   Total Animals: {stats['total_animals']}")
    print(f"   Available: {stats['available']}")
    print(f"   Adopted: {stats['adopted']}")
    print(f"   Pending Applications: {stats['pending_applications']}")
    print(f"   Adoption Rate: {stats['adoption_rate']:.1f}%")
    
    # 12. Waitlist Demo
    print("\n10. WAITLIST SYSTEM")
    print("-" * 40)
    
    # Dave joins waitlist for dogs
    dave = FirstTimeAdopter('A-004', 'Dave Brown', 'dave@email.com',
                            '0445678901', '101 Dog Lane', has_yard=True)
    registry.add_adopter(dave)
    
    position = registry.join_waitlist(dave, Species.DOG)
    print(f"   Dave joined dog waitlist at position {position}")
    
    # Add a new dog (triggers notification)
    print("\n   Adding new dog to shelter...")
    new_dog = factory.create_animal(
        'dog', 'D-003', 'Charlie', 12, 'Golden Retriever', 'Golden',
        size=Size.LARGE, is_house_trained=True, is_neutered=True
    )
    registry.add_animal(new_dog)
    
    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
