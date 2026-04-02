"""
NIT2112 Object-Oriented Programming
COMPLETE EXAMPLE: GourmetBite Restaurant Order Management System

This is a COMPLETE working example demonstrating all OOP concepts:
- Encapsulation, Inheritance, Polymorphism, Abstraction
- Design Patterns: Factory, Adapter, Observer, Singleton
- Custom Exception Hierarchy
- Complex Business Rules

Students can use this as a reference for understanding how concepts integrate.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Callable, Tuple
from enum import Enum
import uuid


# ============================================================================
# SECTION 1: ENUMS AND CONSTANTS
# ============================================================================

class MenuCategory(Enum):
    """Categories of menu items."""
    APPETIZER = "appetizer"
    MAIN_COURSE = "main_course"
    DESSERT = "dessert"
    BEVERAGE = "beverage"


class OrderStatus(Enum):
    """Status of an order."""
    PENDING = "pending"
    PREPARING = "preparing"
    READY = "ready"
    SERVED = "served"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TableStatus(Enum):
    """Status of a restaurant table."""
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    CLEANING = "cleaning"


class DietaryTag(Enum):
    """Dietary restriction tags."""
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    GLUTEN_FREE = "gluten_free"
    DAIRY_FREE = "dairy_free"
    NUT_FREE = "nut_free"
    HALAL = "halal"


# ============================================================================
# SECTION 2: CUSTOM EXCEPTIONS
# ============================================================================

class RestaurantError(Exception):
    """Base exception for all restaurant-related errors."""
    pass


class MenuError(RestaurantError):
    """Base exception for menu-related errors."""
    pass


class ItemNotFoundError(MenuError):
    """Raised when a menu item cannot be found."""
    def __init__(self, item_id: str):
        self.item_id = item_id
        super().__init__(f"Menu item '{item_id}' not found.")


class ItemUnavailableError(MenuError):
    """Raised when a menu item is not available."""
    def __init__(self, item_name: str, reason: str = "out of stock"):
        self.item_name = item_name
        self.reason = reason
        super().__init__(f"'{item_name}' is currently unavailable: {reason}")


class OrderError(RestaurantError):
    """Base exception for order-related errors."""
    pass


class OrderNotFoundError(OrderError):
    """Raised when an order cannot be found."""
    def __init__(self, order_id: str):
        self.order_id = order_id
        super().__init__(f"Order '{order_id}' not found.")


class InvalidOrderError(OrderError):
    """Raised when an order operation is invalid."""
    def __init__(self, order_id: str, reason: str):
        self.order_id = order_id
        self.reason = reason
        super().__init__(f"Invalid operation on order '{order_id}': {reason}")


class TableError(RestaurantError):
    """Base exception for table-related errors."""
    pass


class TableNotFoundError(TableError):
    """Raised when a table cannot be found."""
    def __init__(self, table_id: str):
        self.table_id = table_id
        super().__init__(f"Table '{table_id}' not found.")


class TableUnavailableError(TableError):
    """Raised when a table is not available."""
    def __init__(self, table_id: str, status: TableStatus):
        self.table_id = table_id
        self.status = status
        super().__init__(f"Table '{table_id}' is {status.value}.")


class StaffError(RestaurantError):
    """Base exception for staff-related errors."""
    pass


class StaffNotFoundError(StaffError):
    """Raised when a staff member cannot be found."""
    def __init__(self, staff_id: str):
        self.staff_id = staff_id
        super().__init__(f"Staff member '{staff_id}' not found.")


class IntegrationError(RestaurantError):
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

class Orderable(ABC):
    """Interface for items that can be ordered."""
    
    @abstractmethod
    def get_price(self) -> float:
        """Get the price of the item."""
        pass
    
    @abstractmethod
    def get_preparation_time(self) -> int:
        """Get preparation time in minutes."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if item is currently available."""
        pass


class Customizable(ABC):
    """Interface for items that can be customized."""
    
    @abstractmethod
    def add_modification(self, modification: str) -> None:
        """Add a modification to the item."""
        pass
    
    @abstractmethod
    def get_modifications(self) -> List[str]:
        """Get all modifications."""
        pass
    
    @abstractmethod
    def calculate_modification_cost(self) -> float:
        """Calculate additional cost from modifications."""
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
# SECTION 4: MENU ITEM HIERARCHY
# ============================================================================

class MenuItem(Orderable, Customizable):
    """Abstract base class for all menu items."""
    
    MODIFICATION_COST = 1.50  # Cost per modification
    
    def __init__(self, item_id: str, name: str, description: str,
                 base_price: float, dietary_tags: List[DietaryTag] = None):
        self._item_id = item_id
        self._name = name
        self._description = description
        self._base_price = base_price
        self._dietary_tags = dietary_tags or []
        self._is_available = True
        self._modifications: List[str] = []
    
    @property
    def item_id(self) -> str:
        return self._item_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def base_price(self) -> float:
        return self._base_price
    
    @property
    def dietary_tags(self) -> List[DietaryTag]:
        return self._dietary_tags.copy()
    
    # Orderable interface
    def get_price(self) -> float:
        """Get total price including modifications."""
        return self._base_price + self.calculate_modification_cost()
    
    def is_available(self) -> bool:
        return self._is_available
    
    def set_availability(self, available: bool) -> None:
        self._is_available = available
    
    # Customizable interface
    def add_modification(self, modification: str) -> None:
        self._modifications.append(modification)
    
    def get_modifications(self) -> List[str]:
        return self._modifications.copy()
    
    def calculate_modification_cost(self) -> float:
        return len(self._modifications) * self.MODIFICATION_COST
    
    def has_dietary_tag(self, tag: DietaryTag) -> bool:
        """Check if item has a specific dietary tag."""
        return tag in self._dietary_tags
    
    @property
    @abstractmethod
    def category(self) -> MenuCategory:
        """Get the menu category."""
        pass
    
    @abstractmethod
    def get_preparation_time(self) -> int:
        """Get preparation time in minutes."""
        pass
    
    def __str__(self) -> str:
        tags = ", ".join(t.value for t in self._dietary_tags) if self._dietary_tags else "None"
        return f"{self._name} (${self._base_price:.2f}) - {tags}"


