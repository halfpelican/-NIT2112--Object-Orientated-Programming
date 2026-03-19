class Animal:
    def act(self):
        print("General Action")

class Swimming(Animal):
    def act(self):
        print("Swimming")

class Flyer(Animal):
    def act(self):
        print("Flying")

class FlyingFish(Swimming, Flyer):
    pass

fish = FlyingFish()
fish.act()

print(FlyingFish.mro())