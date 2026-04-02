"""
Food Delivery Platform - Complete OOP Reference Implementation
==============================================================

This module demonstrates all major Object-Oriented Programming concepts
through a food delivery platform simulation.

OOP Concepts Demonstrated:
- Class hierarchies with Abstract Base Classes (ABC)
- Interfaces using ABC
- Encapsulation with properties and validation
- Custom exception hierarchy
- Design Patterns: Factory, Adapter, Observer, Singleton
- Enums for type safety
- Composition and aggregation

Author: OOP Teaching Reference
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Callable, Any, Tuple
import random
import uuid


# =============================================================================
# SECTION 1: ENUMERATIONS
# =============================================================================

class RestaurantType(Enum):
    """Types of restaurants on the platform."""
    FAST_FOOD = auto()
    CASUAL_DINING = auto()
    FINE_DINING = auto()
    CLOUD_KITCHEN = auto()


class OrderStatus(Enum):
    """Possible states of an order throughout its lifecycle."""
    PLACED = "placed"
    ACCEPTED = "accepted"
    PREPARING = "preparing"
    READY = "ready"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PaymentMethod(Enum):
    """Supported payment methods."""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    DIGITAL_WALLET = "digital_wallet"
    CASH_ON_DELIVERY = "cash_on_delivery"


class VehicleType(Enum):
    """Types of delivery vehicles."""
    BIKE = auto()
    CAR = auto()
    WALKING = auto()


class DietaryTag(Enum):
    """Dietary restriction and preference tags."""
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    GLUTEN_FREE = "gluten_free"
    HALAL = "halal"
    KOSHER = "kosher"
    NUT_FREE = "nut_free"


class MealPeriod(Enum):
    """Meal periods for time-based pricing and availability."""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    LATE_NIGHT = "late_night"


# =============================================================================
# SECTION 2: CUSTOM EXCEPTIONS HIERARCHY
# =============================================================================

class DeliveryException(Exception):
    """Base exception for all delivery platform errors."""
    pass


class RestaurantException(DeliveryException):
    """Base exception for restaurant-related errors."""
    pass


class RestaurantClosedError(RestaurantException):
    """Raised when attempting to order from a closed restaurant."""
    def __init__(self, restaurant_name: str, opening_hours: str = ""):
        self.restaurant_name = restaurant_name
        self.opening_hours = opening_hours
        message = f"Restaurant '{restaurant_name}' is currently closed."
        if opening_hours:
            message += f" Opening hours: {opening_hours}"
        super().__init__(message)


class RestaurantNotFoundError(RestaurantException):
    """Raised when a restaurant cannot be found."""
    def __init__(self, restaurant_id: str):
        self.restaurant_id = restaurant_id
        super().__init__(f"Restaurant with ID '{restaurant_id}' not found.")


class OutOfDeliveryRangeError(RestaurantException):
    """Raised when delivery address is outside restaurant's delivery range."""
    def __init__(self, distance: float, max_range: float):
        self.distance = distance
        self.max_range = max_range
        super().__init__(
            f"Delivery address is {distance:.1f}km away, "
            f"but maximum delivery range is {max_range:.1f}km."
        )


class OrderException(DeliveryException):
    """Base exception for order-related errors."""
    pass


class MinimumOrderNotMetError(OrderException):
    """Raised when order total is below minimum requirement."""
    def __init__(self, current_total: float, minimum_required: float):
        self.current_total = current_total
        self.minimum_required = minimum_required
        super().__init__(
            f"Order total ${current_total:.2f} is below minimum "
            f"${minimum_required:.2f}."
        )


class ItemNotAvailableError(OrderException):
    """Raised when a menu item is not available."""
    def __init__(self, item_name: str, reason: str = ""):
        self.item_name = item_name
        self.reason = reason
        message = f"Item '{item_name}' is not available."
        if reason:
            message += f" Reason: {reason}"
        super().__init__(message)


class OrderCancellationError(OrderException):
    """Raised when an order cannot be cancelled."""
    def __init__(self, order_id: str, current_status: OrderStatus):
        self.order_id = order_id
        self.current_status = current_status
        super().__init__(
            f"Order '{order_id}' cannot be cancelled. "
            f"Current status: {current_status.value}"
        )


class InvalidOrderStatusError(OrderException):
    """Raised when attempting an invalid status transition."""
    def __init__(self, current: OrderStatus, attempted: OrderStatus):
        self.current = current
        self.attempted = attempted
        super().__init__(
            f"Cannot transition from {current.value} to {attempted.value}."
        )


class DeliveryPersonException(DeliveryException):
    """Base exception for delivery person related errors."""
    pass


class NoDriverAvailableError(DeliveryPersonException):
    """Raised when no drivers are available for delivery."""
    def __init__(self, location: str = ""):
        self.location = location
        message = "No delivery drivers available"
        if location:
            message += f" near {location}"
        super().__init__(message)


class DeliveryFailedError(DeliveryPersonException):
    """Raised when a delivery fails."""
    def __init__(self, order_id: str, reason: str):
        self.order_id = order_id
        self.reason = reason
        super().__init__(f"Delivery for order '{order_id}' failed: {reason}")


class PaymentException(DeliveryException):
    """Base exception for payment-related errors."""
    pass


class PaymentDeclinedError(PaymentException):
    """Raised when a payment is declined."""
    def __init__(self, reason: str = "Card declined"):
        self.reason = reason
        super().__init__(f"Payment declined: {reason}")


class RefundFailedError(PaymentException):
    """Raised when a refund cannot be processed."""
    def __init__(self, order_id: str, amount: float, reason: str):
        self.order_id = order_id
        self.amount = amount
        self.reason = reason
        super().__init__(
            f"Refund of ${amount:.2f} for order '{order_id}' failed: {reason}"
        )


# =============================================================================
# SECTION 3: INTERFACES (Abstract Base Classes)
# =============================================================================

class Orderable(ABC):
    """Interface for items that can be ordered."""
    
    @abstractmethod
    def add_to_cart(self, item: 'MenuItem', quantity: int = 1) -> None:
        """Add an item to the cart."""
        pass
    
    @abstractmethod
    def remove_from_cart(self, item: 'MenuItem', quantity: int = 1) -> None:
        """Remove an item from the cart."""
        pass
    
    @abstractmethod
    def calculate_subtotal(self) -> float:
        """Calculate the subtotal of all items."""
        pass


class Deliverable(ABC):
    """Interface for deliverable orders."""
    
    @abstractmethod
    def assign_driver(self, driver: 'DeliveryPerson') -> None:
        """Assign a delivery driver to the order."""
        pass
    
    @abstractmethod
    def track_delivery(self) -> Dict[str, Any]:
        """Get current delivery tracking information."""
        pass
    
    @abstractmethod
    def confirm_delivery(self) -> None:
        """Confirm that delivery has been completed."""
        pass


class Observable(ABC):
    """Interface for observable subjects (Observer pattern)."""
    
    @abstractmethod
    def add_observer(self, observer: 'Observer') -> None:
        """Register an observer."""
        pass
    
    @abstractmethod
    def remove_observer(self, observer: 'Observer') -> None:
        """Unregister an observer."""
        pass
    
    @abstractmethod
    def notify_observers(self, event: str, data: Dict[str, Any]) -> None:
        """Notify all observers of an event."""
        pass


class Observer(ABC):
    """Interface for observers."""
    
    @abstractmethod
    def update(self, event: str, data: Dict[str, Any]) -> None:
        """Receive update notification."""
        pass


class Rateable(ABC):
    """Interface for entities that can be rated."""
    
    @abstractmethod
    def add_rating(self, rating: int, review: str = "") -> None:
        """Add a rating (1-5) with optional review."""
        pass
    
    @abstractmethod
    def get_average_rating(self) -> float:
        """Get the average rating."""
        pass
    
    @abstractmethod
    def get_reviews(self) -> List[Dict[str, Any]]:
        """Get all reviews."""
        pass


# =============================================================================
# SECTION 4: SINGLETON PATTERN - Platform Registry
# =============================================================================

