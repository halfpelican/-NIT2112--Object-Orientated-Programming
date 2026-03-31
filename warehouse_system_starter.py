"""
NIT2112 Practical Challenge: WareBot Smart Warehouse System
============================================================
Student Name: [Your Name]
Student ID: [Your ID]
Date: [Date]

AI Copilot Used: [Yes/No - Name of tool e.g., GitHub Copilot, ChatGPT]

INSTRUCTIONS:
- Complete all TODO sections
- Demonstrate all required OOP concepts
- Document your AI interactions as you work
- Test your code before submission
============================================================
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional, Dict


# ============================================================
# CUSTOM EXCEPTIONS
# ============================================================
class WarehouseError(Exception):
    """Base exception for warehouse system errors."""
    pass


class InventoryError(WarehouseError):
    """Base exception for inventory-related errors."""
    pass


class InsufficientStockError(InventoryError):
    """Raised when there isn't enough stock to fulfill a request."""
    pass


class ProductExpiredError(InventoryError):
    """Raised when attempting to ship an expired product."""
    pass


class ZoneError(WarehouseError):
    """Base exception for zone-related errors."""
    pass


class ZoneFullError(ZoneError):
    """Raised when a zone has reached its capacity."""
    pass


class IncompatibleProductError(ZoneError):
    """Raised when a product cannot be stored in a particular zone type."""
    pass


class OrderError(WarehouseError):
    """Base exception for order-related errors."""
    pass


class UnfulfillableOrderError(OrderError):
    """Raised when an order cannot be fulfilled."""
    pass


# ============================================================
# INTERFACES / ABSTRACT BASE CLASSES
# ============================================================
class Storable(ABC):
    """Interface for items that can be stored in warehouse zones."""
    
    @abstractmethod
    def get_storage_requirements(self) -> str:
        """Return the storage requirements for this item."""
        pass


class Shippable(ABC):
    """Interface for items that can be shipped."""
    
    @abstractmethod
    def is_shippable(self) -> bool:
        """Check if the item can be shipped."""
        pass


# ============================================================
# PRODUCT HIERARCHY
# ============================================================
class Product(Storable, Shippable):
    """
    Abstract base class for all warehouse products.
    
    Attributes:
        sku (str): Stock Keeping Unit - unique identifier
        name (str): Product name
        quantity (int): Current stock quantity
        unit_price (float): Price per unit in dollars
    """
    
    LOW_STOCK_THRESHOLD = 10
    
    def __init__(self, sku: str, name: str, quantity: int, unit_price: float):
        # TODO: Implement with proper encapsulation
        # Use private/protected attributes
        # Initialize observer list for low stock alerts
        pass
    
    # TODO: Implement property getters and setters for encapsulated attributes
    # Example:
    # @property
    # def sku(self) -> str:
    #     return self._sku
    
    @abstractmethod
    def display_info(self) -> None:
        """Display product information. Must be overridden by subclasses."""
        pass
    
    def get_value(self) -> float:
        """Calculate total value of stock (quantity × unit_price)."""
        # TODO: Implement
        pass
    
    # Observer pattern methods
    def attach(self, observer: 'StockObserver') -> None:
        """Attach an observer to receive low stock notifications."""
        # TODO: Implement
        pass
    
    def detach(self, observer: 'StockObserver') -> None:
        """Detach an observer from notifications."""
        # TODO: Implement
        pass
    
    def notify_observers(self) -> None:
        """Notify all observers of low stock."""
        # TODO: Implement
        pass
    
    def reduce_stock(self, amount: int) -> None:
        """
        Reduce stock by specified amount.
        Raises InsufficientStockError if not enough stock.
        Triggers low stock notification if below threshold.
        """
        # TODO: Implement with exception handling and observer notification
        pass


class StandardProduct(Product):
    """
    Standard warehouse product with no special storage requirements.
    
    Additional Attributes:
        weight_kg (float): Weight in kilograms
    """
    
    def __init__(self, sku: str, name: str, quantity: int, unit_price: float, weight_kg: float):
        # TODO: Call parent constructor and set additional attributes
        pass
    
    def display_info(self) -> None:
        # TODO: Implement
        pass
    
    def is_shippable(self) -> bool:
        # TODO: Standard products are always shippable if in stock
        pass
    
    def get_storage_requirements(self) -> str:
        # TODO: Return "standard"
        pass