class Appetizer(MenuItem):
    """Appetizer menu item."""
    
    BASE_PREP_TIME = 10  # minutes
    
    def __init__(self, item_id: str, name: str, description: str,
                 base_price: float, is_shareable: bool = False,
                 dietary_tags: List[DietaryTag] = None):
        super().__init__(item_id, name, description, base_price, dietary_tags)
        self._is_shareable = is_shareable
    
    @property
    def is_shareable(self) -> bool:
        return self._is_shareable
    
    @property
    def category(self) -> MenuCategory:
        return MenuCategory.APPETIZER
    
    def get_preparation_time(self) -> int:
        return self.BASE_PREP_TIME


class MainCourse(MenuItem):
    """Main course menu item."""
    
    BASE_PREP_TIME = 25  # minutes
    
    def __init__(self, item_id: str, name: str, description: str,
                 base_price: float, protein_type: str,
                 cooking_style: str = "grilled",
                 dietary_tags: List[DietaryTag] = None):
        super().__init__(item_id, name, description, base_price, dietary_tags)
        self._protein_type = protein_type
        self._cooking_style = cooking_style
    
    @property
    def protein_type(self) -> str:
        return self._protein_type
    
    @property
    def cooking_style(self) -> str:
        return self._cooking_style
    
    @cooking_style.setter
    def cooking_style(self, value: str) -> None:
        valid_styles = ["grilled", "fried", "steamed", "baked", "raw"]
        if value.lower() not in valid_styles:
            raise ValueError(f"Invalid cooking style. Choose from: {valid_styles}")
        self._cooking_style = value.lower()
    
    @property
    def category(self) -> MenuCategory:
        return MenuCategory.MAIN_COURSE
    
    def get_preparation_time(self) -> int:
        # Different cooking styles have different prep times
        style_times = {
            "grilled": 25,
            "fried": 20,
            "steamed": 30,
            "baked": 35,
            "raw": 10
        }
        return style_times.get(self._cooking_style, self.BASE_PREP_TIME)


class Dessert(MenuItem):
    """Dessert menu item."""
    
    BASE_PREP_TIME = 8  # minutes
    
    def __init__(self, item_id: str, name: str, description: str,
                 base_price: float, is_cold: bool = True,
                 contains_alcohol: bool = False,
                 dietary_tags: List[DietaryTag] = None):
        super().__init__(item_id, name, description, base_price, dietary_tags)
        self._is_cold = is_cold
        self._contains_alcohol = contains_alcohol
    
    @property
    def is_cold(self) -> bool:
        return self._is_cold
    
    @property
    def contains_alcohol(self) -> bool:
        return self._contains_alcohol
    
    @property
    def category(self) -> MenuCategory:
        return MenuCategory.DESSERT
    
    def get_preparation_time(self) -> int:
        # Hot desserts take longer
        return self.BASE_PREP_TIME + (5 if not self._is_cold else 0)


class Beverage(MenuItem):
    """Beverage menu item."""
    
    BASE_PREP_TIME = 3  # minutes
    
    def __init__(self, item_id: str, name: str, description: str,
                 base_price: float, size_ml: int = 330,
                 is_alcoholic: bool = False, is_hot: bool = False,
                 dietary_tags: List[DietaryTag] = None):
        super().__init__(item_id, name, description, base_price, dietary_tags)
        self._size_ml = size_ml
        self._is_alcoholic = is_alcoholic
        self._is_hot = is_hot
    
    @property
    def size_ml(self) -> int:
        return self._size_ml
    
    @property
    def is_alcoholic(self) -> bool:
        return self._is_alcoholic
    
    @property
    def is_hot(self) -> bool:
        return self._is_hot
    
    @property
    def category(self) -> MenuCategory:
        return MenuCategory.BEVERAGE
    
    def get_preparation_time(self) -> int:
        # Hot beverages take a bit longer
        return self.BASE_PREP_TIME + (2 if self._is_hot else 0)


# ============================================================================
# SECTION 5: STAFF HIERARCHY
# ============================================================================

class Staff(ABC):
    """Abstract base class for restaurant staff."""
    
    def __init__(self, staff_id: str, name: str, hourly_rate: float):
        self._staff_id = staff_id
        self._name = name
        self._hourly_rate = hourly_rate
        self._is_on_duty = False
        self._assigned_tables: List['Table'] = []
    
    @property
    def staff_id(self) -> str:
        return self._staff_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def hourly_rate(self) -> float:
        return self._hourly_rate
    
    @property
    def is_on_duty(self) -> bool:
        return self._is_on_duty
    
    @is_on_duty.setter
    def is_on_duty(self, value: bool) -> None:
        self._is_on_duty = value
    
    @property
    def assigned_tables(self) -> List['Table']:
        return self._assigned_tables.copy()
    
    @property
    @abstractmethod
    def role(self) -> str:
        """Get the staff member's role."""
        pass
    
    @property
    @abstractmethod
    def max_tables(self) -> int:
        """Maximum tables this staff can handle."""
        pass
    
    def can_take_table(self) -> bool:
        """Check if staff can take another table."""
        return len(self._assigned_tables) < self.max_tables
    
    def assign_table(self, table: 'Table') -> None:
        """Assign a table to this staff member."""
        if not self.can_take_table():
            raise StaffError(f"{self._name} cannot take more tables (max: {self.max_tables})")
        self._assigned_tables.append(table)
    
    def release_table(self, table: 'Table') -> None:
        """Release a table from this staff member."""
        if table in self._assigned_tables:
            self._assigned_tables.remove(table)
    
    def receive_notification(self, message: str) -> None:
        """Receive a notification."""
        print(f"[{self.role.upper()} - {self._name}]: {message}")
    
    def __str__(self) -> str:
        status = "On Duty" if self._is_on_duty else "Off Duty"
        return f"{self.role}: {self._name} ({status}, Tables: {len(self._assigned_tables)})"


