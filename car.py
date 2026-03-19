class Car:
    def __init__(self, make, model, year):
        self.make = make
        self.model = model
        self.year = year
        self.odometer_reading = 0

my_car = Car('Toyota', 'Corolla', 2020)
your_car = Car('Honda', 'Civic', 2019)
your_car.year = 2021

print(my_car.model)
print(your_car.year)
print(my_car.odometer_reading)