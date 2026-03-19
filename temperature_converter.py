class TemperatureConverter:
    def __init__(self):
        pass

    def celsius_to_fahrenheit(self, celsius):
        return (celsius * 9/5) + 32
    
    def fahrenheit_to_celsius(self, fahrenheit):
        return (fahrenheit - 32) * 5/9
    
    def __kelvin_to_celsius(self, kelvin):
        return kelvin - 273.15
    
    def convert_to_standard(self, kelvin, standard="Celsius"):
        celsius = self.__kelvin_to_celsius(kelvin)
        if standard == "Fahrenheit":
            return self.celsius_to_fahrenheit(celsius)
        return celsius
    
converter = TemperatureConverter()
print(converter.celsius_to_fahrenheit(25))
print(converter.fahrenheit_to_celsius(77))
print(converter.convert_to_standard(10))