class Waiter(Staff):
    """Waiter staff member."""
    
    def __init__(self, staff_id: str, name: str, hourly_rate: float = 18.0):
        super().__init__(staff_id, name, hourly_rate)
    
    @property
    def role(self) -> str:
        return "Waiter"
    
    @property
    def max_tables(self) -> int:
        return 4


class SeniorWaiter(Staff):
    """Senior waiter with more responsibilities."""
    
    def __init__(self, staff_id: str, name: str, hourly_rate: float = 24.0):
        super().__init__(staff_id, name, hourly_rate)
    
    @property
    def role(self) -> str:
        return "Senior Waiter"
    
    @property
    def max_tables(self) -> int:
        return 6
    
    def train_new_waiter(self, waiter: Waiter) -> str:
        """Train a new waiter (senior waiter responsibility)."""
        return f"{self._name} is training {waiter.name}"


class Chef(Staff):
    """Chef staff member."""
    
    def __init__(self, staff_id: str, name: str, specialty: str,
                 hourly_rate: float = 30.0):
        super().__init__(staff_id, name, hourly_rate)
        self._specialty = specialty
        self._current_orders: List['Order'] = []
    
    @property
    def specialty(self) -> str:
        return self._specialty
    
    @property
    def current_orders(self) -> List['Order']:
        return self._current_orders.copy()
    
    @property
    def role(self) -> str:
        return "Chef"
    
    @property
    def max_tables(self) -> int:
        return 0  # Chefs don't serve tables
    
    def accept_order(self, order: 'Order') -> None:
        """Accept an order for preparation."""
        self._current_orders.append(order)
    
    def complete_order(self, order: 'Order') -> None:
        """Mark an order as prepared."""
        if order in self._current_orders:
            self._current_orders.remove(order)


class HeadChef(Chef):
    """Head chef with additional responsibilities."""
    
    def __init__(self, staff_id: str, name: str, specialty: str = "all",
                 hourly_rate: float = 45.0):
        super().__init__(staff_id, name, specialty, hourly_rate)
    
    @property
    def role(self) -> str:
        return "Head Chef"
    
    def create_daily_special(self, name: str, price: float) -> MainCourse:
        """Create a daily special menu item."""
        special_id = f"SPECIAL-{datetime.now().strftime('%Y%m%d')}"
        return MainCourse(
            special_id, f"Chef's Special: {name}",
            f"Today's special created by {self._name}",
            price, "seasonal", "grilled"
        )


# ============================================================================
# SECTION 6: TABLE AND ORDER CLASSES
# ============================================================================

class Table:
    """Represents a restaurant table."""
    
    def __init__(self, table_id: str, capacity: int, location: str = "main"):
        self._table_id = table_id
        self._capacity = capacity
        self._location = location  # main, patio, private
        self._status = TableStatus.AVAILABLE
        self._current_order: Optional['Order'] = None
        self._assigned_waiter: Optional[Staff] = None
    
    @property
    def table_id(self) -> str:
        return self._table_id
    
    @property
    def capacity(self) -> int:
        return self._capacity
    
    @property
    def location(self) -> str:
        return self._location
    
    @property
    def status(self) -> TableStatus:
        return self._status
    
    @status.setter
    def status(self, value: TableStatus) -> None:
        self._status = value
    
    @property
    def current_order(self) -> Optional['Order']:
        return self._current_order
    
    @current_order.setter
    def current_order(self, order: Optional['Order']) -> None:
        self._current_order = order
    
    @property
    def assigned_waiter(self) -> Optional[Staff]:
        return self._assigned_waiter
    
    @assigned_waiter.setter
    def assigned_waiter(self, waiter: Optional[Staff]) -> None:
        self._assigned_waiter = waiter
    
    def is_available(self) -> bool:
        return self._status == TableStatus.AVAILABLE
    
    def seat_guests(self, party_size: int) -> None:
        """Seat guests at this table."""
        if party_size > self._capacity:
            raise TableError(f"Party size {party_size} exceeds capacity {self._capacity}")
        if not self.is_available():
            raise TableUnavailableError(self._table_id, self._status)
        self._status = TableStatus.OCCUPIED
    
    def clear_table(self) -> None:
        """Clear the table after guests leave."""
        self._status = TableStatus.CLEANING
        self._current_order = None
    
    def mark_ready(self) -> None:
        """Mark table as ready for new guests."""
        self._status = TableStatus.AVAILABLE
    
    def __str__(self) -> str:
        return f"Table {self._table_id} ({self._capacity} seats, {self._location}) - {self._status.value}"