class SingletonMeta(type):
    """
    Metaclass implementing the Singleton pattern.
    
    This ensures only one instance of a class exists throughout
    the application lifecycle.
    """
    _instances: Dict[type, Any] = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class DeliveryPlatformRegistry(metaclass=SingletonMeta):
    """
    Central registry for the delivery platform (Singleton).
    
    Stores and manages all restaurants, drivers, customers, and orders.
    Uses Singleton pattern to ensure consistent state across the application.
    """
    
    def __init__(self):
        self._restaurants: Dict[str, 'Restaurant'] = {}
        self._drivers: Dict[str, 'DeliveryPerson'] = {}
        self._customers: Dict[str, 'Customer'] = {}
        self._orders: Dict[str, 'Order'] = {}
        self._promo_codes: Dict[str, 'PromoCode'] = {}
        print("[Registry] DeliveryPlatformRegistry initialized (Singleton)")
    
    def register_restaurant(self, restaurant: 'Restaurant') -> None:
        """Register a restaurant on the platform."""
        self._restaurants[restaurant.restaurant_id] = restaurant
        print(f"[Registry] Restaurant registered: {restaurant.name}")
    
    def register_driver(self, driver: 'DeliveryPerson') -> None:
        """Register a delivery driver."""
        self._drivers[driver.driver_id] = driver
        print(f"[Registry] Driver registered: {driver.name}")
    
    def register_customer(self, customer: 'Customer') -> None:
        """Register a customer."""
        self._customers[customer.customer_id] = customer
        print(f"[Registry] Customer registered: {customer.name}")
    
    def register_order(self, order: 'Order') -> None:
        """Register a new order."""
        self._orders[order.order_id] = order
        print(f"[Registry] Order registered: {order.order_id}")
    
    def add_promo_code(self, promo: 'PromoCode') -> None:
        """Add a promo code to the platform."""
        self._promo_codes[promo.code] = promo
        print(f"[Registry] Promo code added: {promo.code}")
    
    def get_restaurant(self, restaurant_id: str) -> 'Restaurant':
        """Get a restaurant by ID."""
        if restaurant_id not in self._restaurants:
            raise RestaurantNotFoundError(restaurant_id)
        return self._restaurants[restaurant_id]
    
    def get_available_drivers(self, location: Tuple[float, float], 
                               vehicle_type: Optional[VehicleType] = None) -> List['DeliveryPerson']:
        """Get available drivers near a location."""
        available = [
            driver for driver in self._drivers.values()
            if driver.is_available and driver.calculate_distance(location) <= driver.max_range
        ]
        if vehicle_type:
            available = [d for d in available if d.vehicle_type == vehicle_type]
        return sorted(available, key=lambda d: d.get_average_rating(), reverse=True)
    
    def get_promo_code(self, code: str) -> Optional['PromoCode']:
        """Get a promo code if valid."""
        return self._promo_codes.get(code.upper())
    
    def get_all_restaurants(self) -> List['Restaurant']:
        """Get all registered restaurants."""
        return list(self._restaurants.values())
    
    def get_order(self, order_id: str) -> 'Order':
        """Get an order by ID."""
        if order_id not in self._orders:
            raise OrderException(f"Order '{order_id}' not found")
        return self._orders[order_id]
    
    @property
    def stats(self) -> Dict[str, int]:
        """Get platform statistics."""
        return {
            "restaurants": len(self._restaurants),
            "drivers": len(self._drivers),
            "customers": len(self._customers),
            "orders": len(self._orders),
            "promo_codes": len(self._promo_codes)
        }


# =============================================================================
# SECTION 5: MENU ITEM HIERARCHY
# =============================================================================

@dataclass
class Customization:
    """Represents a customization option for menu items."""
    name: str
    options: List[str]
    price_modifier: float = 0.0
    selected: Optional[str] = None


class MenuItem(ABC):
    """
    Abstract base class for menu items.
    
    Demonstrates encapsulation with private attributes and properties.
    """
    
    def __init__(self, item_id: str, name: str, description: str,
                 base_price: float, dietary_tags: Optional[Set[DietaryTag]] = None):
        self._item_id = item_id
        self._name = name
        self._description = description
        self._base_price = base_price
        self._dietary_tags = dietary_tags or set()
        self._customizations: List[Customization] = []
        self._is_available = True
        self._prep_time_minutes = 10
    
    @property
    def item_id(self) -> str:
        """Get item ID (read-only)."""
        return self._item_id
    
    @property
    def name(self) -> str:
        """Get item name."""
        return self._name
    
    @property
    def description(self) -> str:
        """Get item description."""
        return self._description
    
    @property
    def base_price(self) -> float:
        """Get base price before customizations."""
        return self._base_price
    
    @base_price.setter
    def base_price(self, value: float) -> None:
        """Set base price with validation."""
        if value < 0:
            raise ValueError("Price cannot be negative")
        self._base_price = value
    
    @property
    def dietary_tags(self) -> Set[DietaryTag]:
        """Get dietary tags."""
        return self._dietary_tags.copy()
    
    @property
    def is_available(self) -> bool:
        """Check if item is available."""
        return self._is_available
    
    @is_available.setter
    def is_available(self, value: bool) -> None:
        """Set availability status."""
        self._is_available = value
    
    @property
    def prep_time(self) -> int:
        """Get preparation time in minutes."""
        return self._prep_time_minutes
    
    def add_customization(self, customization: Customization) -> None:
        """Add a customization option."""
        self._customizations.append(customization)
    
    @abstractmethod
    def calculate_price(self) -> float:
        """Calculate total price including customizations."""
        pass
    
    @abstractmethod
    def get_category(self) -> str:
        """Get the item category."""
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name}, ${self.base_price:.2f})"


class MainDish(MenuItem):
    """Main dish menu item (entrees, main courses)."""
    
    def __init__(self, item_id: str, name: str, description: str,
                 base_price: float, portion_size: str = "Regular",
                 dietary_tags: Optional[Set[DietaryTag]] = None):
        super().__init__(item_id, name, description, base_price, dietary_tags)
        self._portion_size = portion_size
        self._prep_time_minutes = 15
    
    @property
    def portion_size(self) -> str:
        return self._portion_size
    
    def calculate_price(self) -> float:
        """Calculate price with customization modifiers."""
        total = self._base_price
        for custom in self._customizations:
            if custom.selected:
                total += custom.price_modifier
        return total
    
    def get_category(self) -> str:
        return "Main Dish"


class SideDish(MenuItem):
    """Side dish menu item."""
    
    def __init__(self, item_id: str, name: str, description: str,
                 base_price: float, dietary_tags: Optional[Set[DietaryTag]] = None):
        super().__init__(item_id, name, description, base_price, dietary_tags)
        self._prep_time_minutes = 8
    
    def calculate_price(self) -> float:
        return self._base_price
    
    def get_category(self) -> str:
        return "Side Dish"


class Beverage(MenuItem):
    """Beverage menu item."""
    
    def __init__(self, item_id: str, name: str, description: str,
                 base_price: float, size: str = "Medium", is_alcoholic: bool = False,
                 dietary_tags: Optional[Set[DietaryTag]] = None):
        super().__init__(item_id, name, description, base_price, dietary_tags)
        self._size = size
        self._is_alcoholic = is_alcoholic
        self._prep_time_minutes = 2
    
    @property
    def size(self) -> str:
        return self._size
    
    @property
    def is_alcoholic(self) -> bool:
        return self._is_alcoholic
    
    def calculate_price(self) -> float:
        size_multiplier = {"Small": 0.8, "Medium": 1.0, "Large": 1.3}
        return self._base_price * size_multiplier.get(self._size, 1.0)
    
    def get_category(self) -> str:
        return "Beverage"


class Dessert(MenuItem):
    """Dessert menu item."""
    
    def __init__(self, item_id: str, name: str, description: str,
                 base_price: float, dietary_tags: Optional[Set[DietaryTag]] = None):
        super().__init__(item_id, name, description, base_price, dietary_tags)
        self._prep_time_minutes = 5
    
    def calculate_price(self) -> float:
        return self._base_price
    
    def get_category(self) -> str:
        return "Dessert"


class Combo(MenuItem):
    """Combo meal containing multiple items."""
    
    def __init__(self, item_id: str, name: str, description: str,
                 items: List[MenuItem], discount_percentage: float = 15.0,
                 dietary_tags: Optional[Set[DietaryTag]] = None):
        # Calculate base price from items
        base_price = sum(item.base_price for item in items)
        super().__init__(item_id, name, description, base_price, dietary_tags)
        self._items = items
        self._discount_percentage = discount_percentage
        # Prep time is the max of all items
        self._prep_time_minutes = max(item.prep_time for item in items)
    
    @property
    def items(self) -> List[MenuItem]:
        """Get items in the combo."""
        return self._items.copy()
    
    @property
    def discount_percentage(self) -> float:
        return self._discount_percentage
    
    def calculate_price(self) -> float:
        """Calculate discounted combo price."""
        total = sum(item.calculate_price() for item in self._items)
        return total * (1 - self._discount_percentage / 100)
    
    def get_category(self) -> str:
        return "Combo"


# =============================================================================
# SECTION 6: RESTAURANT HIERARCHY
# =============================================================================

class Restaurant(Rateable):
    """
    Abstract base class for restaurants.
    
    Inherits from Rateable (which inherits from ABC) for customer reviews.
    Demonstrates encapsulation and polymorphism.
    """
    
    def __init__(self, restaurant_id: str, name: str, address: str,
                 location: Tuple[float, float], cuisine_type: str):
        self._restaurant_id = restaurant_id
        self._name = name
        self._address = address
        self._location = location  # (latitude, longitude)
        self._cuisine_type = cuisine_type
        self._menu: Dict[str, MenuItem] = {}
        self._ratings: List[Dict[str, Any]] = []
        self._is_open = True
        self._opening_time = time(9, 0)
        self._closing_time = time(22, 0)
    
    @property
    def restaurant_id(self) -> str:
        return self._restaurant_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def address(self) -> str:
        return self._address
    
    @property
    def location(self) -> Tuple[float, float]:
        return self._location
    
    @property
    def cuisine_type(self) -> str:
        return self._cuisine_type
    
    @property
    def is_open(self) -> bool:
        """Check if restaurant is currently open."""
        now = datetime.now().time()
        return self._is_open and self._opening_time <= now <= self._closing_time
    
    @is_open.setter
    def is_open(self, value: bool) -> None:
        self._is_open = value
    
    @property
    @abstractmethod
    def restaurant_type(self) -> RestaurantType:
        """Get the restaurant type."""
        pass
    
    @property
    @abstractmethod
    def minimum_order(self) -> float:
        """Get minimum order amount."""
        pass
    
    @property
    @abstractmethod
    def delivery_radius(self) -> float:
        """Get delivery radius in kilometers."""
        pass
    
    @property
    @abstractmethod
    def commission_rate(self) -> float:
        """Get platform commission rate (0.0 to 1.0)."""
        pass
    
    @abstractmethod
    def get_prep_time(self) -> int:
        """Get average prep time in minutes."""
        pass
    
    def add_menu_item(self, item: MenuItem) -> None:
        """Add an item to the menu."""
        self._menu[item.item_id] = item
    
    def get_menu_item(self, item_id: str) -> MenuItem:
        """Get a menu item by ID."""
        if item_id not in self._menu:
            raise ItemNotAvailableError(item_id, "Item not on menu")
        item = self._menu[item_id]
        if not item.is_available:
            raise ItemNotAvailableError(item.name, "Currently unavailable")
        return item
    
    def get_menu(self) -> List[MenuItem]:
        """Get all available menu items."""
        return [item for item in self._menu.values() if item.is_available]
    
    def calculate_distance(self, customer_location: Tuple[float, float]) -> float:
        """Calculate distance to customer (simplified)."""
        lat1, lon1 = self._location
        lat2, lon2 = customer_location
        # Simplified distance calculation
        return ((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2) ** 0.5 * 111
    
    def can_deliver_to(self, customer_location: Tuple[float, float]) -> bool:
        """Check if restaurant can deliver to location."""
        return self.calculate_distance(customer_location) <= self.delivery_radius
    
    # Rateable interface implementation
    def add_rating(self, rating: int, review: str = "") -> None:
        """Add a rating (1-5) with optional review."""
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        self._ratings.append({
            "rating": rating,
            "review": review,
            "timestamp": datetime.now()
        })
    
    def get_average_rating(self) -> float:
        """Get average rating."""
        if not self._ratings:
            return 0.0
        return sum(r["rating"] for r in self._ratings) / len(self._ratings)
    
    def get_reviews(self) -> List[Dict[str, Any]]:
        """Get all reviews."""
        return self._ratings.copy()
    
    def get_opening_hours(self) -> str:
        """Get formatted opening hours."""
        return f"{self._opening_time.strftime('%H:%M')} - {self._closing_time.strftime('%H:%M')}"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name}, {self.cuisine_type})"


