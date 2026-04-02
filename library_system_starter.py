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
from typing import List, Optional, Dict, Callable
import uuid


# ============================================================================
# SECTION 1: CUSTOM EXCEPTIONS
# ============================================================================

class LibraryError(Exception):
    """Base exception for all library-related errors."""
    pass


class CatalogueError(LibraryError):
    """Base exception for catalogue-related errors."""
    pass


class ItemNotFoundError(CatalogueError):
    """Raised when a catalogue item cannot be found."""
    def __init__(self, item_id: str):
        self.item_id = item_id
        super().__init__(f"Catalogue item '{item_id}' not found.")


class ItemUnavailableError(CatalogueError):
    """Raised when attempting to borrow an unavailable item."""
    def __init__(self, item_id: str, reason: str = ""):
        self.item_id = item_id
        message = f"Item '{item_id}' is not available"
        if reason:
            message += f": {reason}"
        super().__init__(message)


class MemberError(LibraryError):
    """Base exception for member-related errors."""
    pass


class MemberNotFoundError(MemberError):
    """Raised when a member cannot be found."""
    def __init__(self, member_id: str):
        self.member_id = member_id
        super().__init__(f"Member '{member_id}' not found.")


class LoanLimitExceededError(MemberError):
    """Raised when a member exceeds their loan limit."""
    def __init__(self, member_id: str, current_loans: int, max_loans: int):
        self.member_id = member_id
        self.current_loans = current_loans
        self.max_loans = max_loans
        super().__init__(
            f"Member '{member_id}' has reached loan limit "
            f"({current_loans}/{max_loans})."
        )


class OutstandingFinesError(MemberError):
    """Raised when a member has excessive outstanding fines."""
    def __init__(self, member_id: str, fines: float, limit: float = 10.0):
        self.member_id = member_id
        self.fines = fines
        self.limit = limit
        super().__init__(
            f"Member '{member_id}' has outstanding fines of ${fines:.2f} "
            f"(limit: ${limit:.2f})."
        )


class EligibilityError(MemberError):
    """Raised when a member does not meet eligibility requirements."""
    def __init__(self, member_id: str, item_id: str, reason: str):
        self.member_id = member_id
        self.item_id = item_id
        self.reason = reason
        super().__init__(
            f"Member '{member_id}' in eligibility check for item '{item_id}': {reason}"
        )


class TransactionError(LibraryError):
    """Base exception for transaction-related errors."""
    pass


class InvalidReturnError(TransactionError):
    """Raised when a return operation is invalid."""
    def __init__(self, member_id: str, item_id: str, reason: str = ""):
        self.member_id = member_id
        self.item_id = item_id
        message = f"Invalid return: member '{member_id}', item '{item_id}'"
        if reason:
            message += f" - {reason}"
        super().__init__(message)


class ReservationConflictError(TransactionError):
    """Raised when a reservation conflict occurs."""
    def __init__(self, member_id: str, item_id: str, reason: str = ""):
        self.member_id = member_id
        self.item_id = item_id
        message = f"Reservation conflict: member '{member_id}', item '{item_id}'"
        if reason:
            message += f" - {reason}"
        super().__init__(message)


class IntegrationError(LibraryError):
    """Base exception for integration-related errors."""
    pass


class LegacyDataFormatError(IntegrationError):
    """Raised when legacy data format is invalid."""
    def __init__(self, field: str, expected: str, received: str = ""):
        self.field = field
        message = f"Invalid legacy data format for field '{field}'"
        if expected:
            message += f": expected {expected}"
        if received:
            message += f", received '{received}'"
        super().__init__(message)


# ============================================================================
# SECTION 2: INTERFACES (Abstract Base Classes)
# ============================================================================

class Borrowable(ABC):
    """Interface for items that can be borrowed."""
    
    @abstractmethod
    def calculate_loan_period(self) -> int:
        """Returns maximum loan period in days."""
        pass


class Reservable(ABC):
    """Interface for items that can be reserved."""
    
    @abstractmethod
    def get_reservation_priority(self) -> float:
        """Returns priority weight for reservation queue."""
        pass
    
    @abstractmethod
    def can_be_reserved(self) -> bool:
        """Returns True if item can be reserved."""
        pass


# ============================================================================
# SECTION 3: CATALOGUE ITEM HIERARCHY
# ============================================================================

class CatalogueItem(Borrowable, Reservable):
    """Abstract base class for all catalogue items."""
    
    def __init__(self, item_id: str, title: str, author: str, 
                 publication_year: int):
        self._item_id = item_id
        self._title = title
        self._author = author
        self._publication_year = publication_year
        self._is_available = True
        self._observers: List[Callable[[str], None]] = []
    
    @property
    def item_id(self) -> str:
        return self._item_id
    
    @property
    def title(self) -> str:
        return self._title
    
    @property
    def author(self) -> str:
        return self._author
    
    @property
    def publication_year(self) -> int:
        return self._publication_year
    
    @property
    def is_available(self) -> bool:
        return self._is_available
    
    @is_available.setter
    def is_available(self, value: bool) -> None:
        old_value = self._is_available
        self._is_available = value
        # Notify observers when item becomes available
        if not old_value and value:
            self._notify_observers(
                f"Item '{self._title}' (ID: {self._item_id}) is now available!"
            )
    
    def attach_observer(self, observer: Callable[[str], None]) -> None:
        """Attach an observer to be notified of availability changes."""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach_observer(self, observer: Callable[[str], None]) -> None:
        """Detach an observer from notifications."""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def _notify_observers(self, message: str) -> None:
        """Notify all observers with a message."""
        for observer in self._observers:
            observer(message)
    
    @abstractmethod
    def get_item_type(self) -> str:
        """Returns the type of catalogue item."""
        pass
    
    def __str__(self) -> str:
        status = "Available" if self._is_available else "On Loan"
        return (f"{self.get_item_type()}: '{self._title}' by {self._author} "
                f"({self._publication_year}) [{status}]")