class OrderItem:
    """Represents a single item in an order with quantity and modifications."""
    
    def __init__(self, menu_item: MenuItem, quantity: int = 1,
                 special_instructions: str = ""):
        self._menu_item = menu_item
        self._quantity = quantity
        self._special_instructions = special_instructions
        self._modifications: List[str] = []
    
    @property
    def menu_item(self) -> MenuItem:
        return self._menu_item
    
    @property
    def quantity(self) -> int:
        return self._quantity
    
    @quantity.setter
    def quantity(self, value: int) -> None:
        if value < 1:
            raise ValueError("Quantity must be at least 1")
        self._quantity = value
    
    @property
    def special_instructions(self) -> str:
        return self._special_instructions
    
    def add_modification(self, mod: str) -> None:
        self._modifications.append(mod)
        self._menu_item.add_modification(mod)
    
    def get_subtotal(self) -> float:
        return self._menu_item.get_price() * self._quantity
    
    def get_prep_time(self) -> int:
        return self._menu_item.get_preparation_time()
    
    def __str__(self) -> str:
        mods = f" [{', '.join(self._modifications)}]" if self._modifications else ""
        return f"{self._quantity}x {self._menu_item.name}{mods} - ${self.get_subtotal():.2f}"


class Order(Observable):
    """Represents a customer order."""
    
    TAX_RATE = 0.10  # 10% tax
    
    def __init__(self, order_id: str, table: Table, waiter: Staff):
        self._order_id = order_id
        self._table = table
        self._waiter = waiter
        self._items: List[OrderItem] = []
        self._status = OrderStatus.PENDING
        self._created_at = datetime.now()
        self._completed_at: Optional[datetime] = None
        self._discount_percent: float = 0.0
        self._tip_amount: float = 0.0
        self._observers: List[Callable[[str], None]] = []
        
        # Link order to table
        table.current_order = self
    
    @property
    def order_id(self) -> str:
        return self._order_id
    
    @property
    def table(self) -> Table:
        return self._table
    
    @property
    def waiter(self) -> Staff:
        return self._waiter
    
    @property
    def items(self) -> List[OrderItem]:
        return self._items.copy()
    
    @property
    def status(self) -> OrderStatus:
        return self._status
    
    @status.setter
    def status(self, value: OrderStatus) -> None:
        old_status = self._status
        self._status = value
        if old_status != value:
            self.notify(f"Order {self._order_id} status: {old_status.value} → {value.value}")
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def discount_percent(self) -> float:
        return self._discount_percent
    
    @discount_percent.setter
    def discount_percent(self, value: float) -> None:
        if not 0 <= value <= 100:
            raise ValueError("Discount must be between 0 and 100")
        self._discount_percent = value
    
    @property
    def tip_amount(self) -> float:
        return self._tip_amount
    
    @tip_amount.setter
    def tip_amount(self, value: float) -> None:
        self._tip_amount = max(0, value)
    
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
    
    def add_item(self, order_item: OrderItem) -> None:
        """Add an item to the order."""
        if self._status != OrderStatus.PENDING:
            raise InvalidOrderError(self._order_id, "Cannot modify non-pending order")
        if not order_item.menu_item.is_available():
            raise ItemUnavailableError(order_item.menu_item.name)
        self._items.append(order_item)
    
    def remove_item(self, item_index: int) -> OrderItem:
        """Remove an item from the order by index."""
        if self._status != OrderStatus.PENDING:
            raise InvalidOrderError(self._order_id, "Cannot modify non-pending order")
        if 0 <= item_index < len(self._items):
            return self._items.pop(item_index)
        raise InvalidOrderError(self._order_id, f"Invalid item index: {item_index}")
    
    def get_subtotal(self) -> float:
        """Calculate subtotal before tax and discount."""
        return sum(item.get_subtotal() for item in self._items)
    
    def get_discount_amount(self) -> float:
        """Calculate discount amount."""
        return self.get_subtotal() * (self._discount_percent / 100)
    
    def get_tax_amount(self) -> float:
        """Calculate tax amount."""
        taxable = self.get_subtotal() - self.get_discount_amount()
        return taxable * self.TAX_RATE
    
    def get_total(self) -> float:
        """Calculate final total including tax."""
        subtotal = self.get_subtotal()
        discount = self.get_discount_amount()
        tax = self.get_tax_amount()
        return subtotal - discount + tax
    
    def get_grand_total(self) -> float:
        """Calculate grand total including tip."""
        return self.get_total() + self._tip_amount
    
    def get_estimated_prep_time(self) -> int:
        """Estimate total preparation time."""
        if not self._items:
            return 0
        # Parallel cooking - return max time, not sum
        return max(item.get_prep_time() for item in self._items)
    
    def submit(self) -> None:
        """Submit the order for preparation."""
        if not self._items:
            raise InvalidOrderError(self._order_id, "Cannot submit empty order")
        self.status = OrderStatus.PREPARING
    
    def mark_ready(self) -> None:
        """Mark order as ready to serve."""
        self.status = OrderStatus.READY
    
    def mark_served(self) -> None:
        """Mark order as served."""
        self.status = OrderStatus.SERVED
    
    def complete(self) -> None:
        """Complete the order."""
        self.status = OrderStatus.COMPLETED
        self._completed_at = datetime.now()
    
    def cancel(self, reason: str = "") -> None:
        """Cancel the order."""
        if self._status in (OrderStatus.SERVED, OrderStatus.COMPLETED):
            raise InvalidOrderError(self._order_id, "Cannot cancel served/completed order")
        self.status = OrderStatus.CANCELLED
        self.notify(f"Order {self._order_id} cancelled: {reason}")
    
    def __str__(self) -> str:
        return (f"Order {self._order_id} | Table {self._table.table_id} | "
                f"{len(self._items)} items | ${self.get_total():.2f} | {self._status.value}")


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


