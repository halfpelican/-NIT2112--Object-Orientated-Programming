class Car:
    def __init__(self, model, colour):
        self.model = model
        self.colour = colour
        self.__engine_running = False
        self.__fuel_level = 100

    def start_engine(self, car_key):
        if car_key == "car_key_number":
            self.__engine_running = True
            print("Vroom! Engine has started.")
    
    def stop_engine(self):
        self.__engine_running = False
        print("A quite rumble and then vehicle falls silent")

    def drive(self, distance):
        if self.__engine_running == True:
            if self.__fuel_level > 0:
                print(f"Driving for {distance} kms")
                self.__fuel_level -= distance / 14.5
                if self.__fuel_level < 0:
                    self.__fuel_level = 0
                print(f"Fuel Level: {self.__fuel_level:.2f}%")
            else:
                print("Out of fuel! Please refuel the car.")
        else:
            print("Engine is not running. Start the engine")
    
    def refuel(self, amount):
        self.__fuel_level += amount
        if self.__fuel_level > 100:
            self.__fuel_level = 100
        print(f"Refueled. Fuel level: {self.__fuel_level}%")

my_car = Car("Tesla Model 3", "Red")
print(f"My car is a {my_car.colour} {my_car.model}")
my_car.start_engine(car_key="car_key_number")
my_car.drive(50)
my_car.stop_engine()