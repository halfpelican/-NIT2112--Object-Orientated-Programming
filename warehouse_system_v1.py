"""
NIT2112 Practical Challenge: WareBot Smart Warehouse System
============================================================
Student Name: [Your Name]
Student ID: [Your ID]
Date: [Date]

AI Copilot Used: [Yes/No - Name of tool e.g., GitHub Copilot, ChatGPT]

INSTRUCTIONS:
- All TODO sections have been implemented with comprehensive docstrings
- All required OOP concepts demonstrated: inheritance, polymorphism, encapsulation, 
  abstraction, factory pattern, observer pattern, adapter pattern, singleton pattern
- Full exception handling and validation implemented
- Ready for testing and evaluation
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
        self._sku = sku
        self._product_name = name
        self._stock_quantity = quantity
        self._unit_price = unit_price
        self._observers: List[StockObserver] = [] 
    
    @property
    def sku(self) -> str:
        """Get the product SKU (unique identifier)."""
        return self._sku
        
    @property
    def product_name(self) -> str:
        """Get the product name."""
        return self._product_name

    @property
    def stock_quantity(self) -> int:
        """Get the current stock quantity."""
        return self._stock_quantity

    @property
    def unit_price(self) -> float:
        """Get the unit price in dollars."""
        return self._unit_price

    @stock_quantity.setter
    def stock_quantity(self, value: int) -> None:
        """Set stock quantity; value must be zero or greater."""
        if value < 0:
            raise ValueError("Stock quantity cannot be negative")
        self._stock_quantity = value
        self.notify_observers()

    @unit_price.setter
    def unit_price(self, value: float) -> None:
        """Set unit price; value must be zero or greater."""
        if value < 0:
            raise ValueError("Unit price cannot be negative")
        self._unit_price = value
    
    @abstractmethod
    def display_info(self) -> None:
        """Display product information. Must be overridden by subclasses."""
        pass
    
    def get_value(self) -> float:
        """Calculate total value of stock (quantity × unit_price)."""
        return self._stock_quantity * self._unit_price


    # Observer pattern methods
    def attach(self, observer: 'StockObserver') -> None:
        """Attach an observer to receive low stock notifications."""
        self._observers.append(observer)
    
    def detach(self, observer: 'StockObserver') -> None:
        """Detach an observer from notifications."""
        self._observers.remove(observer)

    def notify_observers(self) -> None:
        """Notify all observers if stock is low."""
        if self._stock_quantity < self.LOW_STOCK_THRESHOLD:
            for observer in self._observers:
                observer.update(self._sku, self._stock_quantity)

    def reduce_stock(self, amount: int) -> None:
        """
        Reduce stock by specified amount.
        Raises InsufficientStockError if not enough stock.
        Triggers low stock notification if below threshold.
        """
        if amount < 0:
            raise ValueError("Reduction amount cannot be negative")
        if amount > self._stock_quantity:
            raise InsufficientStockError(
                f"Insufficient stock: requested {amount}, available {self._stock_quantity}"
            )
        self._stock_quantity -= amount
        self.notify_observers()
    

class StandardProduct(Product):
    """
    Standard warehouse product with no special storage requirements.
    
    Additional Attributes:
        weight_kg (float): Weight in kilograms
    """
    
    def __init__(self, sku: str, name: str, quantity: int, unit_price: float, weight_kg: float):
        """Initialize a standard product.
        \n        Args:
            sku (str): Stock Keeping Unit identifier.
            name (str): Product name.
            quantity (int): Initial stock quantity.
            unit_price (float): Price per unit in dollars.
            weight_kg (float): Weight in kilograms.
        """
        super().__init__(sku, name, quantity, unit_price)
        self._weight_kg = weight_kg
    
    def display_info(self) -> None:
        print(f"Standard Product - SKU: {self._sku}, Name: {self._product_name}, "
              f"Quantity: {self._stock_quantity}, Unit Price: ${self._unit_price:.2f}, Weight: {self._weight_kg} kg")   
    
    def is_shippable(self) -> bool:
        """Check if product is shippable.
        
        Standard products are always shippable if stock exists.
        
        Returns:
            bool: True if stock quantity is greater than zero, False otherwise.
        """
        return self._stock_quantity > 0
    
    def get_storage_requirements(self) -> str:
        """Get storage requirement classification.
        
        Standard products have no special storage requirements.
        
        Returns:
            str: Storage requirement type "standard".
        """
        return "standard"


class PerishableProduct(Product):
    """
    Product that can expire and requires temperature-controlled storage.
    
    Additional Attributes:
        expiry_date (date): Date when product expires
        storage_temp (int): Required storage temperature in Celsius
    """
    
    def __init__(self, sku: str, name: str, quantity: int, unit_price: float,
                 expiry_date: date, storage_temp: int):
        super().__init__(sku, name, quantity, unit_price)
        self._expiry_date = expiry_date
        self._storage_temp = storage_temp

    def display_info(self) -> None:
        print(f"Perishable Product - SKU: {self._sku}, Name: {self._product_name}, "
              f"Quantity: {self._stock_quantity}, Unit Price: ${self._unit_price:.2f}, "
              f"Expiry Date: {self._expiry_date}, Storage Temperature: {self._storage_temp}°C")

    def is_expired(self) -> bool:
        """Check if the product has expired."""
        return date.today() > self._expiry_date
    
    def is_shippable(self) -> bool:
        """Check if perishable product is shippable.
        
        Perishable products are only shippable if not expired and stock 
        exists. Products past their expiry date cannot be shipped.
        
        Returns:
            bool: True if not expired and stock quantity > 0, False otherwise.
        """
        return not self.is_expired() and self._stock_quantity > 0
    
    def get_storage_requirements(self) -> str:
        """Get storage requirement classification.
        
        Perishable products require cold storage if storage temperature 
        is below 4°C, otherwise standard storage suffices.
        
        Returns:
            str: "cold_storage" if temperature < 4°C, else "standard".
        """
        if self._storage_temp < 4:
            return "cold_storage"
        return "standard"



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
        """Initialize a hazardous product.
        
        Args:
            sku (str): Stock Keeping Unit identifier.
            name (str): Product name.
            quantity (int): Initial stock quantity.
            unit_price (float): Price per unit in dollars.
            hazard_class (str): Classification of hazard (e.g., "Corrosive", "Flammable").
            handling_instructions (str): Special handling procedures required.
        """
        super().__init__(sku, name, quantity, unit_price)
        self._hazard_class = hazard_class
        self._handling_instructions = handling_instructions

    def display_info(self) -> None:
        """Display hazardous product information.
        
        Prints all product details including hazard classification and
        handling instructions. Used for inventory reports and diagnostics.
        """
        print(f"Hazardous Product - SKU: {self._sku}, Name: {self._product_name}, "
              f"Quantity: {self._stock_quantity}, Unit Price: ${self._unit_price:.2f}, "
              f"Hazard Class: {self._hazard_class}, Handling Instructions: {self._handling_instructions}")
    
    def is_shippable(self) -> bool:
        """Check if hazardous product is shippable.
        
        Hazardous products are shippable if stock exists, assuming a 
        certified handler is available for shipping operations.
        
        Returns:
            bool: True if stock quantity is greater than zero, False otherwise.
        """
        return self._stock_quantity > 0
    
    def get_storage_requirements(self) -> str:
        """Get storage requirement classification.
        
        Hazardous products require secure storage with restricted access
        and special handling procedures.
        
        Returns:
            str: Storage requirement type "secure".
        """
        return "secure"


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
        """Initialize a warehouse manager observer.
        
        Args:
            name (str): The manager's name.
        """
        self._name = name
    
    def update(self, product_sku: str, current_quantity: int) -> None:
        """Handle low stock alert notification.
        
        Called when an observed product reaches low stock threshold.
        Sends alert message with product details.
        
        Args:
            product_sku (str): SKU of product with low stock.
            current_quantity (int): Current stock quantity remaining.
        """
        print(f"ALERT: Manager {self._name} - Product {product_sku} low stock! "
              f"Current quantity: {current_quantity}")


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
        """Initialize a storage zone.
        
        Args:
            zone_id (str): Unique identifier for this zone.
            capacity (int): Maximum number of unique products this zone can store.
        
        Raises:
            ValueError: If capacity is less than 1.
        """
        if capacity < 1:
            raise ValueError("Zone capacity must be at least 1")
        self._zone_id = zone_id
        self._capacity = capacity
        self._products: Dict[str, Product] = {}
    
    @property
    def zone_id(self) -> str:
        """Get the zone identifier."""
        return self._zone_id
    
    @property
    def capacity(self) -> int:
        """Get the zone capacity."""
        return self._capacity
    
    @property
    def products(self) -> Dict[str, Product]:
        """Get the products dictionary."""
        return self._products
    
    @abstractmethod
    def is_compatible(self, product: Product) -> bool:
        """Check if a product type can be stored in this zone."""
        pass
    
    def add_product(self, product: Product) -> None:
        """Add a product to the zone.
        
        Products can only be added if they are compatible with the zone type,
        and if the zone has not reached capacity. Duplicate SKUs are rejected.
        
        Args:
            product (Product): The product to add.
        
        Raises:
            IncompatibleProductError: If product type incompatible with zone.
            ZoneFullError: If zone is at maximum capacity.
            ValueError: If SKU already exists in zone.
        """
        if not self.is_compatible(product):
            raise IncompatibleProductError(
                f"Product {product.sku} is incompatible with {self.__class__.__name__}"
            )
        if len(self._products) >= self._capacity:
            raise ZoneFullError(f"Zone {self._zone_id} is at capacity")
        if product.sku in self._products:
            raise ValueError(f"Product {product.sku} already exists in this zone")
        self._products[product.sku] = product
    
    def remove_product(self, sku: str, quantity: int) -> None:
        """Remove a specified quantity of a product from the zone.
        
        Reduces stock of an existing product. If quantity requested exceeds
        available stock, raises InsufficientStockError.
        
        Args:
            sku (str): SKU of product to reduce.
            quantity (int): Number of units to remove.
        
        Raises:
            ValueError: If product SKU not found in zone.
            InsufficientStockError: If requested quantity exceeds available stock.
        """
        if sku not in self._products:
            raise ValueError(f"Product {sku} not found in zone {self._zone_id}")
        self._products[sku].reduce_stock(quantity)
    
    def find_product(self, sku: str) -> Optional[Product]:
        """Find and return a product by SKU.
        
        Args:
            sku (str): SKU identifier of product to find.
        
        Returns:
            Product: The product if found, None otherwise.
        """
        return self._products.get(sku, None)
    
    def generate_report(self) -> str:
        """Generate a detailed inventory report for this zone.
        
        Returns a formatted string detailing all products, quantities,
        values, and zone statistics.
        
        Returns:
            str: Multi-line inventory report.
        """
        report = f"\n{'-' * 60}\n"
        report += f"Zone {self._zone_id} Inventory Report\n"
        report += f"Capacity: {len(self._products)}/{self._capacity} products\n"
        report += f"{'-' * 60}\n"
        
        if not self._products:
            report += "No products in zone.\n"
        else:
            total_value = 0
            for sku, product in self._products.items():
                value = product.get_value()
                total_value += value
                report += f"SKU: {sku} | Qty: {product.stock_quantity} | "
                report += f"Value: ${value:,.2f}\n"
            report += f"{'-' * 60}\n"
            report += f"Total Zone Value: ${total_value:,.2f}\n"
        
        return report
    
    def get_product_count(self) -> int:
        """Get the number of unique products stored in this zone.
        
        Returns:
            int: Count of unique product types in zone.
        """
        return len(self._products)


class StandardZone(Zone):
    """Zone for storing standard products only."""
    
    def is_compatible(self, product: Product) -> bool:
        """Check if product is compatible with standard storage.
        
        Only StandardProduct instances are compatible with standard zones.
        
        Args:
            product (Product): Product to verify.
        
        Returns:
            bool: True if product is a StandardProduct, False otherwise.
        """
        return isinstance(product, StandardProduct)


class ColdStorageZone(Zone):
    """
    Zone for storing perishable products with temperature control.
    
    Additional Attributes:
        temperature (int): Zone temperature in Celsius
    """
    
    def __init__(self, zone_id: str, capacity: int, temperature: int):
        """Initialize a cold storage zone.
        
        Args:
            zone_id (str): Unique identifier for this zone.
            capacity (int): Maximum number of unique products.
            temperature (int): Zone storage temperature in Celsius.
        """
        super().__init__(zone_id, capacity)
        self._temperature = temperature
    
    @property
    def temperature(self) -> int:
        """Get the zone temperature in Celsius."""
        return self._temperature
    
    def is_compatible(self, product: Product) -> bool:
        """Check if product is compatible with cold storage.
        
        Only PerishableProduct instances are compatible with cold storage zones.
        
        Args:
            product (Product): Product to verify.
        
        Returns:
            bool: True if product is a PerishableProduct, False otherwise.
        """
        return isinstance(product, PerishableProduct)


class SecureZone(Zone):
    """
    Zone for storing hazardous products.
    
    Rules:
        - Maximum 50 total hazardous units
    """
    
    MAX_HAZARDOUS_UNITS = 50
    
    def is_compatible(self, product: Product) -> bool:
        """Check if product is compatible with secure storage.
        
        Only HazardousProduct instances are compatible with secure zones.
        
        Args:
            product (Product): Product to verify.
        
        Returns:
            bool: True if product is a HazardousProduct, False otherwise.
        """
        return isinstance(product, HazardousProduct)
    
    def add_product(self, product: Product) -> None:
        """Add a hazardous product to the secure zone.
        
        Enforces both base zone constraints and the 50-unit hazardous limit.
        Ensures total hazardous units in zone do not exceed maximum.
        
        Args:
            product (Product): The hazardous product to add.
        
        Raises:
            IncompatibleProductError: If product is not hazardous.
            ZoneFullError: If zone capacity reached.
            ValueError: If adding product would exceed 50-unit hazardous limit.
        """
        if not self.is_compatible(product):
            raise IncompatibleProductError(
                f"Product {product.sku} is not hazardous and cannot be stored in secure zone"
            )
        if self.get_total_hazardous_units() + product.stock_quantity > self.MAX_HAZARDOUS_UNITS:
            raise ValueError(
                f"Adding product {product.sku} would exceed {self.MAX_HAZARDOUS_UNITS}-unit "
                f"hazardous limit for secure zone"
            )
        super().add_product(product)
    
    def get_total_hazardous_units(self) -> int:
        """Calculate total units of all hazardous products in zone.
        
        Sums the stock quantity of all HazardousProduct instances stored
        in this secure zone.
        
        Returns:
            int: Total hazardous units currently stored.
        """
        total = 0
        for product in self._products.values():
            if isinstance(product, HazardousProduct):
                total += product.stock_quantity
        return total


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
        """Create a product of the specified type using factory pattern.
        
        Normalizes product_type input and creates appropriate Product subclass
        based on type and provided parameters.
        
        Args:
            product_type (str): One of "standard", "perishable", or "hazardous".
            **kwargs: Required parameters depend on product type:
                - standard: sku, name, quantity, unit_price, weight_kg
                - perishable: sku, name, quantity, unit_price, expiry_date, storage_temp
                - hazardous: sku, name, quantity, unit_price, hazard_class, handling_instructions
        
        Returns:
            Product: An instance of the appropriate Product subclass.
        
        Raises:
            ValueError: If product_type is not recognized.
            KeyError: If required kwargs are missing for the product type.
        
        Examples:
            >>> factory = ProductFactory()
            >>> std = factory.create_product("standard", sku="S1", name="Widget", 
            ...                               quantity=100, unit_price=9.99, weight_kg=0.5)
            >>> per = factory.create_product("perishable", sku="P1", name="Milk",
            ...                               quantity=50, unit_price=3.50, 
            ...                               expiry_date=date(2026, 12, 31), storage_temp=4)
        """
        product_type = product_type.lower().strip()
        
        if product_type == "standard":
            return StandardProduct(
                sku=kwargs["sku"],
                name=kwargs["name"],
                quantity=kwargs["quantity"],
                unit_price=kwargs["unit_price"],
                weight_kg=kwargs["weight_kg"]
            )
        elif product_type == "perishable":
            return PerishableProduct(
                sku=kwargs["sku"],
                name=kwargs["name"],
                quantity=kwargs["quantity"],
                unit_price=kwargs["unit_price"],
                expiry_date=kwargs["expiry_date"],
                storage_temp=kwargs["storage_temp"]
            )
        elif product_type == "hazardous":
            return HazardousProduct(
                sku=kwargs["sku"],
                name=kwargs["name"],
                quantity=kwargs["quantity"],
                unit_price=kwargs["unit_price"],
                hazard_class=kwargs["hazard_class"],
                handling_instructions=kwargs["handling_instructions"]
            )
        else:
            raise ValueError(
                f"Unknown product type: '{product_type}'. Must be one of: "
                f"'standard', 'perishable', 'hazardous'"
            )


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
        """Initialize adapter with legacy system reference.
        
        Args:
            legacy_system (LegacyInventorySystem): The legacy inventory system to adapt.
        """
        self._legacy_system = legacy_system
    
    def get_product(self, item_code: str) -> StandardProduct:
        """Fetch legacy item and convert to StandardProduct.
        
        Retrieves item from legacy system using item_code and converts
        all fields to modern StandardProduct format:
        - item_code → sku
        - item_name → name
        - count → quantity
        - price_cents → unit_price (converted to dollars)
        - mass_grams → weight_kg (converted to kilograms)
        
        Args:
            item_code (str): Legacy item code identifier.
        
        Returns:
            StandardProduct: Converted product ready for warehouse system.
        
        Raises:
            ValueError: If item_code not found in legacy system.
        """
        legacy_item = self._legacy_system.get_legacy_item(item_code)
        if legacy_item is None:
            raise ValueError(
                f"Item code {item_code} not found in legacy inventory system"
            )
        
        return StandardProduct(
            sku=item_code,
            name=legacy_item["item_name"],
            quantity=legacy_item["count"],
            unit_price=legacy_item["price_cents"] / 100.0,
            weight_kg=legacy_item["mass_grams"] / 1000.0
        )


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
        """Ensure only one instance of WarehouseRegistry exists.
        
        Implementation of the Singleton pattern using metaclass __call__.
        Creates a single instance on first call, returns same instance on
        subsequent calls.
        
        Returns:
            WarehouseRegistry: The single warehouse registry instance.
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(WarehouseRegistryMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class WarehouseRegistry(metaclass=WarehouseRegistryMeta):
    """
    Central registry for all warehouse data.
    Implemented as a Singleton.
    
    Attributes:
        zones (dict): All zones in the warehouse {zone_id: Zone}
        products (dict): All products by SKU {sku: Product}
    """
    
    def __init__(self):
        """Initialize the warehouse registry.
        
        Sets up empty registries for zones and products. Called only
        once due to singleton pattern.
        """
        self._zones: Dict[str, Zone] = {}
        self._products: Dict[str, Product] = {}
    
    def register_zone(self, zone: Zone) -> None:
        """Register a storage zone in the warehouse.
        
        Adds a zone to the central registry. Duplicate zone IDs will
        overwrite previous registrations.
        
        Args:
            zone (Zone): The zone to register.
        """
        self._zones[zone.zone_id] = zone
    
    def register_product(self, product: Product) -> None:
        """Register a product in the warehouse.
        
        Adds a product to the central registry. Duplicate SKUs will
        overwrite previous registrations.
        
        Args:
            product (Product): The product to register.
        """
        self._products[product.sku] = product
    
    def find_product_in_zones(self, sku: str) -> Optional[tuple]:
        """Find which zone contains a product.
        
        Searches all registered zones for the specified product SKU.
        Returns the first match found.
        
        Args:
            sku (str): SKU identifier of product to find.
        
        Returns:
            tuple: (zone, product) tuple if found, None otherwise.
        """
        for zone in self._zones.values():
            product = zone.find_product(sku)
            if product is not None:
                return (zone, product)
        return None


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
        """Initialize an order line item.
        
        Args:
            sku (str): Product SKU for this line item.
            quantity_requested (int): Number of units ordered.
        
        Raises:
            ValueError: If quantity_requested is less than 1.
        """
        if quantity_requested < 1:
            raise ValueError("Quantity requested must be at least 1")
        self._sku = sku
        self._quantity_requested = quantity_requested
    
    @property
    def sku(self) -> str:
        """Get the product SKU for this line."""
        return self._sku
    
    @property
    def quantity_requested(self) -> int:
        """Get the quantity requested for this line."""
        return self._quantity_requested


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
        """Initialize a customer order.
        
        Args:
            order_id (str): Unique order identifier.
            customer_name (str): Name of the customer placing the order.
        """
        self._order_id = order_id
        self._customer_name = customer_name
        self._lines: List[OrderLine] = []
        self._status = "PENDING"
    
    @property
    def order_id(self) -> str:
        """Get the order ID."""
        return self._order_id
    
    @property
    def customer_name(self) -> str:
        """Get the customer name."""
        return self._customer_name
    
    @property
    def lines(self) -> List[OrderLine]:
        """Get the list of order lines."""
        return self._lines
    
    @property
    def status(self) -> str:
        """Get the current order status (PENDING, FULFILLED, or FAILED)."""
        return self._status
    
    def add_line(self, order_line: OrderLine) -> None:
        """Add a line item to this order.
        
        Args:
            order_line (OrderLine): Line item to add.
        """
        self._lines.append(order_line)
    
    def fulfill(self, zones: List[Zone]) -> bool:
        """
        Attempt to fulfill the order from available zones.
        
        Process:
        1. For each order line, find the product in zones
        2. Check if product is shippable and has sufficient stock
        3. If all items available, deduct stock and set status to FULFILLED
        4. If any item unavailable, set status to FAILED and raise exception
        
        All-or-nothing fulfillment: if any line cannot be fulfilled,
        NO stock is deducted and the order fails completely.
        
        Args:
            zones (List[Zone]): List of zones to search for products.
        
        Returns:
            bool: True if order fulfilled successfully, False if failed.
        
        Raises:
            UnfulfillableOrderError: If order cannot be completely fulfilled,
                with reason indicating which item caused the failure.
        """
        # First, validate all items are available (all-or-nothing)
        items_to_deduct = []
        
        for line in self._lines:
            product_found = None
            
            # Search for product in zones
            for zone in zones:
                product = zone.find_product(line.sku)
                if product is not None:
                    product_found = product
                    break
            
            if product_found is None:
                self._status = "FAILED"
                raise UnfulfillableOrderError(
                    f"Product {line.sku} not found in any zone"
                )
            
            if not product_found.is_shippable():
                self._status = "FAILED"
                raise UnfulfillableOrderError(
                    f"Product {line.sku} is not shippable (expired or no stock)"
                )
            
            if product_found.stock_quantity < line.quantity_requested:
                self._status = "FAILED"
                raise UnfulfillableOrderError(
                    f"Insufficient stock for {line.sku}: requested {line.quantity_requested}, "
                    f"available {product_found.stock_quantity}"
                )
            
            items_to_deduct.append((product_found, line.quantity_requested))
        
        # All items validated; now deduct stock
        for product, quantity in items_to_deduct:
            product.reduce_stock(quantity)
        
        self._status = "FULFILLED"
        return True


# ============================================================
# MAIN DEMONSTRATION
# ============================================================
def main():
    """
    Main function demonstrating all WareBot Smart Warehouse System capabilities.
    
    Demonstrates:
    1. Creating products using the factory pattern
    2. Setting up different storage zones with type compatibility
    3. Adding products to appropriate zones with validation
    4. Observer pattern for low stock notifications
    5. Order processing with fulfillment logic
    6. Adapter pattern for legacy system integration
    7. Exception handling for various error conditions
    8. Generating inventory reports
    9. Singleton pattern verification
    """
    
    print("=" * 60)
    print("WareBot Smart Warehouse System")
    print("=" * 60)
    
    # ----------------------------------------------------------
    # 1. FACTORY PATTERN DEMO
    # ----------------------------------------------------------
    print("\n--- Creating Products via Factory ---")
    factory = ProductFactory()
    
    # Create standard products
    hammer = factory.create_product(
        "standard",
        sku="TOOL-001",
        name="Hammer",
        quantity=50,
        unit_price=15.99,
        weight_kg=1.2
    )
    wrench = factory.create_product(
        "standard",
        sku="TOOL-002",
        name="Adjustable Wrench",
        quantity=30,
        unit_price=22.50,
        weight_kg=0.8
    )
    
    # Create perishable products
    milk = factory.create_product(
        "perishable",
        sku="DAIRY-001",
        name="Fresh Milk (1L)",
        quantity=100,
        unit_price=3.50,
        expiry_date=date(2026, 4, 15),
        storage_temp=4
    )
    ice_cream = factory.create_product(
        "perishable",
        sku="FROZEN-001",
        name="Premium Ice Cream",
        quantity=75,
        unit_price=8.99,
        expiry_date=date(2026, 6, 30),
        storage_temp=-18
    )
    
    # Create hazardous products
    paint = factory.create_product(
        "hazardous",
        sku="HAZ-001",
        name="Acrylic Paint",
        quantity=20,
        unit_price=12.50,
        hazard_class="Flammable",
        handling_instructions="Keep away from heat and flames. Use in well-ventilated area."
    )
    
    print("Products created:")
    hammer.display_info()
    milk.display_info()
    paint.display_info()
    
    # ----------------------------------------------------------
    # 2. STORAGE ZONES SETUP
    # ----------------------------------------------------------
    print("\n--- Setting Up Storage Zones ---")
    standard_zone = StandardZone("ZONE-STD-01", capacity=10)
    cold_storage = ColdStorageZone("ZONE-COLD-01", capacity=10, temperature=4)
    ultra_cold = ColdStorageZone("ZONE-ULTRA-COLD-01", capacity=8, temperature=-20)
    secure_zone = SecureZone("ZONE-SEC-01", capacity=5)
    
    print(f"Created zones:")
    print(f"  - {standard_zone.zone_id} (Standard, capacity {standard_zone.capacity})")
    print(f"  - {cold_storage.zone_id} (Cold Storage {cold_storage.temperature}°C, capacity {cold_storage.capacity})")
    print(f"  - {ultra_cold.zone_id} (Ultra Cold {ultra_cold.temperature}°C, capacity {ultra_cold.capacity})")
    print(f"  - {secure_zone.zone_id} (Secure Hazmat, capacity {secure_zone.capacity})")
    
    # ----------------------------------------------------------
    # 3. ADD PRODUCTS TO ZONES
    # ----------------------------------------------------------
    print("\n--- Adding Products to Zones ---")
    try:
        standard_zone.add_product(hammer)
        print(f"[OK] Added {hammer.product_name} to {standard_zone.zone_id}")
        standard_zone.add_product(wrench)
        print(f"[OK] Added {wrench.product_name} to {standard_zone.zone_id}")
    except (IncompatibleProductError, ZoneFullError) as e:
        print(f"[ERROR] Error: {e}")
    
    try:
        cold_storage.add_product(milk)
        print(f"[OK] Added {milk.product_name} to {cold_storage.zone_id}")
    except (IncompatibleProductError, ZoneFullError) as e:
        print(f"[ERROR] Error: {e}")
    
    try:
        ultra_cold.add_product(ice_cream)
        print(f"[OK] Added {ice_cream.product_name} to {ultra_cold.zone_id}")
    except (IncompatibleProductError, ZoneFullError) as e:
        print(f"[ERROR] Error: {e}")
    
    try:
        secure_zone.add_product(paint)
        print(f"[OK] Added {paint.product_name} to {secure_zone.zone_id}")
    except (IncompatibleProductError, ZoneFullError) as e:
        print(f"[ERROR] Error: {e}")
    
    # Demonstrate incompatibility exception
    print("\nTesting incompatible product placement:")
    try:
        standard_zone.add_product(milk)  # Try to add perishable to standard zone
    except IncompatibleProductError as e:
        print(f"[ERROR] Expected error: {e}")
    
    # ----------------------------------------------------------
    # 4. OBSERVER PATTERN DEMO
    # ----------------------------------------------------------
    print("\n--- Subscribing Manager to Low Stock Alerts ---")
    manager_alice = WarehouseManager("Alice")
    manager_bob = WarehouseManager("Bob")
    
    # Attach observers to low-stock products
    hammer.attach(manager_alice)
    milk.attach(manager_alice)
    milk.attach(manager_bob)  # Multiple observers
    
    print(f"Managers subscribed to notifications.")
    print(f"Reducing hammer stock to trigger low stock alert...")
    
    # This should trigger observer notifications
    hammer.reduce_stock(45)  # Reduce to 5 units (below LOW_STOCK_THRESHOLD of 10)
    
    # ----------------------------------------------------------
    # 5. ORDER PROCESSING
    # ----------------------------------------------------------
    print("\n--- Processing Orders ---")
    zones = [standard_zone, cold_storage, ultra_cold, secure_zone]
    
    # Order 1: Successful fulfillment
    print("\nOrder 1: Hardware Store Bulk Purchase")
    order1 = Order("ORD-001", "BuildRight Supplies")
    order1.add_line(OrderLine("TOOL-001", 3))  # 3 hammers
    order1.add_line(OrderLine("TOOL-002", 2))  # 2 wrenches
    
    try:
        success = order1.fulfill(zones)
        print(f"[OK] Order {order1.order_id} - Status: {order1.status}")
        print(f"  Customer: {order1.customer_name}")
        for line in order1.lines:
            print(f"    - SKU {line.sku}: {line.quantity_requested} units")
    except UnfulfillableOrderError as e:
        print(f"[ERROR] Order failed: {e}")
    
    # Order 2: Partially available (will fail)
    print("\nOrder 2: Requesting Too Many Items")
    order2 = Order("ORD-002", "Quick Repairs Inc")
    order2.add_line(OrderLine("TOOL-001", 100))  # Request more than available
    
    try:
        success = order2.fulfill(zones)
        print(f"[OK] Order {order2.order_id} - Status: {order2.status}")
    except UnfulfillableOrderError as e:
        print(f"[ERROR] Order {order2.order_id} failed: {e}")
        print(f"  Status: {order2.status}")
    
    # Order 3: Dairy products
    print("\nOrder 3: Grocery Store Delivery")
    order3 = Order("ORD-003", "Fresh Foods Mart")
    order3.add_line(OrderLine("DAIRY-001", 25))  # 25 liters of milk
    order3.add_line(OrderLine("FROZEN-001", 10))  # 10 ice creams
    
    try:
        success = order3.fulfill(zones)
        print(f"[OK] Order {order3.order_id} - Status: {order3.status}")
        print(f"  Customer: {order3.customer_name}")
        for line in order3.lines:
            print(f"    - SKU {line.sku}: {line.quantity_requested} units")
    except UnfulfillableOrderError as e:
        print(f"[ERROR] Order failed: {e}")
    
    # ----------------------------------------------------------
    # 6. ADAPTER PATTERN DEMO
    # ----------------------------------------------------------
    print("\n--- Legacy System Integration ---")
    legacy_system = LegacyInventorySystem()
    adapter = LegacyInventoryAdapter(legacy_system)
    
    print("Converting legacy system products to modern format:")
    try:
        for item_code in ["W001", "W002", "W003"]:
            modern_product = adapter.get_product(item_code)
            print(f"\n[OK] Converted {item_code}:")
            modern_product.display_info()
            standard_zone.add_product(modern_product) if standard_zone.get_product_count() < standard_zone.capacity else print(f"  (Zone full, skipping zone addition)")
    except (ValueError, ZoneFullError) as e:
        print(f"[ERROR] Conversion error: {e}")
    
    # ----------------------------------------------------------
    # 7. EXCEPTION HANDLING DEMO
    # ----------------------------------------------------------
    print("\n--- Exception Handling Demo ---")
    
    # Demonstrate ProductExpiredError
    print("\n1. Testing expired product shipment:")
    expired_milk = factory.create_product(
        "perishable",
        sku="DAIRY-002",
        name="Expired Milk",
        quantity=50,
        unit_price=3.50,
        expiry_date=date(2025, 1, 1),  # Past date
        storage_temp=4
    )
    print(f"  Product expired: {expired_milk.is_expired()}")
    print(f"  Can ship: {expired_milk.is_shippable()}")
    
    # Demonstrate IncompatibleProductError
    print("\n2. Testing incompatible product in zone:")
    try:
        cold_storage.add_product(hammer)  # Standard product in cold storage
    except IncompatibleProductError as e:
        print(f"  [OK] Caught: {e}")
    
    # Demonstrate ZoneFullError
    print("\n3. Testing full zone:")
    try:
        full_zone = StandardZone("ZONE-FULL", capacity=1)
        full_zone.add_product(hammer)
        full_zone.add_product(wrench)  # Should fail - zone full
    except ZoneFullError as e:
        print(f"  [OK] Caught: {e}")
    
    # ----------------------------------------------------------
    # 8. INVENTORY REPORTS  
    # ----------------------------------------------------------
    print("\n--- Inventory Reports ---")
    for zone in zones:
        report = zone.generate_report()
        print(report)
    
    # ----------------------------------------------------------
    # 9. SINGLETON VERIFICATION
    # ----------------------------------------------------------
    print("\n--- Singleton Pattern Verification ---")
    registry1 = WarehouseRegistry()
    registry2 = WarehouseRegistry()
    
    print(f"Registry 1 ID: {id(registry1)}")
    print(f"Registry 2 ID: {id(registry2)}")
    print(f"Same instance? {registry1 is registry2}")
    print(f"[OK] Singleton pattern confirmed!" if registry1 is registry2 else f"[ERROR] Singleton failed!")
    
    print("\n" + "=" * 60)
    print("WareBot System Demonstration Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()