class RestaurantRegistry(metaclass=RegistryMeta):
    """
    Central registry for restaurant operations.
    Singleton ensures single source of truth.
    """
    
    def __init__(self):
        self._menu_items: Dict[str, MenuItem] = {}
        self._tables: Dict[str, Table] = {}
        self._staff: Dict[str, Staff] = {}
        self._orders: Dict[str, Order] = {}
        self._kitchen_observers: List[Callable[[str], None]] = []
        self._management_observers: List[Callable[[str], None]] = []
    
    # Menu management
    def add_menu_item(self, item: MenuItem) -> None:
        self._menu_items[item.item_id] = item
    
    def get_menu_item(self, item_id: str) -> MenuItem:
        if item_id not in self._menu_items:
            raise ItemNotFoundError(item_id)
        return self._menu_items[item_id]
    
    def get_menu_by_category(self, category: MenuCategory) -> List[MenuItem]:
        return [item for item in self._menu_items.values() 
                if item.category == category and item.is_available()]
    
    def get_items_by_dietary_tag(self, tag: DietaryTag) -> List[MenuItem]:
        return [item for item in self._menu_items.values() 
                if item.has_dietary_tag(tag) and item.is_available()]
    
    # Table management
    def add_table(self, table: Table) -> None:
        self._tables[table.table_id] = table
    
    def get_table(self, table_id: str) -> Table:
        if table_id not in self._tables:
            raise TableNotFoundError(table_id)
        return self._tables[table_id]
    
    def get_available_tables(self, min_capacity: int = 1) -> List[Table]:
        return [t for t in self._tables.values() 
                if t.is_available() and t.capacity >= min_capacity]
    
    # Staff management
    def add_staff(self, staff: Staff) -> None:
        self._staff[staff.staff_id] = staff
    
    def get_staff(self, staff_id: str) -> Staff:
        if staff_id not in self._staff:
            raise StaffNotFoundError(staff_id)
        return self._staff[staff_id]
    
    def get_available_waiters(self) -> List[Staff]:
        return [s for s in self._staff.values() 
                if isinstance(s, (Waiter, SeniorWaiter)) 
                and s.is_on_duty and s.can_take_table()]
    
    def get_on_duty_chefs(self) -> List[Chef]:
        return [s for s in self._staff.values() 
                if isinstance(s, Chef) and s.is_on_duty]
    
    # Order management
    def add_order(self, order: Order) -> None:
        self._orders[order.order_id] = order
        # Notify kitchen
        for observer in self._kitchen_observers:
            order.attach(observer)
    
    def get_order(self, order_id: str) -> Order:
        if order_id not in self._orders:
            raise OrderNotFoundError(order_id)
        return self._orders[order_id]
    
    def get_active_orders(self) -> List[Order]:
        active_statuses = (OrderStatus.PENDING, OrderStatus.PREPARING, OrderStatus.READY)
        return [o for o in self._orders.values() if o.status in active_statuses]
    
    def get_orders_for_table(self, table_id: str) -> List[Order]:
        return [o for o in self._orders.values() if o.table.table_id == table_id]
    
    # Observer management
    def attach_kitchen_observer(self, observer: Callable[[str], None]) -> None:
        if observer not in self._kitchen_observers:
            self._kitchen_observers.append(observer)
    
    def attach_management_observer(self, observer: Callable[[str], None]) -> None:
        if observer not in self._management_observers:
            self._management_observers.append(observer)
    
    def notify_management(self, message: str) -> None:
        for observer in self._management_observers:
            observer(message)
    
    def get_daily_revenue(self) -> float:
        """Calculate total revenue for completed orders today."""
        today = datetime.now().date()
        completed = [o for o in self._orders.values() 
                     if o.status == OrderStatus.COMPLETED 
                     and o.created_at.date() == today]
        return sum(o.get_grand_total() for o in completed)


# --- Factory Pattern ---
class MenuItemFactory:
    """Factory for creating menu items."""
    
    @staticmethod
    def create_item(category: str, item_id: str, name: str,
                    description: str, price: float, **kwargs) -> MenuItem:
        """
        Create a menu item based on category.
        
        Args:
            category: One of 'appetizer', 'main', 'dessert', 'beverage'
            item_id: Unique identifier
            name: Item name
            description: Item description
            price: Base price
            **kwargs: Category-specific parameters
            
        Returns:
            MenuItem: Created menu item
            
        Raises:
            MenuError: If category is invalid
        """
        dietary_tags = kwargs.get('dietary_tags', [])
        
        category_lower = category.lower()
        
        if category_lower == 'appetizer':
            return Appetizer(
                item_id, name, description, price,
                is_shareable=kwargs.get('is_shareable', False),
                dietary_tags=dietary_tags
            )
        
        elif category_lower in ('main', 'main_course'):
            return MainCourse(
                item_id, name, description, price,
                protein_type=kwargs.get('protein_type', 'chicken'),
                cooking_style=kwargs.get('cooking_style', 'grilled'),
                dietary_tags=dietary_tags
            )
        
        elif category_lower == 'dessert':
            return Dessert(
                item_id, name, description, price,
                is_cold=kwargs.get('is_cold', True),
                contains_alcohol=kwargs.get('contains_alcohol', False),
                dietary_tags=dietary_tags
            )
        
        elif category_lower == 'beverage':
            return Beverage(
                item_id, name, description, price,
                size_ml=kwargs.get('size_ml', 330),
                is_alcoholic=kwargs.get('is_alcoholic', False),
                is_hot=kwargs.get('is_hot', False),
                dietary_tags=dietary_tags
            )
        
        else:
            raise MenuError(f"Unknown menu category: {category}")