class PhysicalBook(CatalogueItem):
    """
    Physical book catalogue item.
    
    Attributes:
        isbn: International Standard Book Number
        shelf_location: Physical location in library (e.g., "A-12-3")
        condition: Book condition (Excellent/Good/Fair/Poor)
    
    Properties:
        Loan period: 21 days (14 if condition is Poor)
        Reservable: Yes, except when condition is Poor
    """
    
    def __init__(self, item_id: str, title: str, author: str,
                 publication_year: int, isbn: str, shelf_location: str,
                 condition: str = "Excellent"):
        """
        Initialise a physical book.
        
        Args:
            condition: One of 'Excellent', 'Good', 'Fair', 'Poor'
        """
        super().__init__(item_id, title, author, publication_year)
        self._isbn = isbn
        self._shelf_location = shelf_location
        self._condition = condition.lower()
        
        if self._condition not in ("excellent", "good", "fair", "poor"):
            raise ValueError(f"Invalid condition: {condition}")
    
    @property
    def isbn(self) -> str:
        return self._isbn
    
    @property
    def shelf_location(self) -> str:
        return self._shelf_location
    
    @property
    def condition(self) -> str:
        return self._condition
    
    def calculate_loan_period(self) -> int:
        """Calculate loan period based on condition."""
        return 14 if self._condition == "poor" else 21
    
    def can_be_reserved(self) -> bool:
        """Physical books can be reserved unless in poor condition."""
        return self._condition != "poor"
    
    def get_reservation_priority(self) -> float:
        """Priority based on condition (fair = 1.5, others = 1.0)."""
        return 1.5 if self._condition == "fair" else 1.0
    
    def get_item_type(self) -> str:
        return "Physical Book"


class EBook(CatalogueItem):
    """
    Electronic book catalogue item.
    
    Attributes:
        file_format: Format type (PDF, EPUB, MOBI, etc.)
        file_size_mb: Size in megabytes
        drm_protected: Whether digital rights management is enabled
    
    Properties:
        Loan period: 14 days
        Reservable: Yes (unlimited concurrent access for eBooks)
    """
    
    def __init__(self, item_id: str, title: str, author: str,
                 publication_year: int, file_format: str,
                 file_size_mb: float, drm_protected: bool = True):
        """Initialise an eBook."""
        super().__init__(item_id, title, author, publication_year)
        self._file_format = file_format.upper()
        self._file_size_mb = file_size_mb
        self._drm_protected = drm_protected
    
    @property
    def file_format(self) -> str:
        return self._file_format
    
    @property
    def file_size_mb(self) -> float:
        return self._file_size_mb
    
    @property
    def drm_protected(self) -> bool:
        return self._drm_protected
    
    def calculate_loan_period(self) -> int:
        """eBooks have standard 14-day loan period."""
        return 14
    
    def can_be_reserved(self) -> bool:
        """eBooks can always be reserved."""
        return True
    
    def get_reservation_priority(self) -> float:
        """Standard priority for eBooks."""
        return 1.0
    
    def get_item_type(self) -> str:
        return "EBook"


class Audiobook(CatalogueItem):
    """
    Audiobook catalogue item.
    
    Attributes:
        narrator: Name of narrating voice actor
        duration_minutes: Total length in minutes
        chapter_count: Number of chapters
    
    Properties:
        Loan period: 14 days
        Reservable: Yes
    """
    
    def __init__(self, item_id: str, title: str, author: str,
                 publication_year: int, narrator: str,
                 duration_minutes: int, chapter_count: int):
        """Initialise an audiobook."""
        super().__init__(item_id, title, author, publication_year)
        self._narrator = narrator
        self._duration_minutes = duration_minutes
        self._chapter_count = chapter_count
    
    @property
    def narrator(self) -> str:
        return self._narrator
    
    @property
    def duration_minutes(self) -> int:
        return self._duration_minutes
    
    @property
    def chapter_count(self) -> int:
        return self._chapter_count
    
    def calculate_loan_period(self) -> int:
        """Audiobooks have standard 14-day loan period."""
        return 14
    
    def can_be_reserved(self) -> bool:
        """Audiobooks can be reserved."""
        return True
    
    def get_reservation_priority(self) -> float:
        """Standard priority for audiobooks."""
        return 1.0
    
    def get_item_type(self) -> str:
        return "Audiobook"


class AcademicJournal(CatalogueItem):
    """
    Academic journal catalogue item.
    
    Attributes:
        journal_name: Name of the journal
        volume: Volume number
        issue: Issue number
        impact_factor: Journal impact factor (for priority)
        peer_reviewed: Whether article is peer-reviewed
    
    Properties:
        Loan period: 7 days (non-renewable)
        Reservable: Only for peer-reviewed articles
        Priority weight: impact_factor × 10
    """
    
    def __init__(self, item_id: str, title: str, author: str,
                 publication_year: int, journal_name: str, volume: int,
                 issue: int, impact_factor: float, peer_reviewed: bool = True):
        """Initialise an academic journal."""
        super().__init__(item_id, title, author, publication_year)
        self._journal_name = journal_name
        self._volume = volume
        self._issue = issue
        self._impact_factor = impact_factor
        self._peer_reviewed = peer_reviewed
    
    @property
    def journal_name(self) -> str:
        return self._journal_name
    
    @property
    def volume(self) -> int:
        return self._volume
    
    @property
    def issue(self) -> int:
        return self._issue
    
    @property
    def impact_factor(self) -> float:
        return self._impact_factor
    
    @property
    def peer_reviewed(self) -> bool:
        return self._peer_reviewed
    
    def calculate_loan_period(self) -> int:
        """Academic journals have short 7-day non-renewable loan period."""
        return 7
    
    def can_be_reserved(self) -> bool:
        """Academic journals can be reserved only if peer-reviewed."""
        return self._peer_reviewed
    
    def get_reservation_priority(self) -> float:
        """Priority weighted by impact factor."""
        return self._impact_factor * 10
    
    def get_item_type(self) -> str:
        return "Academic Journal"


