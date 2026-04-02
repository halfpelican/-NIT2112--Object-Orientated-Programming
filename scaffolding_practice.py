"""Practice scaffold for a simple Car class used in OOP exercises."""


class Car:
	"""Represents a car with basic identity details and speed behaviour.

	Attributes:
		make: Manufacturer name (for example, Toyota).
		model: Specific model name (for example, Corolla).
		year: Production year of the car.
		current_speed: Current speed value, defaulting to 0.0.
	"""

	def __init__(self, make: str, model: str, year: int, current_speed: float = 0.0) -> None:
		"""Initialise a Car object with identity details and starting speed."""

		self.make = make
		self.model = model
		self.year = year
		self.current_speed = current_speed

	def accelerate(self, amount: float) -> None:
		"""Increase the car's speed by the given amount, but not exceeding a maximum speed of 150.

		Args:
			amount: Non-negative value to add to current speed.

		Raises:
			TypeError: If amount is not a number.
			ValueError: If amount is negative.
		"""

		if isinstance(amount, bool) or not isinstance(amount, (int, float)):
			raise TypeError("Acceleration amount must be a number")
		if amount < 0:
			raise ValueError("Acceleration amount must be non-negative")
		self.current_speed = min(150.0, self.current_speed + amount)

	def brake(self, amount: float) -> None:
		"""Decrease the car's speed by amount without going below zero.

		Args:
			amount: Non-negative value to subtract from current speed.

		Raises:
			TypeError: If amount is not a number.
			ValueError: If amount is negative.
		"""

		if isinstance(amount, bool) or not isinstance(amount, (int, float)):
			raise TypeError("Brake amount must be a number")
		if amount < 0:
			raise ValueError("Brake amount must be non-negative")
		self.current_speed = max(0.0, self.current_speed - amount)

	def get_speed(self) -> float:
		"""Return the car's current speed."""

		return self.current_speed
