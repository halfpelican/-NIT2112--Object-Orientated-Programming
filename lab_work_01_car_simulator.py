class Car:
    def __init__(self, make, model, year):
        self.make = make
        self.model = model
        self.year = year
        self.odometer = 0

    def get_descriptive_name(self):
        return (f"The make of the car is {self.make.title()}, model being {self.model.title()}, built in the year {self.year}")
   
    def read_odometer(self):
        print(f"The current odometer reading is {self.odometer} km")

    def drive(self, km = 5):
        print(f"You drive up the street 5km")
        self.odometer += km

    def __str__(self):
        return f"{self.year} {self.make.title()} {self.model.title()}"
    # prints: 2025 Audi A4

if __name__ == "__main__":
    my_car = Car("audi", "a4", 2025)
    my_car.drive()
    my_car.read_odometer()
    my_car.drive()
    my_car.read_odometer()
    print(my_car.get_descriptive_name())
    print(my_car)