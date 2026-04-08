# 🧩 Abstraction — Vehicle System
# 📝 Problem

# Use abstract class:

# Vehicle with abstract method start()
# Implement in Car, Bike

from abc import ABC, abstractmethod

class Vehicle:
    @abstractmethod
    def start(self):
        pass


class Car(Vehicle):
    def start(self):
        print("Car is starting.")

class Bike(Vehicle):
    def start(self):
        print("Bike is starting.")

ob1 = Car()
ob1.start()