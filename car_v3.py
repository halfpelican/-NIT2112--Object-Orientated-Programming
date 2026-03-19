class Vehicle:
    def __init__(self, make, model, year):
        self.make = make
        self.model = model
        self.year = year

    def display_info(self):
        print(f"Vehicle Info: {self.year} {self.make} {self.model}")

class Car(Vehicle):
    def __init__(self, make, model, year, doors):
        super().__init__(make, model, year)
        self.doors = doors

    def display_info(self):
        super().display_info()
        print(f"Car with {self.doors} doors")

class Motorcycle(Vehicle):
    def __init__(self, make, model, year, wheels):
        super().__init__(make, model, year)
        self.wheels = wheels

    def display_info(self):
        super().display_info()
        print(f"An impressive vehicle from {self.make} with {self.wheels} wheels")

my_car = Car("Tesla", "Model 3", 2024, 4)
my_car.display_info()
my_motorcycle = Motorcycle("Yamaha", "MT-03", 2013, "Scorpio Rubber")
my_motorcycle.display_info()

