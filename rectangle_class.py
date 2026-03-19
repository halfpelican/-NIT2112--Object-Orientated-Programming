class Rectangle:
    def __init__(self, width, height):
        self.__width = width
        self.__height = height

    def get_width(self):
        return self.__width
    
    def set_width(self, width):
        if width > 0:
            self.__width = width
        else:
            print("Width must be greater than 0")

    def get_height(self):
        return self.__height
    
    def set_height(self, height):
        if height > 0:
            self.__height = height
        else:
            print("Height must be greater than 0")
    
    def calculate_area(self):
        return self.__width * self.__height
    
    def display_dimensions(self):
        print(f"The width is {self.__width}cm and the height is {self.__height}cm")


rect = Rectangle(5,10)
print(rect.get_width())
rect.set_width(8)
print(rect.calculate_area())
rect.display_dimensions()    