class PerishableProduct(Product):
    """
    Product that can expire and requires temperature-controlled storage.
    
    Additional Attributes:
        expiry_date (date): Date when product expires
        storage_temp (int): Required storage temperature in Celsius
    """
    
    def __init__(self, sku: str, name: str, quantity: int, unit_price: float,
                 expiry_date: date, storage_temp: int):
        # TODO: Implement
        pass
    
    def display_info(self) -> None:
        # TODO: Implement - show expiry date and storage temp
        pass
    
    def is_expired(self) -> bool:
        """Check if the product has expired."""
        # TODO: Compare expiry_date with today's date
        pass
    
    def is_shippable(self) -> bool:
        # TODO: Not shippable if expired or no stock
        pass
    
    def get_storage_requirements(self) -> str:
        # TODO: Return "cold_storage"
        pass


class HazardousProduct(Product):
    """
    Product that requires special handling and secure storage.
    
    Additional Attributes:
        hazard_class (str): Classification of hazard (e.g., "Corrosive", "Flammable")
        handling_instructions (str): Special instructions for handling
    
    Rules:
        - Maximum 50 units per secure zone
        - Requires certified handler for shipping
    """
    
    MAX_UNITS_PER_ZONE = 50
    
    def __init__(self, sku: str, name: str, quantity: int, unit_price: float,
                 hazard_class: str, handling_instructions: str):
        # TODO: Implement
        pass
    
    def display_info(self) -> None:
        # TODO: Implement - show hazard class and handling instructions
        pass
    
    def is_shippable(self) -> bool:
        # TODO: Shippable if in stock (assume handler is certified)
        pass
    
    def get_storage_requirements(self) -> str:
        # TODO: Return "secure"
        pass


# ============================================================
# OBSERVER PATTERN - Low Stock Alerts
# ============================================================
class StockObserver(ABC):
    """Abstract observer for stock level changes."""
    
    @abstractmethod
    def update(self, product_sku: str, current_quantity: int) -> None:
        """Called when observed product stock changes."""
        pass


class WarehouseManager(StockObserver):
    """
    Concrete observer that receives low stock alerts.
    
    Attributes:
        name (str): Manager's name
    """
    
    def __init__(self, name: str):
        # TODO: Implement
        pass
    
    def update(self, product_sku: str, current_quantity: int) -> None:
        # TODO: Print alert message with manager name, SKU, and quantity
        pass


# ============================================================
# STORAGE ZONES
# ============================================================
class Zone(ABC):
    """
    Abstract base class for storage zones.
    
    Attributes:
        zone_id (str): Unique zone identifier
        capacity (int): Maximum number of unique products
        products (dict): Products stored in this zone {sku: Product}
    """
    
    def __init__(self, zone_id: str, capacity: int):
        # TODO: Implement with proper encapsulation
        pass
    
    @abstractmethod
    def is_compatible(self, product: Product) -> bool:
        """Check if a product type can be stored in this zone."""
        pass
    
    def add_product(self, product: Product) -> None:
        """
        Add a product to the zone.
        
        Raises:
            ZoneFullError: If zone is at capacity
            IncompatibleProductError: If product type doesn't match zone
        """
        # TODO: Implement with validation
        pass
    
    def remove_product(self, sku: str, quantity: int) -> None:
        """
        Remove/reduce quantity of a product from the zone.
        
        Raises:
            InsufficientStockError: If not enough stock
        """
        # TODO: Implement
        pass
    
    def find_product(self, sku: str) -> Optional[Product]:
        """Find a product by SKU. Returns None if not found."""
        # TODO: Implement
        pass
    
    def generate_report(self) -> str:
        """Generate inventory report for this zone."""
        # TODO: Implement
        pass
    
    def get_product_count(self) -> int:
        """Return number of unique products in zone."""
        # TODO: Implement
        pass


class StandardZone(Zone):
    """Zone for storing standard products only."""
    
    def is_compatible(self, product: Product) -> bool:
        # TODO: Only accept StandardProduct
        pass


class ColdStorageZone(Zone):
    """
    Zone for storing perishable products with temperature control.
    
    Additional Attributes:
        temperature (int): Zone temperature in Celsius
    """
    
    def __init__(self, zone_id: str, capacity: int, temperature: int):
        # TODO: Implement
        pass
    
    def is_compatible(self, product: Product) -> bool:
        # TODO: Only accept PerishableProduct
        pass