class FastFood(Restaurant):
    """Fast food restaurant with quick prep times and wide delivery."""
    
    @property
    def restaurant_type(self) -> RestaurantType:
        return RestaurantType.FAST_FOOD
    
    @property
    def minimum_order(self) -> float:
        return 10.0
    
    @property
    def delivery_radius(self) -> float:
        return 8.0  # km
    
    @property
    def commission_rate(self) -> float:
        return 0.15  # 15%
    
    def get_prep_time(self) -> int:
        return 10  # minutes


class CasualDining(Restaurant):
    """Casual dining restaurant with moderate prep times."""
    
    @property
    def restaurant_type(self) -> RestaurantType:
        return RestaurantType.CASUAL_DINING
    
    @property
    def minimum_order(self) -> float:
        return 20.0
    
    @property
    def delivery_radius(self) -> float:
        return 6.0
    
    @property
    def commission_rate(self) -> float:
        return 0.20  # 20%
    
    def get_prep_time(self) -> int:
        return 20


class FineDining(Restaurant):
    """Fine dining restaurant with longer prep times and smaller radius."""
    
    @property
    def restaurant_type(self) -> RestaurantType:
        return RestaurantType.FINE_DINING
    
    @property
    def minimum_order(self) -> float:
        return 50.0
    
    @property
    def delivery_radius(self) -> float:
        return 5.0
    
    @property
    def commission_rate(self) -> float:
        return 0.25  # 25%
    
    def get_prep_time(self) -> int:
        return 35


class CloudKitchen(Restaurant):
    """
    Delivery-only kitchen (ghost kitchen).
    No physical dining space, optimized for delivery.
    """
    
    @property
    def restaurant_type(self) -> RestaurantType:
        return RestaurantType.CLOUD_KITCHEN
    
    @property
    def minimum_order(self) -> float:
        return 15.0
    
    @property
    def delivery_radius(self) -> float:
        return 10.0  # Widest range
    
    @property
    def commission_rate(self) -> float:
        return 0.30  # 30% (highest)
    
    def get_prep_time(self) -> int:
        return 15


# =============================================================================
# SECTION 7: DELIVERY PERSON HIERARCHY
# =============================================================================

class DeliveryPerson(Rateable):
    """
    Abstract base class for delivery personnel.
    
    Inherits from Rateable (which inherits from ABC).
    Different delivery methods have different ranges and capacities.
    """
    
    def __init__(self, driver_id: str, name: str, phone: str,
                 current_location: Tuple[float, float]):
        self._driver_id = driver_id
        self._name = name
        self._phone = phone
        self._current_location = current_location
        self._is_available = True
        self._current_order: Optional['Order'] = None
        self._ratings: List[Dict[str, Any]] = []
        self._completed_deliveries = 0
    
    @property
    def driver_id(self) -> str:
        return self._driver_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def phone(self) -> str:
        return self._phone
    
    @property
    def current_location(self) -> Tuple[float, float]:
        return self._current_location
    
    @current_location.setter
    def current_location(self, value: Tuple[float, float]) -> None:
        self._current_location = value
    
    @property
    def is_available(self) -> bool:
        return self._is_available and self._current_order is None
    
    @is_available.setter
    def is_available(self, value: bool) -> None:
        self._is_available = value
    
    @property
    @abstractmethod
    def vehicle_type(self) -> VehicleType:
        """Get the vehicle type."""
        pass
    
    @property
    @abstractmethod
    def max_range(self) -> float:
        """Get maximum delivery range in km."""
        pass
    
    @property
    @abstractmethod
    def max_capacity(self) -> int:
        """Get maximum number of items/orders."""
        pass
    
    @abstractmethod
    def get_speed_rating(self) -> float:
        """Get speed rating (km per minute)."""
        pass
    
    def calculate_distance(self, location: Tuple[float, float]) -> float:
        """Calculate distance to a location."""
        lat1, lon1 = self._current_location
        lat2, lon2 = location
        return ((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2) ** 0.5 * 111
    
    def estimate_delivery_time(self, restaurant_location: Tuple[float, float],
                                customer_location: Tuple[float, float]) -> int:
        """Estimate delivery time in minutes."""
        dist_to_restaurant = self.calculate_distance(restaurant_location)
        dist_to_customer = ((customer_location[0] - restaurant_location[0]) ** 2 + 
                           (customer_location[1] - restaurant_location[1]) ** 2) ** 0.5 * 111
        total_distance = dist_to_restaurant + dist_to_customer
        return int(total_distance / self.get_speed_rating())
    
    def assign_order(self, order: 'Order') -> None:
        """Assign an order to this driver."""
        if not self.is_available:
            raise DeliveryPersonException(f"Driver {self.name} is not available")
        self._current_order = order
        print(f"[Driver] {self.name} assigned to order {order.order_id}")
    
    def complete_delivery(self) -> None:
        """Mark current delivery as complete."""
        if self._current_order:
            self._completed_deliveries += 1
            self._current_order = None
            print(f"[Driver] {self.name} completed delivery #{self._completed_deliveries}")
    
    # Rateable interface
    def add_rating(self, rating: int, review: str = "") -> None:
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        self._ratings.append({
            "rating": rating,
            "review": review,
            "timestamp": datetime.now()
        })
    
    def get_average_rating(self) -> float:
        if not self._ratings:
            return 4.0  # Default rating for new drivers
        return sum(r["rating"] for r in self._ratings) / len(self._ratings)
    
    def get_reviews(self) -> List[Dict[str, Any]]:
        return self._ratings.copy()
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name}, {self.vehicle_type.name})"


class BikeDelivery(DeliveryPerson):
    """Delivery person using a bicycle/motorcycle."""
    
    @property
    def vehicle_type(self) -> VehicleType:
        return VehicleType.BIKE
    
    @property
    def max_range(self) -> float:
        return 8.0  # km
    
    @property
    def max_capacity(self) -> int:
        return 3  # orders
    
    def get_speed_rating(self) -> float:
        return 0.5  # km per minute (30 km/h average)


class CarDelivery(DeliveryPerson):
    """Delivery person using a car."""
    
    @property
    def vehicle_type(self) -> VehicleType:
        return VehicleType.CAR
    
    @property
    def max_range(self) -> float:
        return 15.0
    
    @property
    def max_capacity(self) -> int:
        return 5
    
    def get_speed_rating(self) -> float:
        return 0.6  # km per minute (36 km/h with traffic)


class WalkingDelivery(DeliveryPerson):
    """Delivery person on foot (for short distances)."""
    
    @property
    def vehicle_type(self) -> VehicleType:
        return VehicleType.WALKING
    
    @property
    def max_range(self) -> float:
        return 2.0
    
    @property
    def max_capacity(self) -> int:
        return 2
    
    def get_speed_rating(self) -> float:
        return 0.08  # km per minute (5 km/h)


# =============================================================================
# SECTION 8: CUSTOMER AND CART
# =============================================================================

@dataclass
class CartItem:
    """Represents an item in the shopping cart."""
    menu_item: MenuItem
    quantity: int
    special_instructions: str = ""
    
    def get_subtotal(self) -> float:
        return self.menu_item.calculate_price() * self.quantity


class Customer:
    """
    Represents a customer on the platform.
    
    Demonstrates encapsulation with private payment info.
    """
    
    def __init__(self, customer_id: str, name: str, email: str,
                 phone: str, address: str, location: Tuple[float, float]):
        self._customer_id = customer_id
        self._name = name
        self._email = email
        self._phone = phone
        self._address = address
        self._location = location
        self._payment_methods: List[Dict[str, str]] = []  # Private
        self._is_subscriber = False
        self._subscription_expiry: Optional[datetime] = None
        self._order_history: List[str] = []
    
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
    def phone(self) -> str:
        return self._phone
    
    @property
    def address(self) -> str:
        return self._address
    
    @property
    def location(self) -> Tuple[float, float]:
        return self._location
    
    @property
    def is_subscriber(self) -> bool:
        """Check if customer has active subscription."""
        if self._subscription_expiry is None:
            return False
        return datetime.now() < self._subscription_expiry
    
    def add_payment_method(self, method_type: PaymentMethod, 
                           last_four: str, token: str) -> None:
        """Add a payment method (securely stored)."""
        self._payment_methods.append({
            "type": method_type.value,
            "last_four": last_four,
            "token": token  # In real system, this would be encrypted
        })
    
    def activate_subscription(self, months: int = 1) -> None:
        """Activate unlimited delivery subscription."""
        self._is_subscriber = True
        self._subscription_expiry = datetime.now() + timedelta(days=30 * months)
        print(f"[Customer] {self.name} subscribed until {self._subscription_expiry.date()}")
    
    def add_to_order_history(self, order_id: str) -> None:
        """Add an order to history."""
        self._order_history.append(order_id)
    
    def get_order_history(self) -> List[str]:
        """Get order history (IDs only for privacy)."""
        return self._order_history.copy()
    
    def __repr__(self) -> str:
        return f"Customer({self.name}, {self.email})"