# ============================================================================
# SECTION 4: MEMBER HIERARCHY
# ============================================================================

class Member(ABC):
    """Abstract base class for library members."""
    
    def __init__(self, member_id: str, name: str, email: str, 
                 join_date: date):
        self._member_id = member_id
        self._name = name
        self._email = email
        self._join_date = join_date
        self._active_loans: List[CatalogueItem] = []
        self._outstanding_fines: float = 0.0
        self._reservations: List[CatalogueItem] = []
    
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
    def active_loans(self) -> List[CatalogueItem]:
        return self._active_loans.copy()
    
    @property
    def outstanding_fines(self) -> float:
        return self._outstanding_fines
    
    @outstanding_fines.setter
    def outstanding_fines(self, value: float) -> None:
        self._outstanding_fines = max(0.0, value)
    
    @property
    def reservations(self) -> List[CatalogueItem]:
        return self._reservations.copy()
    
    @property
    @abstractmethod
    def max_loans(self) -> int:
        """Maximum number of active loans allowed."""
        pass
    
    @property
    @abstractmethod
    def reservation_limit(self) -> int:
        """Maximum number of reservations allowed."""
        pass
    
    @property
    @abstractmethod
    def late_fee_per_day(self) -> float:
        """Late fee charged per day overdue."""
        pass
    
    def is_new_member(self) -> bool:
        """Check if member joined within the last 30 days."""
        days_since_joining = (date.today() - self._join_date).days
        return days_since_joining <= 30
    
    def can_borrow(self) -> bool:
        """Check if member can borrow new items."""
        return (len(self._active_loans) < self.max_loans and 
                self._outstanding_fines <= 10.0)
    
    def can_reserve(self) -> bool:
        """Check if member can make new reservations."""
        return len(self._reservations) < self.reservation_limit
    
    @abstractmethod
    def can_borrow_item(self, item: CatalogueItem) -> bool:
        """Check if member can borrow a specific item type."""
        pass
    
    def add_loan(self, item: CatalogueItem) -> None:
        """Add an item to active loans."""
        self._active_loans.append(item)
    
    def remove_loan(self, item: CatalogueItem) -> None:
        """Remove an item from active loans."""
        if item in self._active_loans:
            self._active_loans.remove(item)
    
    def add_reservation(self, item: CatalogueItem) -> None:
        """Add an item to reservations."""
        self._reservations.append(item)
    
    def remove_reservation(self, item: CatalogueItem) -> None:
        """Remove an item from reservations."""
        if item in self._reservations:
            self._reservations.remove(item)
    
    def receive_notification(self, message: str) -> None:
        """Receive a notification (observer callback)."""
        print(f"[NOTIFICATION to {self._name}]: {message}")
    
    def get_member_type(self) -> str:
        """Returns the type of member."""
        return self.__class__.__name__
    
    def __str__(self) -> str:
        return (f"{self.get_member_type()}: {self._name} "
                f"(ID: {self._member_id}, Loans: {len(self._active_loans)}/"
                f"{self.max_loans}, Fines: ${self._outstanding_fines:.2f})")


class StandardMember(Member):
    """
    Standard membership tier—basic library access.
    
    Privileges:
        Max loans: 5 active items
        Reservation limit: 2 items
        Late fee: $0.50 per day
        Cannot borrow: Academic journals
    """
    
    def __init__(self, member_id: str, name: str, email: str, join_date: date):
        """Initialise a Standard member."""
        super().__init__(member_id, name, email, join_date)
    
    @property
    def max_loans(self) -> int:
        return 5
    
    @property
    def reservation_limit(self) -> int:
        return 2
    
    @property
    def late_fee_per_day(self) -> float:
        return 0.50
    
    def can_borrow_item(self, item: CatalogueItem) -> bool:
        """Standard members cannot borrow academic journals."""
        return not isinstance(item, AcademicJournal)


class PremiumMember(Member):
    """
    Premium membership tier—enhanced library access.
    
    Privileges:
        Max loans: 15 active items
        Reservation limit: 5 items
        Late fee: $0.25 per day
        Can borrow: All item types
    """
    
    def __init__(self, member_id: str, name: str, email: str, join_date: date):
        """Initialise a Premium member."""
        super().__init__(member_id, name, email, join_date)
    
    @property
    def max_loans(self) -> int:
        return 15
    
    @property
    def reservation_limit(self) -> int:
        return 5
    
    @property
    def late_fee_per_day(self) -> float:
        return 0.25
    
    def can_borrow_item(self, item: CatalogueItem) -> bool:
        """Premium members can borrow all item types."""
        return True


class AcademicMember(Member):
    """
    Academic membership tier—researcher/student access.
    
    Privileges:
        Max loans: 25 active items
        Reservation limit: 10 items
        Late fee: $0.00 (exempt)
        Can borrow: Academic journals (peer-reviewed only)
    """
    
    def __init__(self, member_id: str, name: str, email: str, join_date: date):
        """Initialise an Academic member."""
        super().__init__(member_id, name, email, join_date)
    
    @property
    def max_loans(self) -> int:
        return 25
    
    @property
    def reservation_limit(self) -> int:
        return 10
    
    @property
    def late_fee_per_day(self) -> float:
        return 0.0  # Exempt from late fees
    
    def can_borrow_item(self, item: CatalogueItem) -> bool:
        """Academic members can borrow all items."""
        # Special restriction: academic journals must be peer-reviewed
        if isinstance(item, AcademicJournal):
            return item.peer_reviewed
        return True


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