class SecureZone(Zone):
    """
    Zone for storing hazardous products.
    
    Rules:
        - Maximum 50 total hazardous units
    """
    
    MAX_HAZARDOUS_UNITS = 50
    
    def is_compatible(self, product: Product) -> bool:
        # TODO: Only accept HazardousProduct
        pass
    
    def add_product(self, product: Product) -> None:
        """
        Override to enforce 50-unit limit for hazardous products.
        """
        # TODO: Implement with additional validation
        pass
    
    def get_total_hazardous_units(self) -> int:
        """Calculate total units of hazardous products in zone."""
        # TODO: Implement
        pass


# ============================================================
# FACTORY PATTERN
# ============================================================
class ProductFactory:
    """
    Factory for creating different types of products.
    
    Usage:
        factory = ProductFactory()
        product = factory.create_product("standard", sku="SKU001", ...)
    """
    
    def create_product(self, product_type: str, **kwargs) -> Product:
        """
        Create a product of the specified type.
        
        Args:
            product_type: One of "standard", "perishable", "hazardous"
            **kwargs: Product-specific attributes
            
        Returns:
            Product: The created product instance
            
        Raises:
            ValueError: If product_type is unknown
            KeyError: If required kwargs are missing
        """
        # TODO: Implement factory logic
        # Hint: Use product_type.lower() to normalize input
        pass


# ============================================================
# ADAPTER PATTERN
# ============================================================
class LegacyInventorySystem:
    """
    Simulates an old inventory system with different data format.
    DO NOT MODIFY THIS CLASS.
    """
    
    def __init__(self):
        self.old_data = {
            "W001": {"item_name": "Hammer", "count": 75, "price_cents": 1599, "mass_grams": 800},
            "W002": {"item_name": "Screwdriver Set", "count": 40, "price_cents": 2499, "mass_grams": 500},
            "W003": {"item_name": "Wrench", "count": 30, "price_cents": 899, "mass_grams": 350},
        }
    
    def get_legacy_item(self, item_code: str) -> Optional[Dict]:
        """Get item data in legacy format. Returns None if not found."""
        return self.old_data.get(item_code, None)


class LegacyInventoryAdapter:
    """
    Adapter to convert legacy inventory data to Product objects.
    
    Conversions:
        - price_cents → unit_price (divide by 100)
        - mass_grams → weight_kg (divide by 1000)
        - item_name → name
        - count → quantity
        - item_code → sku
    """
    
    def __init__(self, legacy_system: LegacyInventorySystem):
        # TODO: Store reference to legacy system
        pass
    
    def get_product(self, item_code: str) -> StandardProduct:
        """
        Fetch legacy item and convert to StandardProduct.
        
        Raises:
            ValueError: If item_code not found in legacy system
        """
        # TODO: Implement conversion logic
        pass


# ============================================================
# SINGLETON PATTERN - Warehouse Registry
# ============================================================
class WarehouseRegistryMeta(type):
    """
    Metaclass that implements the Singleton pattern.
    Ensures only one instance of WarehouseRegistry exists.
    """
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        # TODO: Implement singleton logic
        # If instance doesn't exist, create it
        # Always return the same instance
        pass


class WarehouseRegistry(metaclass=WarehouseRegistryMeta):
    """
    Central registry for all warehouse data.
    Implemented as a Singleton.
    
    Attributes:
        zones (dict): All zones in the warehouse {zone_id: Zone}
        products (dict): All products by SKU {sku: Product}
    """
    
    def __init__(self):
        # TODO: Implement
        pass
    
    def register_zone(self, zone: Zone) -> None:
        """Register a zone in the warehouse."""
        # TODO: Implement
        pass
    
    def register_product(self, product: Product) -> None:
        """Register a product in the warehouse."""
        # TODO: Implement
        pass
    
    def find_product_in_zones(self, sku: str) -> Optional[tuple]:
        """
        Find which zone contains a product.
        Returns (zone, product) tuple or None.
        """
        # TODO: Implement
        pass


# ============================================================
# ORDER PROCESSING
# ============================================================
class OrderLine:
    """
    Represents a single line item in an order.
    
    Attributes:
        sku (str): Product SKU
        quantity_requested (int): How many units ordered
    """
    
    def __init__(self, sku: str, quantity_requested: int):
        # TODO: Implement
        pass