# --- Adapter Pattern ---
class LegacyMenuAdapter:
    """
    Adapter for legacy menu data format.
    
    Legacy format:
    {
        "code": "M001",
        "dish_name": "Spaghetti Bolognese",
        "desc": "Classic Italian pasta",
        "cost": 1850,  # Price in cents
        "cat": "MAIN",
        "veg": "N",
        "gf": "N",
        "prep_mins": 25
    }
    """
    
    CATEGORY_MAPPING = {
        "APP": "appetizer",
        "MAIN": "main",
        "DES": "dessert",
        "BEV": "beverage"
    }
    
    def __init__(self, factory: MenuItemFactory):
        self._factory = factory
    
    def adapt(self, legacy_data: Dict) -> MenuItem:
        """Convert legacy menu data to modern MenuItem."""
        # Validate required fields
        required = ['code', 'dish_name', 'cost', 'cat']
        for field in required:
            if field not in legacy_data:
                raise LegacyDataError(field, "required field", "missing")
        
        # Map category
        legacy_cat = legacy_data['cat'].upper()
        if legacy_cat not in self.CATEGORY_MAPPING:
            raise LegacyDataError('cat', f"one of {list(self.CATEGORY_MAPPING.keys())}", legacy_cat)
        category = self.CATEGORY_MAPPING[legacy_cat]
        
        # Convert price from cents to dollars
        price = legacy_data['cost'] / 100
        
        # Build dietary tags
        dietary_tags = []
        if legacy_data.get('veg', 'N').upper() == 'Y':
            dietary_tags.append(DietaryTag.VEGETARIAN)
        if legacy_data.get('gf', 'N').upper() == 'Y':
            dietary_tags.append(DietaryTag.GLUTEN_FREE)
        if legacy_data.get('vegan', 'N').upper() == 'Y':
            dietary_tags.append(DietaryTag.VEGAN)
        
        # Create item using factory
        return self._factory.create_item(
            category=category,
            item_id=legacy_data['code'],
            name=legacy_data['dish_name'],
            description=legacy_data.get('desc', ''),
            price=price,
            dietary_tags=dietary_tags
        )


# --- Observer Pattern: Kitchen Display System ---
class KitchenDisplay:
    """
    Kitchen display system that observes order status changes.
    Implements Observer pattern.
    """
    
    def __init__(self, name: str = "Kitchen"):
        self._name = name
        self._pending_orders: List[Order] = []
    
    def receive_notification(self, message: str) -> None:
        """Receive order notifications."""
        print(f"[{self._name} DISPLAY]: {message}")
    
    def add_order(self, order: Order) -> None:
        """Track a new order."""
        self._pending_orders.append(order)
        order.attach(self.receive_notification)
    
    def get_queue(self) -> List[Order]:
        """Get current order queue."""
        return [o for o in self._pending_orders 
                if o.status in (OrderStatus.PENDING, OrderStatus.PREPARING)]


# ============================================================================
# SECTION 8: ORDER SERVICE
# ============================================================================

class OrderService:
    """Service for managing orders."""
    
    def __init__(self, registry: RestaurantRegistry):
        self._registry = registry
        self._kitchen_display = KitchenDisplay()
        self._order_counter = 0
        
        # Register kitchen display as observer
        registry.attach_kitchen_observer(self._kitchen_display.receive_notification)
    
    def create_order(self, table: Table, waiter: Staff) -> Order:
        """Create a new order for a table."""
        if not table.status == TableStatus.OCCUPIED:
            raise TableError(f"Table {table.table_id} is not occupied")
        
        self._order_counter += 1
        order_id = f"ORD-{self._order_counter:04d}"
        
        order = Order(order_id, table, waiter)
        self._registry.add_order(order)
        self._kitchen_display.add_order(order)
        
        return order
    
    def add_item_to_order(self, order: Order, item_id: str,
                          quantity: int = 1, modifications: List[str] = None,
                          special_instructions: str = "") -> OrderItem:
        """Add an item to an existing order."""
        menu_item = self._registry.get_menu_item(item_id)
        
        order_item = OrderItem(menu_item, quantity, special_instructions)
        
        if modifications:
            for mod in modifications:
                order_item.add_modification(mod)
        
        order.add_item(order_item)
        return order_item
    
    def submit_order(self, order: Order) -> int:
        """Submit order to kitchen. Returns estimated prep time."""
        order.submit()
        
        # Assign to available chef
        chefs = self._registry.get_on_duty_chefs()
        if chefs:
            # Assign to chef with least orders
            chef = min(chefs, key=lambda c: len(c.current_orders))
            chef.accept_order(order)
            chef.receive_notification(f"New order: {order.order_id}")
        
        return order.get_estimated_prep_time()
    
    def complete_preparation(self, order: Order) -> None:
        """Mark order as ready for serving."""
        order.mark_ready()
        
        # Notify waiter
        order.waiter.receive_notification(
            f"Order {order.order_id} for Table {order.table.table_id} is READY!"
        )
    
    def serve_order(self, order: Order) -> None:
        """Mark order as served."""
        order.mark_served()
    
    def close_order(self, order: Order, tip_amount: float = 0) -> float:
        """Close out an order and return total."""
        order.tip_amount = tip_amount
        order.complete()
        
        # Award tip to waiter (just tracking here)
        total = order.get_grand_total()
        
        # Notify management of large orders
        if total > 200:
            self._registry.notify_management(
                f"Large order completed: {order.order_id} - ${total:.2f}"
            )
        
        return total
    
    def apply_discount(self, order: Order, discount_percent: float,
                       reason: str = "") -> None:
        """Apply a discount to an order."""
        order.discount_percent = discount_percent
        self._registry.notify_management(
            f"Discount applied to {order.order_id}: {discount_percent}% - {reason}"
        )
    
    def generate_receipt(self, order: Order) -> str:
        """Generate a receipt for an order."""
        lines = [
            "=" * 40,
            "       GOURMET BITE RESTAURANT",
            "=" * 40,
            f"Order: {order.order_id}",
            f"Table: {order.table.table_id}",
            f"Server: {order.waiter.name}",
            f"Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}",
            "-" * 40,
        ]
        
        for item in order.items:
            lines.append(str(item))
        
        lines.extend([
            "-" * 40,
            f"Subtotal:     ${order.get_subtotal():>10.2f}",
        ])
        
        if order.discount_percent > 0:
            lines.append(f"Discount ({order.discount_percent}%): -${order.get_discount_amount():>9.2f}")
        
        lines.extend([
            f"Tax (10%):    ${order.get_tax_amount():>10.2f}",
            "-" * 40,
            f"Total:        ${order.get_total():>10.2f}",
        ])
        
        if order.tip_amount > 0:
            lines.extend([
                f"Tip:          ${order.tip_amount:>10.2f}",
                f"Grand Total:  ${order.get_grand_total():>10.2f}",
            ])
        
        lines.extend([
            "=" * 40,
            "     Thank you for dining with us!",
            "=" * 40,
        ])
        
        return "\n".join(lines)