class LibraryRegistry(metaclass=RegistryMeta):
    """
    Central registry for managing library catalogue and members.
    Implemented as a Singleton to ensure data consistency.
    """
    
    def __init__(self):
        self._catalogue: Dict[str, CatalogueItem] = {}
        self._members: Dict[str, Member] = {}
        self._admin_observers: List[Callable[[str], None]] = []
    
    def add_item(self, item: CatalogueItem) -> None:
        """Add an item to the catalogue."""
        self._catalogue[item.item_id] = item
    
    def get_item(self, item_id: str) -> CatalogueItem:
        """Retrieve an item from the catalogue."""
        if item_id not in self._catalogue:
            raise ItemNotFoundError(item_id)
        return self._catalogue[item_id]
    
    def add_member(self, member: Member) -> None:
        """Add a member to the directory."""
        self._members[member.member_id] = member
    
    def get_member(self, member_id: str) -> Member:
        """Retrieve a member from the directory."""
        if member_id not in self._members:
            raise MemberNotFoundError(member_id)
        return self._members[member_id]
    
    def attach_admin_observer(self, observer: Callable[[str], None]) -> None:
        """Attach an admin observer for system notifications."""
        if observer not in self._admin_observers:
            self._admin_observers.append(observer)
    
    def notify_admins(self, message: str) -> None:
        """Notify all admin observers."""
        for observer in self._admin_observers:
            observer(message)
    
    def get_all_items(self) -> List[CatalogueItem]:
        """Get all items in the catalogue."""
        return list(self._catalogue.values())
    
    def get_all_members(self) -> List[Member]:
        """Get all registered members."""
        return list(self._members.values())


# --- Factory Pattern ---
class CatalogueItemFactory:
    """
    Factory for creating catalogue items.
    Centralizes object creation and validates parameters.
    """
    
    @staticmethod
    def create_item(item_type: str, **kwargs) -> CatalogueItem:
        """
        Create a catalogue item based on type.
        
        Parameters:
            item_type: One of 'physical', 'ebook', 'audiobook', 'journal'
            **kwargs: Required parameters for the item type:
                Common: item_id, title, author, publication_year
                Physical: isbn, shelf_location, condition (optional)
                EBook: file_format, file_size_mb, drm_protected (optional)
                Audiobook: narrator, duration_minutes, chapter_count
                Journal: journal_name, volume, issue, impact_factor, peer_reviewed (optional)
        
        Returns:
            CatalogueItem: The created item
            
        Raises:
            CatalogueError: If item type is unknown or required parameters missing
        """
        item_type_lower = item_type.lower()
        
        # Validate common required parameters
        required_common = ['item_id', 'title', 'author', 'publication_year']
        for param in required_common:
            if param not in kwargs:
                raise CatalogueError(f"Missing required parameter: {param}")
        
        if item_type_lower == 'physical':
            required = ['isbn', 'shelf_location']
            for param in required:
                if param not in kwargs:
                    raise CatalogueError(f"PhysicalBook requires parameter: {param}")
            return PhysicalBook(
                kwargs['item_id'], kwargs['title'], kwargs['author'],
                kwargs['publication_year'], kwargs['isbn'],
                kwargs['shelf_location'],
                condition=kwargs.get('condition', 'Excellent')
            )
        
        elif item_type_lower == 'ebook':
            required = ['file_format', 'file_size_mb']
            for param in required:
                if param not in kwargs:
                    raise CatalogueError(f"EBook requires parameter: {param}")
            return EBook(
                kwargs['item_id'], kwargs['title'], kwargs['author'],
                kwargs['publication_year'], kwargs['file_format'],
                kwargs['file_size_mb'],
                drm_protected=kwargs.get('drm_protected', True)
            )
        
        elif item_type_lower == 'audiobook':
            required = ['narrator', 'duration_minutes', 'chapter_count']
            for param in required:
                if param not in kwargs:
                    raise CatalogueError(f"Audiobook requires parameter: {param}")
            return Audiobook(
                kwargs['item_id'], kwargs['title'], kwargs['author'],
                kwargs['publication_year'], kwargs['narrator'],
                kwargs['duration_minutes'], kwargs['chapter_count']
            )
        
        elif item_type_lower == 'journal':
            required = ['journal_name', 'volume', 'issue', 'impact_factor']
            for param in required:
                if param not in kwargs:
                    raise CatalogueError(f"AcademicJournal requires parameter: {param}")
            return AcademicJournal(
                kwargs['item_id'], kwargs['title'], kwargs['author'],
                kwargs['publication_year'], kwargs['journal_name'],
                kwargs['volume'], kwargs['issue'], kwargs['impact_factor'],
                peer_reviewed=kwargs.get('peer_reviewed', True)
            )
        
        else:
            raise CatalogueError(
                f"Unknown catalogue item type: {item_type}. "
                f"Must be one of: physical, ebook, audiobook, journal"
            )