# =============================================================================
# SECTION 9: ORDER HIERARCHY
# =============================================================================

class Order(Orderable, Deliverable, Observable):
    """
    Abstract base class for orders.
    
    Implements multiple interfaces: Orderable, Deliverable, Observable.
    All inherit from ABC so Order is also abstract.
    Demonstrates the Observer pattern for order tracking.
    """
    
    # Valid status transitions
    _VALID_TRANSITIONS = {
        OrderStatus.PLACED: {OrderStatus.ACCEPTED, OrderStatus.CANCELLED},
        OrderStatus.ACCEPTED: {OrderStatus.PREPARING, OrderStatus.CANCELLED},
        OrderStatus.PREPARING: {OrderStatus.READY, OrderStatus.CANCELLED},
        OrderStatus.READY: {OrderStatus.PICKED_UP},
        OrderStatus.PICKED_UP: {OrderStatus.IN_TRANSIT},
        OrderStatus.IN_TRANSIT: {OrderStatus.DELIVERED},
        OrderStatus.DELIVERED: set(),
        OrderStatus.CANCELLED: set()
    }
    
    def __init__(self, order_id: str, customer: Customer, restaurant: Restaurant):
        self._order_id = order_id
        self._customer = customer
        self._restaurant = restaurant
        self._cart: List[CartItem] = []
        self._status = OrderStatus.PLACED
        self._driver: Optional[DeliveryPerson] = None
        self._created_at = datetime.now()
        self._updated_at = datetime.now()
        self._observers: List[Observer] = []
        self._delivery_fee = 0.0
        self._tip = 0.0
        self._promo_code: Optional['PromoCode'] = None
        self._payment_method: Optional[PaymentMethod] = None
        self._special_instructions = ""
    
    @property
    def order_id(self) -> str:
        return self._order_id
    
    @property
    def customer(self) -> Customer:
        return self._customer
    
    @property
    def restaurant(self) -> Restaurant:
        return self._restaurant
    
    @property
    def status(self) -> OrderStatus:
        return self._status
    
    @property
    def cart(self) -> List[CartItem]:
        return self._cart.copy()
    
    @property
    def driver(self) -> Optional[DeliveryPerson]:
        return self._driver
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    @abstractmethod
    def order_type(self) -> str:
        """Get the order type name."""
        pass
    
    @abstractmethod
    def validate_order(self) -> bool:
        """Validate the order before placement."""
        pass
    
    def update_status(self, new_status: OrderStatus) -> None:
        """Update order status with validation."""
        if new_status not in self._VALID_TRANSITIONS[self._status]:
            raise InvalidOrderStatusError(self._status, new_status)
        
        old_status = self._status
        self._status = new_status
        self._updated_at = datetime.now()
        
        self.notify_observers("status_changed", {
            "order_id": self._order_id,
            "old_status": old_status.value,
            "new_status": new_status.value,
            "timestamp": self._updated_at.isoformat()
        })
    
    # Orderable interface
    def add_to_cart(self, item: MenuItem, quantity: int = 1) -> None:
        """Add an item to the cart."""
        if not item.is_available:
            raise ItemNotAvailableError(item.name)
        
        # Check if item already in cart
        for cart_item in self._cart:
            if cart_item.menu_item.item_id == item.item_id:
                cart_item.quantity += quantity
                return
        
        self._cart.append(CartItem(menu_item=item, quantity=quantity))
    
    def remove_from_cart(self, item: MenuItem, quantity: int = 1) -> None:
        """Remove an item from the cart."""
        for i, cart_item in enumerate(self._cart):
            if cart_item.menu_item.item_id == item.item_id:
                cart_item.quantity -= quantity
                if cart_item.quantity <= 0:
                    self._cart.pop(i)
                return
    
    def calculate_subtotal(self) -> float:
        """Calculate the subtotal of all items."""
        return sum(item.get_subtotal() for item in self._cart)
    
    # Deliverable interface
    def assign_driver(self, driver: DeliveryPerson) -> None:
        """Assign a delivery driver."""
        self._driver = driver
        driver.assign_order(self)
        self.notify_observers("driver_assigned", {
            "order_id": self._order_id,
            "driver_name": driver.name,
            "vehicle_type": driver.vehicle_type.name
        })
    
    def track_delivery(self) -> Dict[str, Any]:
        """Get current delivery tracking info."""
        return {
            "order_id": self._order_id,
            "status": self._status.value,
            "driver": self._driver.name if self._driver else None,
            "driver_location": self._driver.current_location if self._driver else None,
            "estimated_arrival": self.estimate_delivery_time()
        }
    
    def confirm_delivery(self) -> None:
        """Confirm delivery completion."""
        self.update_status(OrderStatus.DELIVERED)
        if self._driver:
            self._driver.complete_delivery()
    
    # Observable interface
    def add_observer(self, observer: Observer) -> None:
        """Register an observer."""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def remove_observer(self, observer: Observer) -> None:
        """Unregister an observer."""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify_observers(self, event: str, data: Dict[str, Any]) -> None:
        """Notify all observers of an event."""
        for observer in self._observers:
            observer.update(event, data)
    
    def apply_promo_code(self, promo: 'PromoCode') -> float:
        """Apply a promo code and return discount amount."""
        if not promo.is_valid():
            return 0.0
        
        self._promo_code = promo
        discount = promo.calculate_discount(self.calculate_subtotal(), self._delivery_fee)
        promo.use()
        return discount
    
    def calculate_delivery_fee(self, distance: float) -> float:
        """Calculate delivery fee based on distance."""
        if self._customer.is_subscriber:
            return 0.0  # Free delivery for subscribers
        
        base_fee = 2.99
        per_km_fee = 0.50
        fee = base_fee + (distance * per_km_fee)
        
        # Free delivery over $30
        if self.calculate_subtotal() >= 30.0:
            return 0.0
        
        return round(fee, 2)
    
    def calculate_surge_multiplier(self) -> float:
        """Calculate surge pricing multiplier based on time."""
        now = datetime.now()
        hour = now.hour
        
        # Lunch surge: 12-2 PM
        if 12 <= hour < 14:
            return 1.25
        # Dinner surge: 6-8 PM
        elif 18 <= hour < 20:
            return 1.30
        # Late night: 10 PM - 12 AM
        elif 22 <= hour < 24:
            return 1.15
        return 1.0
    
    def calculate_total(self) -> float:
        """Calculate final order total."""
        subtotal = self.calculate_subtotal()
        distance = self._restaurant.calculate_distance(self._customer.location)
        self._delivery_fee = self.calculate_delivery_fee(distance)
        
        # Apply surge pricing
        surge = self.calculate_surge_multiplier()
        delivery_with_surge = self._delivery_fee * surge
        
        # Calculate discount from promo
        discount = 0.0
        if self._promo_code:
            discount = self._promo_code.calculate_discount(subtotal, delivery_with_surge)
        
        total = subtotal + delivery_with_surge + self._tip - discount
        return round(max(total, 0), 2)
    
    def estimate_delivery_time(self) -> int:
        """Estimate total delivery time in minutes."""
        prep_time = self._restaurant.get_prep_time()
        
        if self._driver:
            delivery_time = self._driver.estimate_delivery_time(
                self._restaurant.location,
                self._customer.location
            )
        else:
            # Estimate without driver
            distance = self._restaurant.calculate_distance(self._customer.location)
            delivery_time = int(distance / 0.5)  # Assume average speed
        
        return prep_time + delivery_time
    
    def set_tip(self, amount: float) -> None:
        """Set tip amount."""
        if amount < 0:
            raise ValueError("Tip cannot be negative")
        self._tip = amount
    
    def cancel(self) -> float:
        """
        Cancel the order and return refund amount.
        
        Refund rules:
        - Before accepted: Full refund
        - After accepted, before preparing: 80% refund
        - After preparing starts: 50% refund
        - After ready: No refund
        """
        if self._status in {OrderStatus.READY, OrderStatus.PICKED_UP, 
                            OrderStatus.IN_TRANSIT, OrderStatus.DELIVERED}:
            raise OrderCancellationError(self._order_id, self._status)
        
        total = self.calculate_total()
        
        if self._status == OrderStatus.PLACED:
            refund = total
        elif self._status == OrderStatus.ACCEPTED:
            refund = total * 0.8
        else:  # PREPARING
            refund = total * 0.5
        
        self.update_status(OrderStatus.CANCELLED)
        return round(refund, 2)
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._order_id}, {self._status.value})"


class StandardOrder(Order):
    """Standard delivery order for immediate delivery."""
    
    @property
    def order_type(self) -> str:
        return "Standard"
    
    def validate_order(self) -> bool:
        """Validate standard order requirements."""
        if not self._restaurant.is_open:
            raise RestaurantClosedError(
                self._restaurant.name, 
                self._restaurant.get_opening_hours()
            )
        
        subtotal = self.calculate_subtotal()
        if subtotal < self._restaurant.minimum_order:
            raise MinimumOrderNotMetError(subtotal, self._restaurant.minimum_order)
        
        if not self._restaurant.can_deliver_to(self._customer.location):
            distance = self._restaurant.calculate_distance(self._customer.location)
            raise OutOfDeliveryRangeError(distance, self._restaurant.delivery_radius)
        
        return True