# ============================================================================
# SECTION 9: MAIN DEMONSTRATION
# ============================================================================

def main():
    """Demonstrate the restaurant management system."""
    print("=" * 60)
    print("GourmetBite Restaurant Management System")
    print("=" * 60)
    
    # 1. Singleton Pattern Verification
    print("\n1. SINGLETON PATTERN VERIFICATION")
    print("-" * 40)
    reg1 = RestaurantRegistry()
    reg2 = RestaurantRegistry()
    print(f"   Same instance: {reg1 is reg2}")  # True
    
    registry = reg1
    
    # 2. Create Menu Items using Factory Pattern
    print("\n2. FACTORY PATTERN - CREATING MENU")
    print("-" * 40)
    factory = MenuItemFactory()
    
    # Appetizers
    bruschetta = factory.create_item(
        'appetizer', 'APP-001', 'Bruschetta',
        'Toasted bread with tomatoes and basil',
        12.50, is_shareable=True,
        dietary_tags=[DietaryTag.VEGETARIAN, DietaryTag.VEGAN]
    )
    
    calamari = factory.create_item(
        'appetizer', 'APP-002', 'Crispy Calamari',
        'Lightly fried squid with aioli',
        15.00, is_shareable=True
    )
    
    # Main Courses
    salmon = factory.create_item(
        'main', 'MAIN-001', 'Grilled Salmon',
        'Atlantic salmon with lemon butter sauce',
        28.00, protein_type='fish', cooking_style='grilled',
        dietary_tags=[DietaryTag.GLUTEN_FREE]
    )
    
    steak = factory.create_item(
        'main', 'MAIN-002', 'Ribeye Steak',
        '300g ribeye with herb butter',
        42.00, protein_type='beef', cooking_style='grilled'
    )
    
    pasta = factory.create_item(
        'main', 'MAIN-003', 'Mushroom Risotto',
        'Creamy arborio rice with wild mushrooms',
        24.00, protein_type='vegetable', cooking_style='steamed',
        dietary_tags=[DietaryTag.VEGETARIAN, DietaryTag.GLUTEN_FREE]
    )
    
    # Desserts
    tiramisu = factory.create_item(
        'dessert', 'DES-001', 'Tiramisu',
        'Classic Italian coffee dessert',
        12.00, is_cold=True, contains_alcohol=True
    )
    
    sorbet = factory.create_item(
        'dessert', 'DES-002', 'Mango Sorbet',
        'Refreshing tropical sorbet',
        8.00, is_cold=True,
        dietary_tags=[DietaryTag.VEGAN, DietaryTag.GLUTEN_FREE]
    )
    
    # Beverages
    wine = factory.create_item(
        'beverage', 'BEV-001', 'House Red Wine',
        'Shiraz from Barossa Valley',
        12.00, size_ml=150, is_alcoholic=True
    )
    
    coffee = factory.create_item(
        'beverage', 'BEV-002', 'Espresso',
        'Double shot espresso',
        4.50, size_ml=60, is_hot=True,
        dietary_tags=[DietaryTag.VEGAN]
    )
    
    # Add to registry
    for item in [bruschetta, calamari, salmon, steak, pasta, tiramisu, sorbet, wine, coffee]:
        registry.add_menu_item(item)
    
    print(f"   Menu items created: {len(registry.get_menu_by_category(MenuCategory.APPETIZER))} appetizers")
    print(f"   Menu items created: {len(registry.get_menu_by_category(MenuCategory.MAIN_COURSE))} mains")
    print(f"   Menu items created: {len(registry.get_menu_by_category(MenuCategory.DESSERT))} desserts")
    print(f"   Menu items created: {len(registry.get_menu_by_category(MenuCategory.BEVERAGE))} beverages")
    
    # 3. Create Tables
    print("\n3. CREATING TABLES")
    print("-" * 40)
    tables = [
        Table("T1", 2, "main"),
        Table("T2", 4, "main"),
        Table("T3", 4, "main"),
        Table("T4", 6, "main"),
        Table("T5", 8, "private"),
        Table("T6", 2, "patio"),
    ]
    for table in tables:
        registry.add_table(table)
        print(f"   {table}")
    
    # 4. Create Staff
    print("\n4. CREATING STAFF (Inheritance & Polymorphism)")
    print("-" * 40)
    
    waiter1 = Waiter("W001", "Alice")
    waiter1.is_on_duty = True
    
    waiter2 = Waiter("W002", "Bob")
    waiter2.is_on_duty = True
    
    senior = SeniorWaiter("W003", "Carol")
    senior.is_on_duty = True
    
    chef1 = Chef("C001", "David", "Italian")
    chef1.is_on_duty = True
    
    head_chef = HeadChef("C002", "Elena")
    head_chef.is_on_duty = True
    
    for staff in [waiter1, waiter2, senior, chef1, head_chef]:
        registry.add_staff(staff)
        print(f"   {staff}")
    
    # 5. Management Observer
    print("\n5. OBSERVER PATTERN - MANAGEMENT ALERTS")
    print("-" * 40)
    
    def management_alert(message: str):
        print(f"   [MANAGEMENT ALERT]: {message}")
    
    registry.attach_management_observer(management_alert)
    print("   Management observer attached")
    
    # 6. Create and Process Order
    print("\n6. ORDER WORKFLOW DEMONSTRATION")
    print("-" * 40)
    
    # Initialize order service
    order_service = OrderService(registry)
    
    # Seat guests at table
    table2 = registry.get_table("T2")
    table2.seat_guests(3)
    waiter1.assign_table(table2)
    table2.assigned_waiter = waiter1
    print(f"   Guests seated at {table2}")
    
    # Create order
    order = order_service.create_order(table2, waiter1)
    print(f"   Order created: {order.order_id}")
    
    # Add items
    order_service.add_item_to_order(order, 'APP-001', quantity=1)
    order_service.add_item_to_order(order, 'MAIN-002', quantity=2, 
                                     modifications=['medium-rare', 'extra mushrooms'])
    order_service.add_item_to_order(order, 'MAIN-001', quantity=1)
    order_service.add_item_to_order(order, 'BEV-001', quantity=3)
    
    print(f"   Items added: {len(order.items)}")
    for item in order.items:
        print(f"      - {item}")
    
    # 7. Submit to Kitchen
    print("\n7. KITCHEN PROCESSING")
    print("-" * 40)
    
    prep_time = order_service.submit_order(order)
    print(f"   Order submitted. Estimated prep time: {prep_time} minutes")
    print(f"   Order status: {order.status.value}")
    
    # Simulate preparation complete
    order_service.complete_preparation(order)
    print(f"   Order status: {order.status.value}")
    
    # Serve order
    order_service.serve_order(order)
    print(f"   Order status: {order.status.value}")
    
    # 8. Cost Calculations
    print("\n8. COST CALCULATIONS")
    print("-" * 40)
    print(f"   Subtotal: ${order.get_subtotal():.2f}")
    print(f"   Tax (10%): ${order.get_tax_amount():.2f}")
    print(f"   Total: ${order.get_total():.2f}")
    
    # Apply discount (loyalty customer)
    order_service.apply_discount(order, 10, "Loyalty member")
    print(f"   After 10% discount: ${order.get_total():.2f}")
    
    # 9. Close Order and Generate Receipt
    print("\n9. CLOSING ORDER & RECEIPT")
    print("-" * 40)
    
    grand_total = order_service.close_order(order, tip_amount=25.00)
    print(f"   Grand total (with $25 tip): ${grand_total:.2f}")
    
    print("\n" + order_service.generate_receipt(order))
    
    # 10. Legacy Data Adapter
    print("\n10. ADAPTER PATTERN - LEGACY DATA")
    print("-" * 40)
    
    legacy_data = {
        "code": "LEGACY-001",
        "dish_name": "Classic Margherita Pizza",
        "desc": "Traditional pizza with tomato and mozzarella",
        "cost": 1800,  # $18.00 in cents
        "cat": "MAIN",
        "veg": "Y",
        "gf": "N"
    }
    
    adapter = LegacyMenuAdapter(factory)
    legacy_item = adapter.adapt(legacy_data)
    registry.add_menu_item(legacy_item)
    
    print(f"   Converted legacy item: {legacy_item}")
    print(f"   Price: ${legacy_item.get_price():.2f}")
    print(f"   Dietary tags: {[t.value for t in legacy_item.dietary_tags]}")
    
    # 11. Exception Handling
    print("\n11. EXCEPTION HANDLING")
    print("-" * 40)
    
    # Try to find non-existent item
    try:
        registry.get_menu_item("FAKE-999")
    except ItemNotFoundError as e:
        print(f"   Caught ItemNotFoundError: {e}")
    
    # Try to modify completed order
    try:
        order_service.add_item_to_order(order, 'APP-001')
    except InvalidOrderError as e:
        print(f"   Caught InvalidOrderError: {e}")
    
    # Try to seat at occupied table
    try:
        table2.seat_guests(2)
    except TableUnavailableError as e:
        print(f"   Caught TableUnavailableError: {e}")
    
    # 12. Dietary Filtering (Polymorphism)
    print("\n12. DIETARY TAG FILTERING")
    print("-" * 40)
    
    vegetarian_items = registry.get_items_by_dietary_tag(DietaryTag.VEGETARIAN)
    print(f"   Vegetarian options ({len(vegetarian_items)}):")
    for item in vegetarian_items:
        print(f"      - {item.name}: ${item.base_price:.2f}")
    
    gf_items = registry.get_items_by_dietary_tag(DietaryTag.GLUTEN_FREE)
    print(f"   Gluten-free options ({len(gf_items)}):")
    for item in gf_items:
        print(f"      - {item.name}: ${item.base_price:.2f}")
    
    # 13. Daily Revenue
    print("\n13. DAILY STATISTICS")
    print("-" * 40)
    print(f"   Daily revenue: ${registry.get_daily_revenue():.2f}")
    print(f"   Active orders: {len(registry.get_active_orders())}")
    print(f"   Available tables: {len(registry.get_available_tables())}")
    
    # 14. Head Chef Special (Polymorphism)
    print("\n14. HEAD CHEF DAILY SPECIAL")
    print("-" * 40)
    special = head_chef.create_daily_special("Pan-Seared Duck Breast", 38.00)
    registry.add_menu_item(special)
    print(f"   Created: {special}")
    print(f"   Prep time: {special.get_preparation_time()} minutes")
    
    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