# --- Adapter Pattern ---
class LegacyCatalogueAdapter:
    """
    Adapter to convert legacy catalogue data format to modern CatalogueItem objects.
    
    Legacy format example:
    {
        "book_code": "LB-001",
        "book_title": "Design Patterns",
        "writer": "Gang of Four",
        "year_published": 1994,
        "book_type": "physical",
        "rack_position": "A-12-3",
        "book_condition": "good"
    }
    """
    
    def __init__(self, factory: CatalogueItemFactory):
        self._factory = factory
        self._field_mappings = {
            "book_code": "item_id",
            "book_title": "title",
            "writer": "author",
            "year_published": "publication_year",
            "book_type": "item_type",
            "rack_position": "shelf_location",
            "book_condition": "condition"
        }
    
    def adapt(self, legacy_data: Dict) -> CatalogueItem:
        """
        Convert legacy data format to a modern CatalogueItem.
        
        Legacy format fields:
            book_code → item_id
            book_title → title
            writer → author
            year_published → publication_year
            book_type → item_type (supports legacy types)
            rack_position → shelf_location
            book_condition → condition
        
        Parameters:
            legacy_data: Dictionary in legacy format
        
        Returns:
            CatalogueItem: Converted modern item
            
        Raises:
            LegacyDataFormatError: If required fields missing or invalid
        """
        # Validate required fields
        required_fields = ['book_code', 'book_title', 'writer', 'year_published', 'book_type']
        for field in required_fields:
            if field not in legacy_data:
                raise LegacyDataFormatError(field, "required field", "missing")
        
        # Map legacy data to modern format
        modern_data = {
            'item_id': legacy_data['book_code'],
            'title': legacy_data['book_title'],
            'author': legacy_data['writer'],
            'publication_year': legacy_data['year_published']
        }
        
        # Map item type (legacy might use different codes)
        legacy_type = legacy_data['book_type'].lower()
        type_mapping = {
            'physical': 'physical',
            'book': 'physical',
            'pb': 'physical',
            'ebook': 'ebook',
            'e-book': 'ebook',
            'eb': 'ebook',
            'audiobook': 'audiobook',
            'audio': 'audiobook',
            'ab': 'audiobook',
            'journal': 'journal',
            'academic': 'journal',
            'aj': 'journal'
        }
        
        if legacy_type not in type_mapping:
            raise LegacyDataFormatError(
                'book_type', 
                f"one of {list(type_mapping.keys())}", 
                legacy_type
            )
        
        modern_type = type_mapping[legacy_type]
        
        # Add type-specific fields
        if modern_type == 'physical':
            modern_data['isbn'] = legacy_data.get('isbn', 'UNKNOWN')
            modern_data['shelf_location'] = legacy_data.get('rack_position', 'UNKNOWN')
            modern_data['condition'] = legacy_data.get('book_condition', 'Good').capitalize()
        
        elif modern_type == 'ebook':
            modern_data['file_format'] = legacy_data.get('file_format', 'PDF').upper()
            modern_data['file_size_mb'] = float(legacy_data.get('file_size_mb', 5.0))
            modern_data['drm_protected'] = legacy_data.get('drm_protected', True)
        
        elif modern_type == 'audiobook':
            modern_data['narrator'] = legacy_data.get('narrator', 'Unknown')
            modern_data['duration_minutes'] = int(legacy_data.get('duration_minutes', 600))
            modern_data['chapter_count'] = int(legacy_data.get('chapter_count', 1))
        
        elif modern_type == 'journal':
            modern_data['journal_name'] = legacy_data.get('journal_name', 'Unknown Journal')
            modern_data['volume'] = int(legacy_data.get('volume', 1))
            modern_data['issue'] = int(legacy_data.get('issue', 1))
            modern_data['impact_factor'] = float(legacy_data.get('impact_factor', 1.0))
            modern_data['peer_reviewed'] = legacy_data.get('peer_reviewed', True)
        
        # Create item using factory
        try:
            return self._factory.create_item(modern_type, **modern_data)
        except CatalogueError as e:
            raise LegacyDataFormatError('conversion', 'valid catalogue item', str(e))


# --- Observer Pattern ---
class ReservationQueue:
    """
    Manages reservation waitlist for catalogue items.
    Implements Observer pattern for availability notifications.
    """
    
    def __init__(self):
        self._queues: Dict[str, List[Member]] = {}  # item_id -> [members]
        self._hold_expiry: Dict[str, date] = {}  # item_id -> expiry date
    
    def add_reservation(self, member: Member, item: CatalogueItem) -> int:
        """
        Add a member to the reservation queue for an item.
        
        Validates:
        - Item can be reserved
        - Member can make reservations
        - Member not already in queue for this item
        
        Returns:
            int: Position in queue (1-indexed)
            
        Raises:
            ReservationConflictError: If reservation cannot be made
        """
        if not item.can_be_reserved():
            raise ReservationConflictError(
                member.member_id, item.item_id,
                "Item cannot be reserved"
            )
        
        if not member.can_reserve():
            raise ReservationConflictError(
                member.member_id, item.item_id,
                "Member has reached reservation limit"
            )
        
        # Initialize queue if needed
        if item.item_id not in self._queues:
            self._queues[item.item_id] = []
        
        # Check if member already in queue
        queue = self._queues[item.item_id]
        for existing_member in queue:
            if existing_member.member_id == member.member_id:
                raise ReservationConflictError(
                    member.member_id, item.item_id,
                    "Member already has reservation for this item"
                )
        
        # Add to queue and set expiry
        queue.append(member)
        self._hold_expiry[item.item_id] = date.today() + timedelta(days=7)
        
        member.add_reservation(item)
        return len(queue)
    
    def cancel_reservation(self, member: Member, item: CatalogueItem) -> bool:
        """
        Cancel a member's reservation for an item.
        
        Parameters:
            member: Member canceling the reservation
            item: Item to cancel reservation for
        
        Returns:
            bool: True if cancelled, False if not found in queue
        """
        if item.item_id not in self._queues:
            return False
        
        queue = self._queues[item.item_id]
        for i, queued_member in enumerate(queue):
            if queued_member.member_id == member.member_id:
                queue.pop(i)
                member.remove_reservation(item)
                return True
        
        return False
    
    def process_return(self, item: CatalogueItem) -> Optional[Member]:
        """
        Process an item return and notify next member in queue (FIFO).
        
        Parameters:
            item: Item being returned
        
        Returns:
            Optional[Member]: Next member in queue, or None if empty
        """
        if item.item_id not in self._queues:
            return None
        
        queue = self._queues[item.item_id]
        if not queue:
            return None
        
        # Get first member in queue (FIFO)
        next_member = queue.pop(0)
        next_member.remove_reservation(item)
        
        # Notify member
        next_member.receive_notification(
            f"Item '{item.title}' is now available! "
            f"Your reservation is ready for pickup."
        )
        
        return next_member
    
    def get_queue_position(self, member: Member, item: CatalogueItem) -> int:
        """Get member's position in queue (0 if not in queue)."""
        if item.item_id not in self._queues:
            return 0
        try:
            return self._queues[item.item_id].index(member) + 1
        except ValueError:
            return 0


