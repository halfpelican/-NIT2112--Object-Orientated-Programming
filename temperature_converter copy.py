class TemperatureConverter:
    def __init__(self):
        pass
    
    def converter(self, input_value, input_type, output_type):
        self.__input_value = input_value
        self.__input_type = input_type
        self.__output_type = output_type

        if input_type == "Celsius":
            celsius = input_value
            if output_type == "Fahrenheit":
                return self.__celsius_to_fahrenheit(celsius)
            elif output_type == "Kelvin":
                return self.__celsius_to_kelvin(celsius)
            else: 
                print("Incorrect output type")
        elif input_type == "Fahrenheit":
            fahrenheit = input_value
            if output_type == "Celsius":
                return self.__fahrenheit_to_celsius(fahrenheit)
            elif output_type == "Kelvin":
                return self.__fahrenheit_to_kelvin(fahrenheit)
            else: 
                print("Incorrect output type")     
        elif input_type == "Kelvin":
            if output_type == "Celsius":
                return self.__convert_to_standard(input_value) 
            elif output_type == "Fahrenheit":
                return self.__convert_to_standard(input_value, "Fahrenheit")
            else:
                print("Incorrect output type")     
        else:
            print("Incorrect input type")     



    def __celsius_to_fahrenheit(self, celsius):
        return (celsius * 9/5) + 32
    
    def __fahrenheit_to_celsius(self, fahrenheit):
        return (fahrenheit - 32) * 5/9
    
    def __kelvin_to_celsius(self, kelvin):
        return kelvin - 273.15
    
    def __convert_to_standard(self, kelvin, standard="Celsius"):
        celsius = self.__kelvin_to_celsius(kelvin)
        if standard == "Fahrenheit":
            return self.celsius_to_fahrenheit(celsius)
        return celsius
    
converter = TemperatureConverter()
print(converter.converter(25, "Celsius", "Fahrenheit"))
