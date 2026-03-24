from abc import ABC, abstractmethod

class AbstractAnimal(ABC):
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def make_sound(self):
        pass
    def describe(self):
        return f"This animal is named {self.name}."

class Dog(AbstractAnimal):
    def __init__(self, name):
        super().__init__(name)

    def make_sound(self):
        return "Woof!"

my_dog = Dog("Buddy")

print(my_dog.describe())
print(my_dog.make_sound())