# ============================================================================
# SECTION 6: TRANSACTION MANAGEMENT
# ============================================================================

class Transaction:
    """Represents a borrowing transaction."""
    
    def __init__(self, member: Member, item: CatalogueItem, 
                 borrow_date: date):
        self._transaction_id = str(uuid.uuid4())[:8]
        self._member = member
        self._item = item
        self._borrow_date = borrow_date
        self._due_date = borrow_date + timedelta(days=item.calculate_loan_period())
        self._returned_date: Optional[date] = None
        self._fine_amount: float = 0.0
    
    @property
    def transaction_id(self) -> str:
        return self._transaction_id
    
    @property
    def member(self) -> Member:
        return self._member
    
    @property
    def item(self) -> CatalogueItem:
        return self._item
    
    @property
    def borrow_date(self) -> date:
        return self._borrow_date
    
    @property
    def due_date(self) -> date:
        return self._due_date
    
    @property
    def returned_date(self) -> Optional[date]:
        return self._returned_date
    
    @returned_date.setter
    def returned_date(self, value: date) -> None:
        self._returned_date = value
    
    @property
    def fine_amount(self) -> float:
        return self._fine_amount
    
    @fine_amount.setter
    def fine_amount(self, value: float) -> None:
        self._fine_amount = max(0.0, value)
    
    def is_overdue(self, check_date: date = None) -> bool:
        """Check if transaction is overdue."""
        if check_date is None:
            check_date = date.today()
        return check_date > self._due_date and self._returned_date is None
    
    def days_overdue(self, check_date: date = None) -> int:
        """Calculate number of days overdue."""
        if check_date is None:
            check_date = date.today()
        if check_date <= self._due_date:
            return 0
        return (check_date - self._due_date).days
    
    def __str__(self) -> str:
        status = "Returned" if self._returned_date else "Active"
        return (f"Transaction {self._transaction_id}: {self._member.name} "
                f"borrowed '{self._item.title}' ({status})")


class BorrowingService:
    """
    Manages borrowing operations for the library.
    Implements business rules for loans, returns, and fines.
    """
    
    def __init__(self, registry: LibraryRegistry, 
                 reservation_queue: ReservationQueue):
        self._registry = registry
        self._reservation_queue = reservation_queue
        self._transactions: Dict[str, Transaction] = {}
    
    def borrow_item(self, member: Member, item: CatalogueItem) -> Transaction:
        """
        Process a borrowing transaction with comprehensive validation.
        
        Validates:
        - Member can borrow (under loan limit, reasonable fines)
        - Member can borrow specific item type
        - Item is available
        - Item can be borrowed (not on loan)
        
        Parameters:
            member: The member borrowing the item
            item: The item being borrowed
        
        Returns:
            Transaction: The created transaction
            
        Raises:
            LoanLimitExceededError: If member at loan limit
            OutstandingFinesError: If member has excessive fines
            ItemUnavailableError: If item not available
        """
        # Check if member can borrow
        if not member.can_borrow():
            if len(member.active_loans) >= member.max_loans:
                raise LoanLimitExceededError(
                    member.member_id,
                    f"Maximum {member.max_loans} loans reached"
                )
            if member.outstanding_fines > 10.0:
                raise OutstandingFinesError(
                    member.member_id,
                    f"Outstanding fines: ${member.outstanding_fines:.2f}"
                )
        
        # Check if member can borrow this specific item type
        if not member.can_borrow_item(item):
            raise EligibilityError(
                member.member_id, item.item_id,
                f"Member not eligible to borrow {item.get_item_type()}"
            )
        
        # Check if item is available
        if not item.is_available:
            raise ItemUnavailableError(item.item_id, "Item is currently on loan")
        
        # Create transaction
        transaction = Transaction(member, item, date.today())
        
        # Update state
        item.is_available = False
        member.add_loan(item)
        self._transactions[transaction.transaction_id] = transaction
        
        # Remove from reservation queue if present
        self._reservation_queue.cancel_reservation(member, item)
        
        # Notify admins
        self._registry.notify_admins(
            f"NEW LOAN: {member.name} borrowed '{item.title}' "
            f"(Transaction: {transaction.transaction_id})"
        )
        
        return transaction
    
    def return_item(self, member: Member, item: CatalogueItem, 
                    return_date: date = None) -> float:
        """
        Process a return transaction and calculate fines.
        
        Handles:
        - Validating member has item on loan
        - Calculating late fees (with new member discount)
        - Marking item as available
        - Processing reservation queue
        
        Parameters:
            member: The member returning the item
            item: The item being returned
            return_date: Date of return (defaults to today)
        
        Returns:
            float: Fine amount charged (0.0 if none)
            
        Raises:
            InvalidReturnError: If member doesn't have this item on loan
        """
        if return_date is None:
            return_date = date.today()
        
        # Find transaction
        transaction = None
        for txn in self._transactions.values():
            if (txn.member.member_id == member.member_id and 
                txn.item.item_id == item.item_id and 
                txn.returned_date is None):
                transaction = txn
                break
        
        if transaction is None:
            raise InvalidReturnError(
                member.member_id,
                f"Member does not have '{item.title}' on loan"
            )
        
        # Calculate fine
        days_overdue = transaction.days_overdue(return_date)
        fine_amount = self.calculate_fine(member, item, days_overdue)
        
        # Update transaction
        transaction.returned_date = return_date
        transaction.fine_amount = fine_amount
        
        # Update state
        item.is_available = True
        member.remove_loan(item)
        member.outstanding_fines += fine_amount
        
        # Process reservation queue
        next_member = self._reservation_queue.process_return(item)
        
        # Notify admins
        status = f"Fine: ${fine_amount:.2f}" if fine_amount > 0 else "No fine"
        self._registry.notify_admins(
            f"RETURN: {member.name} returned '{item.title}' ({status})"
        )
        
        return fine_amount
    
    def calculate_fine(self, member: Member, item: CatalogueItem, 
                       days_overdue: int) -> float:
        """
        Calculate fine for an overdue item.
        
        Applies 10% discount for new members (joined within 30 days).
        """
        if days_overdue <= 0:
            return 0.0
        
        base_fine = days_overdue * member.late_fee_per_day
        
        # Apply new member discount
        if member.is_new_member():
            base_fine *= 0.9
        
        return round(base_fine, 2)
    
    def get_member_transactions(self, member: Member) -> List[Transaction]:
        """Get all transactions for a member."""
        return [t for t in self._transactions.values() 
                if t.member.member_id == member.member_id]