class ScheduledOrder(Order):
    """Order scheduled for future delivery."""
    
    def __init__(self, order_id: str, customer: Customer, restaurant: Restaurant,
                 scheduled_time: datetime):
        super().__init__(order_id, customer, restaurant)
        self._scheduled_time = scheduled_time
    
    @property
    def order_type(self) -> str:
        return "Scheduled"
    
    @property
    def scheduled_time(self) -> datetime:
        return self._scheduled_time
    
    def validate_order(self) -> bool:
        """Validate scheduled order requirements."""
        # Must be at least 30 minutes in the future
        if self._scheduled_time < datetime.now() + timedelta(minutes=30):
            raise OrderException("Scheduled time must be at least 30 minutes from now")
        
        # Must be within 7 days
        if self._scheduled_time > datetime.now() + timedelta(days=7):
            raise OrderException("Cannot schedule orders more than 7 days in advance")
        
        subtotal = self.calculate_subtotal()
        if subtotal < self._restaurant.minimum_order:
            raise MinimumOrderNotMetError(subtotal, self._restaurant.minimum_order)
        
        return True


class GroupOrder(Order):
    """Order that allows multiple people to add items."""
    
    def __init__(self, order_id: str, customer: Customer, restaurant: Restaurant,
                 organizer_name: str):
        super().__init__(order_id, customer, restaurant)
        self._organizer = organizer_name
        self._participants: Dict[str, List[CartItem]] = {organizer_name: []}
        self._is_open_for_additions = True
    
    @property
    def order_type(self) -> str:
        return "Group"
    
    @property
    def participants(self) -> List[str]:
        return list(self._participants.keys())
    
    def add_participant(self, name: str) -> None:
        """Add a participant to the group order."""
        if not self._is_open_for_additions:
            raise OrderException("Group order is closed for additions")
        self._participants[name] = []
    
    def add_item_for_participant(self, participant: str, item: MenuItem, 
                                  quantity: int = 1) -> None:
        """Add an item for a specific participant."""
        if participant not in self._participants:
            raise OrderException(f"Participant '{participant}' not in group")
        
        if not item.is_available:
            raise ItemNotAvailableError(item.name)
        
        self._participants[participant].append(
            CartItem(menu_item=item, quantity=quantity)
        )
        # Also add to main cart
        self.add_to_cart(item, quantity)
    
    def close_for_additions(self) -> None:
        """Close the group order for new additions."""
        self._is_open_for_additions = False
    
    def get_participant_subtotal(self, participant: str) -> float:
        """Get subtotal for a specific participant."""
        if participant not in self._participants:
            return 0.0
        return sum(item.get_subtotal() for item in self._participants[participant])
    
    def validate_order(self) -> bool:
        """Validate group order requirements."""
        if not self._restaurant.is_open:
            raise RestaurantClosedError(self._restaurant.name)
        
        subtotal = self.calculate_subtotal()
        # Group orders have higher minimum
        min_order = self._restaurant.minimum_order * 1.5
        if subtotal < min_order:
            raise MinimumOrderNotMetError(subtotal, min_order)
        
        return True


class SubscriptionOrder(Order):
    """Recurring subscription-based order."""
    
    def __init__(self, order_id: str, customer: Customer, restaurant: Restaurant,
                 frequency: str = "weekly"):
        super().__init__(order_id, customer, restaurant)
        self._frequency = frequency  # "daily", "weekly", "biweekly"
        self._next_delivery: Optional[datetime] = None
        self._is_active = True
    
    @property
    def order_type(self) -> str:
        return "Subscription"
    
    @property
    def frequency(self) -> str:
        return self._frequency
    
    @property
    def is_active(self) -> bool:
        return self._is_active
    
    def pause_subscription(self) -> None:
        """Pause the subscription."""
        self._is_active = False
        print(f"[Subscription] Order {self._order_id} paused")
    
    def resume_subscription(self) -> None:
        """Resume the subscription."""
        self._is_active = True
        self._calculate_next_delivery()
        print(f"[Subscription] Order {self._order_id} resumed")
    
    def _calculate_next_delivery(self) -> None:
        """Calculate the next delivery date."""
        now = datetime.now()
        if self._frequency == "daily":
            self._next_delivery = now + timedelta(days=1)
        elif self._frequency == "weekly":
            self._next_delivery = now + timedelta(weeks=1)
        elif self._frequency == "biweekly":
            self._next_delivery = now + timedelta(weeks=2)
    
    def validate_order(self) -> bool:
        """Validate subscription order requirements."""
        if not self._customer.is_subscriber:
            raise OrderException("Customer must have active subscription for recurring orders")
        
        subtotal = self.calculate_subtotal()
        if subtotal < self._restaurant.minimum_order:
            raise MinimumOrderNotMetError(subtotal, self._restaurant.minimum_order)
        
        return True


# =============================================================================
# SECTION 10: PROMO CODES
# =============================================================================

class PromoCode:
    """Represents a promotional discount code."""
    
    def __init__(self, code: str, discount_type: str, discount_value: float,
                 min_order: float = 0.0, max_discount: Optional[float] = None,
                 free_delivery: bool = False, max_uses: int = 1,
                 expiry_date: Optional[datetime] = None):
        self._code = code.upper()
        self._discount_type = discount_type  # "percentage", "fixed", "free_delivery"
        self._discount_value = discount_value
        self._min_order = min_order
        self._max_discount = max_discount
        self._free_delivery = free_delivery
        self._max_uses = max_uses
        self._uses = 0
        self._expiry_date = expiry_date
    
    @property
    def code(self) -> str:
        return self._code
    
    def is_valid(self) -> bool:
        """Check if promo code is valid."""
        if self._uses >= self._max_uses:
            return False
        if self._expiry_date and datetime.now() > self._expiry_date:
            return False
        return True
    
    def can_apply(self, subtotal: float) -> bool:
        """Check if promo can be applied to an order."""
        return self.is_valid() and subtotal >= self._min_order
    
    def calculate_discount(self, subtotal: float, delivery_fee: float) -> float:
        """Calculate the discount amount."""
        if not self.can_apply(subtotal):
            return 0.0
        
        if self._free_delivery:
            return delivery_fee
        
        if self._discount_type == "percentage":
            discount = subtotal * (self._discount_value / 100)
        elif self._discount_type == "fixed":
            discount = self._discount_value
        else:
            discount = 0.0
        
        if self._max_discount:
            discount = min(discount, self._max_discount)
        
        return round(discount, 2)
    
    def use(self) -> None:
        """Mark the promo code as used."""
        self._uses += 1
    
    def __repr__(self) -> str:
        return f"PromoCode({self._code}, {self._discount_type})"


# =============================================================================
# SECTION 11: OBSERVER PATTERN - Order Tracking System
# =============================================================================

class CustomerNotifier(Observer):
    """Notifies customers about order updates."""
    
    def __init__(self, customer: Customer):
        self._customer = customer
    
    def update(self, event: str, data: Dict[str, Any]) -> None:
        """Handle notification."""
        if event == "status_changed":
            print(f"  📱 SMS to {self._customer.name}: "
                  f"Order {data['order_id'][:8]}... is now {data['new_status']}")
        elif event == "driver_assigned":
            print(f"  📱 SMS to {self._customer.name}: "
                  f"{data['driver_name']} is picking up your order")


class RestaurantNotifier(Observer):
    """Notifies restaurant about order updates."""
    
    def __init__(self, restaurant: Restaurant):
        self._restaurant = restaurant
    
    def update(self, event: str, data: Dict[str, Any]) -> None:
        """Handle notification."""
        if event == "status_changed":
            if data['new_status'] == 'placed':
                print(f"  🔔 Alert to {self._restaurant.name}: "
                      f"New order received! ID: {data['order_id'][:8]}...")
            elif data['new_status'] == 'cancelled':
                print(f"  🔔 Alert to {self._restaurant.name}: "
                      f"Order {data['order_id'][:8]}... cancelled")


class DriverNotifier(Observer):
    """Notifies drivers about delivery assignments."""
    
    def __init__(self, driver: DeliveryPerson):
        self._driver = driver
    
    def update(self, event: str, data: Dict[str, Any]) -> None:
        """Handle notification."""
        if event == "status_changed":
            if data['new_status'] == 'ready':
                print(f"  🚗 Alert to {self._driver.name}: "
                      f"Order {data['order_id'][:8]}... ready for pickup!")
        elif event == "driver_assigned":
            print(f"  🚗 Alert to {self._driver.name}: "
                  f"New delivery assigned!")


class SupportDashboard(Observer):
    """Central dashboard for customer support to monitor orders."""
    
    def __init__(self, name: str = "Support Dashboard"):
        self._name = name
        self._events_logged: List[Dict[str, Any]] = []
    
    def update(self, event: str, data: Dict[str, Any]) -> None:
        """Log all events for support monitoring."""
        log_entry = {
            "event": event,
            "data": data,
            "logged_at": datetime.now().isoformat()
        }
        self._events_logged.append(log_entry)
        print(f"  📊 {self._name}: {event} - Order {data.get('order_id', 'N/A')[:8]}...")
    
    @property
    def event_count(self) -> int:
        return len(self._events_logged)


