from abc import ABC, abstractmethod

class Car:
    def __init__(self, model):
        self.model = model

    @abstractmethod
    def drive(self):
        print(f"{self.model} is driving.")

class Audi(Car):
    def drive(self):
        super().drive()
        

class BMW(Car):
    def drive(self):
        super().drive()

c1 = Audi("Audi A4")
c2 = BMW("BMW X5")

c1.drive()
c2.drive()