class Order:
    """
    Represents a customer order.
    
    Attributes:
        order_id (str): Unique order identifier
        customer_name (str): Name of customer
        lines (list): List of OrderLine objects
        status (str): PENDING, FULFILLED, or FAILED
    """
    
    def __init__(self, order_id: str, customer_name: str):
        # TODO: Implement
        pass
    
    def add_line(self, order_line: OrderLine) -> None:
        """Add an order line to this order."""
        # TODO: Implement
        pass
    
    def fulfill(self, zones: List[Zone]) -> bool:
        """
        Attempt to fulfill the order from available zones.
        
        Process:
        1. For each order line, find the product in zones
        2. Check if product is shippable and has sufficient stock
        3. If all items available, deduct stock and set status to FULFILLED
        4. If any item unavailable, set status to FAILED
        
        Args:
            zones: List of zones to search for products
            
        Returns:
            bool: True if order fulfilled, False otherwise
            
        Raises:
            UnfulfillableOrderError: If order cannot be fulfilled (with reason)
        """
        # TODO: Implement order fulfillment logic
        pass


# ============================================================
# MAIN DEMONSTRATION
# ============================================================
def main():
    """
    Main function to demonstrate all system capabilities.
    
    You should demonstrate:
    1. Creating products using the factory
    2. Setting up different storage zones
    3. Adding products to appropriate zones
    4. Setting up warehouse manager observers
    5. Processing sample orders (successful and failed)
    6. Legacy system integration via adapter
    7. Exception handling for various error conditions
    8. Generating inventory reports
    """
    
    print("=" * 60)
    print("WareBot Smart Warehouse System")
    print("=" * 60)
    
    # ----------------------------------------------------------
    # 1. FACTORY PATTERN DEMO
    # ----------------------------------------------------------
    print("\n--- Creating Products via Factory ---")
    # TODO: Create products using ProductFactory
    # Example:
    # factory = ProductFactory()
    # widget = factory.create_product("standard", sku="SKU001", name="Widget", ...)
    
    # ----------------------------------------------------------
    # 2. STORAGE ZONES SETUP
    # ----------------------------------------------------------
    print("\n--- Setting Up Storage Zones ---")
    # TODO: Create StandardZone, ColdStorageZone, SecureZone
    
    # ----------------------------------------------------------
    # 3. ADD PRODUCTS TO ZONES
    # ----------------------------------------------------------
    print("\n--- Adding Products to Zones ---")
    # TODO: Add products to appropriate zones
    # Handle exceptions for incompatible products
    
    # ----------------------------------------------------------
    # 4. OBSERVER PATTERN DEMO
    # ----------------------------------------------------------
    print("\n--- Subscribing Manager to Low Stock Alerts ---")
    # TODO: Create WarehouseManager and attach to products
    
    # ----------------------------------------------------------
    # 5. ORDER PROCESSING
    # ----------------------------------------------------------
    print("\n--- Processing Orders ---")
    # TODO: Create and fulfill orders
    # Show both successful and failed orders
    
    # ----------------------------------------------------------
    # 6. ADAPTER PATTERN DEMO
    # ----------------------------------------------------------
    print("\n--- Legacy System Integration ---")
    # TODO: Use LegacyInventoryAdapter to convert old data
    
    # ----------------------------------------------------------
    # 7. EXCEPTION HANDLING DEMO
    # ----------------------------------------------------------
    print("\n--- Exception Handling Demo ---")
    # TODO: Demonstrate various exceptions:
    # - ProductExpiredError
    # - IncompatibleProductError
    # - InsufficientStockError
    # - ZoneFullError
    
    # ----------------------------------------------------------
    # 8. INVENTORY REPORT
    # ----------------------------------------------------------
    print("\n--- Inventory Reports ---")
    # TODO: Generate and display zone reports
    
    # ----------------------------------------------------------
    # 9. SINGLETON VERIFICATION
    # ----------------------------------------------------------
    print("\n--- Singleton Verification ---")
    # TODO: Show that WarehouseRegistry is a singleton
    # reg1 = WarehouseRegistry()
    # reg2 = WarehouseRegistry()
    # print(f"Same instance? {reg1 is reg2}")  # Should be True


if __name__ == "__main__":
    main()