class OrderTrackingSystem:
    """
    Central order tracking system implementing Observer pattern.
    
    Manages observers and routes notifications appropriately.
    """
    
    def __init__(self):
        self._support_dashboard = SupportDashboard()
        print("[Tracking] Order Tracking System initialized")
    
    @property
    def support_dashboard(self) -> SupportDashboard:
        return self._support_dashboard
    
    def setup_order_tracking(self, order: Order, driver: Optional[DeliveryPerson] = None) -> None:
        """Set up all observers for an order."""
        # Always add support dashboard
        order.add_observer(self._support_dashboard)
        
        # Add customer notifier
        order.add_observer(CustomerNotifier(order.customer))
        
        # Add restaurant notifier
        order.add_observer(RestaurantNotifier(order.restaurant))
        
        # Add driver notifier if assigned
        if driver:
            order.add_observer(DriverNotifier(driver))
        
        print(f"[Tracking] Observers set up for order {order.order_id[:8]}...")


# =============================================================================
# SECTION 12: FACTORY PATTERN
# =============================================================================

class RestaurantFactory:
    """
    Factory for creating restaurant instances.
    
    Centralizes restaurant creation logic and ensures proper initialization.
    """
    
    @staticmethod
    def create_restaurant(restaurant_type: RestaurantType, name: str,
                          address: str, location: Tuple[float, float],
                          cuisine_type: str) -> Restaurant:
        """Create a restaurant based on type."""
        restaurant_id = f"rest_{uuid.uuid4().hex[:8]}"
        
        if restaurant_type == RestaurantType.FAST_FOOD:
            restaurant = FastFood(restaurant_id, name, address, location, cuisine_type)
        elif restaurant_type == RestaurantType.CASUAL_DINING:
            restaurant = CasualDining(restaurant_id, name, address, location, cuisine_type)
        elif restaurant_type == RestaurantType.FINE_DINING:
            restaurant = FineDining(restaurant_id, name, address, location, cuisine_type)
        elif restaurant_type == RestaurantType.CLOUD_KITCHEN:
            restaurant = CloudKitchen(restaurant_id, name, address, location, cuisine_type)
        else:
            raise ValueError(f"Unknown restaurant type: {restaurant_type}")
        
        print(f"[Factory] Created {restaurant_type.name} restaurant: {name}")
        return restaurant


class OrderFactory:
    """
    Factory for creating order instances.
    
    Handles order ID generation and proper initialization.
    """
    
    @staticmethod
    def create_order(order_type: str, customer: Customer, restaurant: Restaurant,
                     **kwargs) -> Order:
        """Create an order based on type."""
        order_id = f"ord_{uuid.uuid4().hex[:8]}"
        
        if order_type == "standard":
            order = StandardOrder(order_id, customer, restaurant)
        elif order_type == "scheduled":
            scheduled_time = kwargs.get('scheduled_time', datetime.now() + timedelta(hours=2))
            order = ScheduledOrder(order_id, customer, restaurant, scheduled_time)
        elif order_type == "group":
            organizer = kwargs.get('organizer_name', customer.name)
            order = GroupOrder(order_id, customer, restaurant, organizer)
        elif order_type == "subscription":
            frequency = kwargs.get('frequency', 'weekly')
            order = SubscriptionOrder(order_id, customer, restaurant, frequency)
        else:
            raise ValueError(f"Unknown order type: {order_type}")
        
        print(f"[Factory] Created {order_type} order: {order_id[:12]}...")
        return order


class DeliveryPersonFactory:
    """Factory for creating delivery person instances."""
    
    @staticmethod
    def create_driver(vehicle_type: VehicleType, name: str, phone: str,
                      location: Tuple[float, float]) -> DeliveryPerson:
        """Create a delivery person based on vehicle type."""
        driver_id = f"drv_{uuid.uuid4().hex[:8]}"
        
        if vehicle_type == VehicleType.BIKE:
            driver = BikeDelivery(driver_id, name, phone, location)
        elif vehicle_type == VehicleType.CAR:
            driver = CarDelivery(driver_id, name, phone, location)
        elif vehicle_type == VehicleType.WALKING:
            driver = WalkingDelivery(driver_id, name, phone, location)
        else:
            raise ValueError(f"Unknown vehicle type: {vehicle_type}")
        
        print(f"[Factory] Created {vehicle_type.name} driver: {name}")
        return driver


# =============================================================================
# SECTION 13: ADAPTER PATTERN - Legacy Menu Integration
# =============================================================================

@dataclass
class LegacyMenuItem:
    """
    Represents menu data from a legacy POS system.
    
    Note the differences from our platform's format:
    - Price in cents instead of dollars
    - Category codes instead of class types
    - Different field names
    """
    item_code: str
    item_name: str
    desc: str
    price_cents: int
    cat_code: str  # "M" = Main, "S" = Side, "B" = Beverage, "D" = Dessert
    dietary_codes: str  # Comma-separated: "V,GF,NF"


class LegacyMenuAdapter:
    """
    Adapter to convert legacy menu data to platform format.
    
    This demonstrates the Adapter pattern - converting one interface
    to another without modifying the original classes.
    """
    
    # Mapping from legacy category codes to our classes
    _CATEGORY_MAP = {
        "M": MainDish,
        "S": SideDish,
        "B": Beverage,
        "D": Dessert
    }
    
    # Mapping from legacy dietary codes to our enum
    _DIETARY_MAP = {
        "V": DietaryTag.VEGETARIAN,
        "VG": DietaryTag.VEGAN,
        "GF": DietaryTag.GLUTEN_FREE,
        "H": DietaryTag.HALAL,
        "K": DietaryTag.KOSHER,
        "NF": DietaryTag.NUT_FREE
    }
    
    def __init__(self):
        self._adapted_count = 0
    
    def adapt(self, legacy_item: LegacyMenuItem) -> MenuItem:
        """Convert a legacy menu item to platform format."""
        # Convert price from cents to dollars
        price = legacy_item.price_cents / 100.0
        
        # Convert dietary codes to tags
        dietary_tags = set()
        if legacy_item.dietary_codes:
            for code in legacy_item.dietary_codes.split(","):
                code = code.strip()
                if code in self._DIETARY_MAP:
                    dietary_tags.add(self._DIETARY_MAP[code])
        
        # Get the appropriate class
        item_class = self._CATEGORY_MAP.get(legacy_item.cat_code, MainDish)
        
        # Create the new menu item
        item = item_class(
            item_id=f"leg_{legacy_item.item_code}",
            name=legacy_item.item_name,
            description=legacy_item.desc,
            base_price=price,
            dietary_tags=dietary_tags
        )
        
        self._adapted_count += 1
        return item
    
    def adapt_menu(self, legacy_items: List[LegacyMenuItem]) -> List[MenuItem]:
        """Convert a list of legacy items."""
        return [self.adapt(item) for item in legacy_items]
    
    @property
    def adapted_count(self) -> int:
        """Get count of adapted items."""
        return self._adapted_count


# =============================================================================
# SECTION 14: HELPER FUNCTIONS
# =============================================================================

def create_sample_menu(restaurant: Restaurant) -> None:
    """Create a sample menu for a restaurant."""
    # Main dishes
    burger = MainDish(
        f"{restaurant.restaurant_id}_burger",
        "Classic Burger",
        "Beef patty with lettuce, tomato, and special sauce",
        12.99
    )
    burger.add_customization(Customization(
        "Cheese", ["None", "Cheddar", "Swiss", "Blue"], 1.50
    ))
    
    salad = MainDish(
        f"{restaurant.restaurant_id}_salad",
        "Garden Salad",
        "Fresh mixed greens with vinaigrette",
        9.99,
        dietary_tags={DietaryTag.VEGETARIAN, DietaryTag.VEGAN, DietaryTag.GLUTEN_FREE}
    )
    
    pasta = MainDish(
        f"{restaurant.restaurant_id}_pasta",
        "Pasta Primavera",
        "Penne with seasonal vegetables in marinara",
        14.99,
        dietary_tags={DietaryTag.VEGETARIAN}
    )
    
    # Sides
    fries = SideDish(
        f"{restaurant.restaurant_id}_fries",
        "French Fries",
        "Crispy golden fries",
        4.99,
        dietary_tags={DietaryTag.VEGAN, DietaryTag.GLUTEN_FREE}
    )
    
    # Beverages
    soda = Beverage(
        f"{restaurant.restaurant_id}_soda",
        "Soft Drink",
        "Choice of cola, sprite, or orange",
        2.99
    )
    
    # Desserts
    cake = Dessert(
        f"{restaurant.restaurant_id}_cake",
        "Chocolate Cake",
        "Rich chocolate layer cake",
        6.99,
        dietary_tags={DietaryTag.VEGETARIAN}
    )
    
    # Combo
    combo = Combo(
        f"{restaurant.restaurant_id}_combo1",
        "Burger Combo",
        "Burger + Fries + Drink",
        [burger, fries, soda],
        discount_percentage=15.0
    )
    
    # Add all items to restaurant
    for item in [burger, salad, pasta, fries, soda, cake, combo]:
        restaurant.add_menu_item(item)


def simulate_order_lifecycle(order: Order, driver: DeliveryPerson,
                              tracking_system: OrderTrackingSystem) -> None:
    """Simulate an order going through all statuses."""
    print(f"\n{'='*60}")
    print(f"SIMULATING ORDER LIFECYCLE: {order.order_id[:12]}...")
    print(f"{'='*60}")
    
    # Set up tracking
    tracking_system.setup_order_tracking(order, driver)
    
    # Place order (already in PLACED status)
    print("\n[Order] Order placed")
    order.notify_observers("status_changed", {
        "order_id": order.order_id,
        "old_status": None,
        "new_status": "placed",
        "timestamp": datetime.now().isoformat()
    })
    
    # Restaurant accepts
    print("\n[Order] Restaurant accepting...")
    order.update_status(OrderStatus.ACCEPTED)
    
    # Start preparing
    print("\n[Order] Starting preparation...")
    order.update_status(OrderStatus.PREPARING)
    
    # Order ready
    print("\n[Order] Order ready for pickup...")
    order.update_status(OrderStatus.READY)
    
    # Assign driver and pickup
    order.assign_driver(driver)
    print("\n[Order] Driver picking up...")
    order.update_status(OrderStatus.PICKED_UP)
    
    # In transit
    print("\n[Order] Driver en route...")
    order.update_status(OrderStatus.IN_TRANSIT)
    
    # Delivered
    print("\n[Order] Delivering...")
    order.confirm_delivery()
    
    print(f"\n✅ Order {order.order_id[:12]}... completed successfully!")