# ============================================================================
# SECTION 7: RESERVATION SYSTEM
# ============================================================================

# ReservationQueue class is defined in Section 5 (Design Patterns)
# Additional reservation helper methods can be added here if needed


# ============================================================================
# SECTION 8: MAIN DEMONSTRATION
# ============================================================================

def main():
    """
    Comprehensive demonstration of the BookHaven Library Management System.
    
    Showcases:
    - Singleton pattern for registry
    - Factory pattern for item creation
    - Adapter pattern for legacy data conversion
    - Observer pattern for reservation notifications
    - Member tier system with different privileges
    - Borrowing and returning with fine calculation
    - Reservation queue management
    """
    print("=" * 70)
    print("BookHaven Library Management System - Demonstration")
    print("=" * 70)
    
    # ================================================================
    # 1. SINGLETON PATTERN VERIFICATION
    # ================================================================
    print("\n1. SINGLETON PATTERN VERIFICATION")
    print("-" * 70)
    reg1 = LibraryRegistry()
    reg2 = LibraryRegistry()
    print(f"   Same instance: {reg1 is reg2}")  # Should be True
    print("   ✓ LibraryRegistry singleton verified")
    
    # ================================================================
    # 2. CREATE ITEMS USING FACTORY
    # ================================================================
    print("\n2. FACTORY PATTERN - CREATING CATALOGUE ITEMS")
    print("-" * 70)
    factory = CatalogueItemFactory()
    
    # Create physical books
    book1 = factory.create_item(
        'physical', item_id='PB-001', title='Clean Code',
        author='Robert C. Martin', publication_year=2008,
        isbn='978-0132350884', shelf_location='A-12-3',
        condition='Excellent'
    )
    reg1.add_item(book1)
    print(f"   {book1}")
    
    book2 = factory.create_item(
        'physical', item_id='PB-002', title='Design Patterns',
        author='Gang of Four', publication_year=1994,
        isbn='978-0201633610', shelf_location='A-12-4',
        condition='Poor'
    )
    reg1.add_item(book2)
    print(f"   {book2}")
    
    # Create eBook
    ebook = factory.create_item(
        'ebook', item_id='EB-001', title='Python Crash Course',
        author='Eric Matthes', publication_year=2019,
        file_format='PDF', file_size_mb=45.3, drm_protected=True
    )
    reg1.add_item(ebook)
    print(f"   {ebook}")
    
    # Create audiobook
    audiobook = factory.create_item(
        'audiobook', item_id='AB-001', title='The Great Gatsby',
        author='F. Scott Fitzgerald', publication_year=2013,
        narrator='Jake Gyllenhaal', duration_minutes=1260, chapter_count=9
    )
    reg1.add_item(audiobook)
    print(f"   {audiobook}")
    
    # Create academic journal
    journal = factory.create_item(
        'journal', item_id='AJ-001',
        title='Machine Learning in Software Engineering',
        author='Various', publication_year=2023,
        journal_name='IEEE Software', volume=40, issue=2,
        impact_factor=2.5, peer_reviewed=True
    )
    reg1.add_item(journal)
    print(f"   {journal}")
    
    # ================================================================
    # 3. LEGACY DATA ADAPTER
    # ================================================================
    print("\n3. ADAPTER PATTERN - LEGACY DATA CONVERSION")
    print("-" * 70)
    adapter = LegacyCatalogueAdapter(factory)
    
    legacy_data = {
        "book_code": "LB-001",
        "book_title": "The Pragmatic Programmer",
        "writer": "David Thomas and Andrew Hunt",
        "year_published": 1999,
        "book_type": "pb",
        "rack_position": "A-15-2",
        "book_condition": "good",
        "isbn": "978-0201616224"
    }
    
    try:
        adapted_book = adapter.adapt(legacy_data)
        reg1.add_item(adapted_book)
        print(f"   ✓ Adapted legacy book: {adapted_book}")
    except LegacyDataFormatError as e:
        print(f"   ✗ Adaptation error: {e}")
    
    # ================================================================
    # 4. CREATE MEMBERS OF DIFFERENT TIERS
    # ================================================================
    print("\n4. MEMBER TIER SYSTEM")
    print("-" * 70)
    
    standard_member = StandardMember(
        "M-001", "Alice Johnson", "alice@example.com", 
        date.today() - timedelta(days=345)
    )
    reg1.add_member(standard_member)
    print(f"   {standard_member}")
    
    premium_member = PremiumMember(
        "M-002", "Bob Smith", "bob@example.com",
        date.today() - timedelta(days=200)
    )
    reg1.add_member(premium_member)
    print(f"   {premium_member}")
    
    new_academic_member = AcademicMember(
        "M-003", "Carol Davis", "carol@example.com",
        date.today() - timedelta(days=15)  # New member
    )
    reg1.add_member(new_academic_member)
    print(f"   {new_academic_member}")
    
    # ================================================================
    # 5. BORROWING SYSTEM
    # ================================================================
    print("\n5. BORROWING SYSTEM AND TRANSACTIONS")
    print("-" * 70)
    
    reservation_queue = ReservationQueue()
    service = BorrowingService(reg1, reservation_queue)
    
    # Standard member borrows a book
    try:
        txn1 = service.borrow_item(standard_member, book1)
        print(f"   ✓ {standard_member.name} borrowed '{book1.title}'")
        print(f"     Transaction ID: {txn1.transaction_id}")
        print(f"     Due date: {txn1.due_date}")
    except (ItemUnavailableError, LoanLimitExceededError) as e:
        print(f"   ✗ Borrow failed: {e}")
    
    # Premium member borrows academic journal
    try:
        txn2 = service.borrow_item(premium_member, journal)
        print(f"   ✓ {premium_member.name} borrowed '{journal.title}'")
    except (ItemUnavailableError, LoanLimitExceededError) as e:
        print(f"   ✗ Borrow failed: {e}")
    
    # Try to borrow restricted item (Standard can't borrow academic journal)
    try:
        txn3 = service.borrow_item(standard_member, journal)
        print(f"   ✓ {standard_member.name} borrowed '{journal.title}'")
    except EligibilityError as e:
        print(f"   ✗ Eligibility check: {e}")
    
    # ================================================================
    # 6. RETURN PROCESSING AND FINES
    # ================================================================
    print("\n6. RETURN PROCESSING AND FINE CALCULATION")
    print("-" * 70)
    
    # Return with NO fine
    fine = service.return_item(standard_member, book1, date.today())
    print(f"   {standard_member.name} returned '{book1.title}'")
    print(f"   Fine: ${fine:.2f}")
    
    # Return with late fine (simulated)
    overdue_date = date.today() + timedelta(days=5)
    fine = service.return_item(premium_member, journal, overdue_date)
    print(f"   {premium_member.name} returned '{journal.title}' (5 days late)")
    print(f"   Fine: ${fine:.2f}")
    
    # ================================================================
    # 7. NEW MEMBER DISCOUNT VERIFICATION
    # ================================================================
    print("\n7. NEW MEMBER DISCOUNT (10% off late fees)")
    print("-" * 70)
    
    # New academic member (within 30 days)
    txn = service.borrow_item(new_academic_member, ebook)
    overdue_return = date.today() + timedelta(days=10)
    fine_with_discount = service.return_item(
        new_academic_member, ebook, overdue_return
    )
    
    print(f"   {new_academic_member.name} is a new member (with 10% discount)")
    print(f"   Item returned 10 days late")
    print(f"   Fine with 10% new member discount: ${fine_with_discount:.2f}")
    
    # ================================================================
    # 8. RESERVATION QUEUE
    # ================================================================
    print("\n8. RESERVATION QUEUE - FIFO PROCESSING")
    print("-" * 70)
    
    # Add members to reservation queue
    try:
        pos1 = reservation_queue.add_reservation(standard_member, book1)
        print(f"   {standard_member.name} added to queue for '{book1.title}'")
        print(f"   Position: {pos1}")
        
        pos2 = reservation_queue.add_reservation(premium_member, book1)
        print(f"   {premium_member.name} added to queue for '{book1.title}'")
        print(f"   Position: {pos2}")
    except ReservationConflictError as e:
        print(f"   ✗ Reservation error: {e}")
    
    # Process return (should notify next in queue)
    print(f"   Processing return of '{book1.title}'...")
    next_member = reservation_queue.process_return(book1)
    if next_member:
        print(f"   ✓ Next member notified: {next_member.name}")
    
    # ================================================================
    # 9. ADMINISTRATIVE FEATURES
    # ================================================================
    print("\n9. ADMINISTRATIVE SUMMARY")
    print("-" * 70)
    
    all_items = reg1.get_all_items()
    available_items = [item for item in all_items if item.is_available]
    
    print(f"   Total catalogue items: {len(all_items)}")
    print(f"   Available items: {len(available_items)}")
    print(f"   Items on loan: {len(all_items) - len(available_items)}")
    
    print(f"   Total members: {len(reg1.get_all_members())}")
    
    # Show member details
    print(f"\n   Member Details:")
    for member in reg1.get_all_members():
        print(f"      {member}")
        print(f"         Outstanding fines: ${member.outstanding_fines:.2f}")
        print(f"         Can borrow: {member.can_borrow()}")
    
    # ================================================================
    # SUMMARY
    # ================================================================
    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("  ✓ Singleton pattern (single registry instance)")
    print("  ✓ Factory pattern (item creation by type)")
    print("  ✓ Adapter pattern (legacy data conversion)")
    print("  ✓ Observer pattern (reservation notifications)")
    print("  ✓ Member tiers with different privileges")
    print("  ✓ Borrowing transactions with validation")
    print("  ✓ Fine calculation with new member discount")
    print("  ✓ Reservation queue with FIFO processing")
    print("=" * 70)


if __name__ == "__main__":
    main()