# =============================================================================
# SECTION 15: MAIN DEMONSTRATION
# =============================================================================

def main():
    """
    Main demonstration function showing all OOP concepts.
    
    Run this to see the complete food delivery platform in action.
    """
    print("=" * 70)
    print("🍕 FOOD DELIVERY PLATFORM - OOP DEMONSTRATION")
    print("=" * 70)
    
    # -------------------------------------------------------------------------
    # 1. SINGLETON PATTERN - Platform Registry
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("1. SINGLETON PATTERN - Platform Registry")
    print("=" * 70)
    
    registry = DeliveryPlatformRegistry()
    
    # Verify singleton - should be same instance
    registry2 = DeliveryPlatformRegistry()
    print(f"Same instance? {registry is registry2}")  # True
    
    # -------------------------------------------------------------------------
    # 2. FACTORY PATTERN - Creating Restaurants
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("2. FACTORY PATTERN - Creating Restaurants")
    print("=" * 70)
    
    # Create different types of restaurants using factory
    fast_food = RestaurantFactory.create_restaurant(
        RestaurantType.FAST_FOOD,
        "Burger Barn",
        "123 Fast Lane",
        (40.7128, -74.0060),  # NYC coordinates
        "American"
    )
    
    casual = RestaurantFactory.create_restaurant(
        RestaurantType.CASUAL_DINING,
        "Pasta Palace",
        "456 Casual Ave",
        (40.7200, -74.0100),
        "Italian"
    )
    
    fine_dining = RestaurantFactory.create_restaurant(
        RestaurantType.FINE_DINING,
        "Le Gourmet",
        "789 Fancy Blvd",
        (40.7150, -74.0080),
        "French"
    )
    
    cloud_kitchen = RestaurantFactory.create_restaurant(
        RestaurantType.CLOUD_KITCHEN,
        "Ghost Grills",
        "321 Cloud St",
        (40.7180, -74.0050),
        "Multi-Cuisine"
    )
    
    # Show restaurant properties (polymorphism)
    print("\n📊 Restaurant Comparison (Polymorphism in action):")
    print("-" * 70)
    print(f"{'Restaurant':<20} {'Type':<15} {'Min Order':<12} {'Radius':<10} {'Commission'}")
    print("-" * 70)
    for rest in [fast_food, casual, fine_dining, cloud_kitchen]:
        print(f"{rest.name:<20} {rest.restaurant_type.name:<15} "
              f"${rest.minimum_order:<10.2f} {rest.delivery_radius:<10.1f} "
              f"{rest.commission_rate*100:.0f}%")
    
    # Register restaurants
    for rest in [fast_food, casual, fine_dining, cloud_kitchen]:
        registry.register_restaurant(rest)
        create_sample_menu(rest)
    
    # -------------------------------------------------------------------------
    # 3. MENU ITEM HIERARCHY
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("3. MENU ITEM HIERARCHY - Different Item Types")
    print("=" * 70)
    
    menu = fast_food.get_menu()
    print(f"\n🍔 {fast_food.name} Menu:")
    print("-" * 50)
    for item in menu:
        tags = ", ".join(t.value for t in item.dietary_tags) or "None"
        print(f"  [{item.get_category():<10}] {item.name:<20} "
              f"${item.calculate_price():.2f} (Tags: {tags})")
    
    # -------------------------------------------------------------------------
    # 4. ADAPTER PATTERN - Legacy Menu Integration
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("4. ADAPTER PATTERN - Legacy Menu Integration")
    print("=" * 70)
    
    # Simulate legacy menu data from old POS system
    legacy_items = [
        LegacyMenuItem("001", "Pad Thai", "Classic Thai noodles", 1299, "M", "GF"),
        LegacyMenuItem("002", "Spring Rolls", "Crispy veggie rolls", 599, "S", "V,VG"),
        LegacyMenuItem("003", "Thai Iced Tea", "Sweet milk tea", 399, "B", "V"),
        LegacyMenuItem("004", "Mango Sticky Rice", "Thai dessert", 699, "D", "V,GF")
    ]
    
    print("\n📋 Legacy menu data (raw format):")
    for item in legacy_items:
        print(f"  Code: {item.item_code}, Name: {item.item_name}, "
              f"Price: {item.price_cents}¢, Cat: {item.cat_code}")
    
    # Use adapter to convert
    adapter = LegacyMenuAdapter()
    adapted_items = adapter.adapt_menu(legacy_items)
    
    print(f"\n✨ Adapted menu items ({adapter.adapted_count} converted):")
    for item in adapted_items:
        tags = ", ".join(t.value for t in item.dietary_tags) or "None"
        print(f"  [{item.get_category():<10}] {item.name:<25} "
              f"${item.calculate_price():.2f} (Tags: {tags})")
    
    # Add adapted items to cloud kitchen
    for item in adapted_items:
        cloud_kitchen.add_menu_item(item)
    
    # -------------------------------------------------------------------------
    # 5. DELIVERY PERSON HIERARCHY
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("5. DELIVERY PERSON HIERARCHY")
    print("=" * 70)
    
    # Create drivers using factory
    bike_driver = DeliveryPersonFactory.create_driver(
        VehicleType.BIKE, "Alex Rider", "555-0101", (40.7130, -74.0055)
    )
    car_driver = DeliveryPersonFactory.create_driver(
        VehicleType.CAR, "Carol Driver", "555-0102", (40.7140, -74.0070)
    )
    walking_driver = DeliveryPersonFactory.create_driver(
        VehicleType.WALKING, "Wade Walker", "555-0103", (40.7125, -74.0058)
    )
    
    # Register drivers
    for driver in [bike_driver, car_driver, walking_driver]:
        registry.register_driver(driver)
    
    # Show driver properties
    print("\n🚗 Driver Comparison:")
    print("-" * 70)
    print(f"{'Driver':<15} {'Vehicle':<10} {'Range':<10} {'Capacity':<10} {'Speed'}")
    print("-" * 70)
    for driver in [bike_driver, car_driver, walking_driver]:
        print(f"{driver.name:<15} {driver.vehicle_type.name:<10} "
              f"{driver.max_range:<10.1f} {driver.max_capacity:<10} "
              f"{driver.get_speed_rating():.2f} km/min")
    
    # -------------------------------------------------------------------------
    # 6. CUSTOMER CREATION
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("6. CUSTOMER CREATION WITH ENCAPSULATION")
    print("=" * 70)
    
    customer = Customer(
        customer_id="cust_001",
        name="John Doe",
        email="john@example.com",
        phone="555-1234",
        address="100 Customer St, NYC",
        location=(40.7135, -74.0065)
    )
    
    # Add payment method (encapsulated)
    customer.add_payment_method(PaymentMethod.CREDIT_CARD, "4242", "tok_visa")
    print(f"Customer: {customer.name}")
    print(f"  Email: {customer.email}")
    print(f"  Is Subscriber: {customer.is_subscriber}")
    
    # Activate subscription
    customer.activate_subscription(months=1)
    print(f"  Is Subscriber (after activation): {customer.is_subscriber}")
    
    registry.register_customer(customer)
    
    # -------------------------------------------------------------------------
    # 7. PROMO CODES
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("7. PROMO CODE SYSTEM")
    print("=" * 70)
    
    # Create various promo codes
    promo_percent = PromoCode(
        code="SAVE20",
        discount_type="percentage",
        discount_value=20.0,
        min_order=15.0,
        max_discount=10.0
    )
    
    promo_fixed = PromoCode(
        code="FLAT5",
        discount_type="fixed",
        discount_value=5.0,
        min_order=20.0
    )
    
    promo_delivery = PromoCode(
        code="FREEDELIVERY",
        discount_type="free_delivery",
        discount_value=0,
        free_delivery=True
    )
    
    for promo in [promo_percent, promo_fixed, promo_delivery]:
        registry.add_promo_code(promo)
    
    print("Available promo codes:")
    print(f"  SAVE20: 20% off (max $10, min order $15)")
    print(f"  FLAT5: $5 off (min order $20)")
    print(f"  FREEDELIVERY: Free delivery on any order")
    
    # -------------------------------------------------------------------------
    # 8. ORDER FACTORY AND TYPES
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("8. ORDER FACTORY - Different Order Types")
    print("=" * 70)
    
    # Create different order types
    standard_order = OrderFactory.create_order("standard", customer, fast_food)
    
    scheduled_order = OrderFactory.create_order(
        "scheduled", customer, casual,
        scheduled_time=datetime.now() + timedelta(hours=3)
    )
    
    group_order = OrderFactory.create_order(
        "group", customer, fast_food,
        organizer_name="John Doe"
    )
    
    # Add items to standard order
    burger = fast_food.get_menu_item(f"{fast_food.restaurant_id}_burger")
    fries = fast_food.get_menu_item(f"{fast_food.restaurant_id}_fries")
    soda = fast_food.get_menu_item(f"{fast_food.restaurant_id}_soda")
    
    standard_order.add_to_cart(burger, 2)
    standard_order.add_to_cart(fries, 2)
    standard_order.add_to_cart(soda, 2)
    
    print(f"\n📦 Standard Order Contents:")
    for cart_item in standard_order.cart:
        print(f"  {cart_item.quantity}x {cart_item.menu_item.name} "
              f"= ${cart_item.get_subtotal():.2f}")
    
    # -------------------------------------------------------------------------
    # 9. PRICING CALCULATIONS
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("9. PRICING AND SURGE CALCULATIONS")
    print("=" * 70)
    
    subtotal = standard_order.calculate_subtotal()
    surge = standard_order.calculate_surge_multiplier()
    distance = fast_food.calculate_distance(customer.location)
    delivery_fee = standard_order.calculate_delivery_fee(distance)
    
    print(f"Subtotal: ${subtotal:.2f}")
    print(f"Distance: {distance:.2f} km")
    print(f"Delivery fee (before surge): ${delivery_fee:.2f}")
    print(f"Surge multiplier: {surge:.2f}x")
    print(f"Delivery fee (with surge): ${delivery_fee * surge:.2f}")
    
    # Apply promo code
    promo = registry.get_promo_code("SAVE20")
    if promo:
        discount = standard_order.apply_promo_code(promo)
        print(f"Promo SAVE20 discount: -${discount:.2f}")
    
    total = standard_order.calculate_total()
    print(f"TOTAL: ${total:.2f}")
    
    # Note: For subscriber, delivery is free
    print(f"\n💎 Note: {customer.name} is a subscriber - free delivery!")
    
    # -------------------------------------------------------------------------
    # 10. OBSERVER PATTERN - Order Tracking
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("10. OBSERVER PATTERN - Order Tracking System")
    print("=" * 70)
    
    tracking_system = OrderTrackingSystem()
    
    # Validate and register the order
    try:
        standard_order.validate_order()
        registry.register_order(standard_order)
        print(f"✅ Order validated successfully")
    except DeliveryException as e:
        print(f"❌ Validation failed: {e}")
    
    # Run order lifecycle simulation
    simulate_order_lifecycle(standard_order, bike_driver, tracking_system)
    
    # -------------------------------------------------------------------------
    # 11. RATING SYSTEM
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("11. RATING SYSTEM (Rateable Interface)")
    print("=" * 70)
    
    # Rate the restaurant
    fast_food.add_rating(5, "Great burgers, fast delivery!")
    fast_food.add_rating(4, "Good food, slightly cold")
    fast_food.add_rating(5, "Best combo deal in town!")
    
    print(f"\n🌟 {fast_food.name} Ratings:")
    print(f"  Average: {fast_food.get_average_rating():.1f}/5.0")
    print(f"  Reviews: {len(fast_food.get_reviews())}")
    
    # Rate the driver
    bike_driver.add_rating(5, "Super fast!")
    bike_driver.add_rating(5, "Very friendly")
    
    print(f"\n🌟 {bike_driver.name} Ratings:")
    print(f"  Average: {bike_driver.get_average_rating():.1f}/5.0")
    print(f"  Reviews: {len(bike_driver.get_reviews())}")
    
    # -------------------------------------------------------------------------
    # 12. GROUP ORDER DEMONSTRATION
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("12. GROUP ORDER DEMONSTRATION")
    print("=" * 70)
    
    # Add participants to group order
    group_order.add_participant("Alice")
    group_order.add_participant("Bob")
    
    # Each person adds their items
    group_order.add_item_for_participant("John Doe", burger, 1)
    group_order.add_item_for_participant("Alice", 
        fast_food.get_menu_item(f"{fast_food.restaurant_id}_salad"), 1)
    group_order.add_item_for_participant("Bob", burger, 2)
    
    print(f"\n👥 Group Order Participants: {group_order.participants}")
    print(f"Group Order Subtotal: ${group_order.calculate_subtotal():.2f}")
    print(f"\nIndividual subtotals:")
    for participant in group_order.participants:
        subtotal = group_order.get_participant_subtotal(participant)
        print(f"  {participant}: ${subtotal:.2f}")
    
    # -------------------------------------------------------------------------
    # 13. EXCEPTION HANDLING DEMONSTRATION
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("13. CUSTOM EXCEPTION HANDLING")
    print("=" * 70)
    
    print("\n🧪 Testing various exception scenarios:")
    
    # Test RestaurantClosedError
    try:
        fast_food.is_open = False
        test_order = OrderFactory.create_order("standard", customer, fast_food)
        test_order.add_to_cart(burger, 1)
        test_order.validate_order()
    except RestaurantClosedError as e:
        print(f"  ✓ RestaurantClosedError: {e}")
    finally:
        fast_food.is_open = True
    
    # Test MinimumOrderNotMetError
    try:
        test_order = OrderFactory.create_order("standard", customer, fine_dining)
        small_item = Dessert("test_small", "Cookie", "Small cookie", 3.00)
        fine_dining.add_menu_item(small_item)
        test_order.add_to_cart(small_item, 1)
        test_order.validate_order()
    except MinimumOrderNotMetError as e:
        print(f"  ✓ MinimumOrderNotMetError: {e}")
    
    # Test ItemNotAvailableError
    try:
        unavailable = MainDish("unavail", "Unavailable Item", "Out of stock", 15.00)
        unavailable.is_available = False
        test_order.add_to_cart(unavailable, 1)
    except ItemNotAvailableError as e:
        print(f"  ✓ ItemNotAvailableError: {e}")
    
    # Test InvalidOrderStatusError
    try:
        # Can't go from DELIVERED back to PLACED
        standard_order.update_status(OrderStatus.PLACED)
    except InvalidOrderStatusError as e:
        print(f"  ✓ InvalidOrderStatusError: {e}")
    
    # Test NoDriverAvailableError simulation
    try:
        # All drivers busy scenario
        raise NoDriverAvailableError("Downtown Area")
    except NoDriverAvailableError as e:
        print(f"  ✓ NoDriverAvailableError: {e}")
    
    # Test PaymentDeclinedError simulation
    try:
        raise PaymentDeclinedError("Insufficient funds")
    except PaymentDeclinedError as e:
        print(f"  ✓ PaymentDeclinedError: {e}")
    
    # -------------------------------------------------------------------------
    # 14. ORDER CANCELLATION
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("14. ORDER CANCELLATION WITH REFUNDS")
    print("=" * 70)
    
    # Create a new order to cancel
    cancel_order = OrderFactory.create_order("standard", customer, casual)
    pasta = casual.get_menu_item(f"{casual.restaurant_id}_pasta")
    cancel_order.add_to_cart(pasta, 2)
    
    try:
        cancel_order.validate_order()
        registry.register_order(cancel_order)
        
        # Show order before cancellation
        print(f"Order {cancel_order.order_id[:12]}... Status: {cancel_order.status.value}")
        print(f"Total: ${cancel_order.calculate_total():.2f}")
        
        # Cancel while still PLACED = full refund
        refund = cancel_order.cancel()
        print(f"Cancelled! Refund: ${refund:.2f} (100%)")
        
        # Try to cancel already cancelled order
        try:
            cancel_order.cancel()
        except OrderCancellationError as e:
            print(f"Cannot re-cancel: {e}")
            
    except DeliveryException as e:
        print(f"Error: {e}")
    
    # -------------------------------------------------------------------------
    # 15. PLATFORM STATISTICS
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("15. PLATFORM STATISTICS (Singleton Registry)")
    print("=" * 70)
    
    stats = registry.stats
    print(f"\n📈 Platform Statistics:")
    print(f"  Restaurants: {stats['restaurants']}")
    print(f"  Drivers: {stats['drivers']}")
    print(f"  Customers: {stats['customers']}")
    print(f"  Orders: {stats['orders']}")
    print(f"  Promo Codes: {stats['promo_codes']}")
    
    print(f"\n  Support Dashboard Events Logged: {tracking_system.support_dashboard.event_count}")
    
    # -------------------------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("🎓 OOP CONCEPTS DEMONSTRATED SUMMARY")
    print("=" * 70)
    print("""
    ✅ Class Hierarchies with ABC
       - Restaurant: FastFood, CasualDining, FineDining, CloudKitchen
       - MenuItem: MainDish, SideDish, Beverage, Dessert, Combo
       - DeliveryPerson: BikeDelivery, CarDelivery, WalkingDelivery
       - Order: StandardOrder, ScheduledOrder, GroupOrder, SubscriptionOrder
    
    ✅ Interfaces (ABC classes)
       - Orderable: add_to_cart, remove_from_cart, calculate_subtotal
       - Deliverable: assign_driver, track_delivery, confirm_delivery
       - Observable: add_observer, remove_observer, notify_observers
       - Rateable: add_rating, get_average_rating, get_reviews
    
    ✅ Encapsulation
       - Private attributes (_order_id, _customer_address, etc.)
       - Properties with getters/setters and validation
       - Protected order details and payment info
    
    ✅ Custom Exception Hierarchy
       - DeliveryException (base)
       - RestaurantException, OrderException, DeliveryPersonException, PaymentException
       - Specific errors: RestaurantClosedError, MinimumOrderNotMetError, etc.
    
    ✅ Design Patterns
       - Factory Pattern: RestaurantFactory, OrderFactory, DeliveryPersonFactory
       - Adapter Pattern: LegacyMenuAdapter
       - Observer Pattern: OrderTrackingSystem with multiple notifiers
       - Singleton Pattern: DeliveryPlatformRegistry (metaclass)
    
    ✅ Enums
       - RestaurantType, OrderStatus, PaymentMethod, VehicleType
       - DietaryTag, MealPeriod
    
    ✅ Business Rules
       - Operating hours, minimum orders, delivery radius
       - Surge pricing, promo codes, subscriptions
       - Commission rates, rating system, cancellation refunds
    """)
    
    print("=" * 70)
    print("✨ Demonstration Complete! ✨")
    print("=" * 70)


if __name__ == "__main__":
    main()
