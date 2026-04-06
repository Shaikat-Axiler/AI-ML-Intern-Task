# Polymorphism + Inheritance — Payment System
# 📝 Problem

# Base class Payment with method pay()
# Derived:

# CreditCard
# PayPal

# Each implements differently

class Payment:

    def pay(self, amount):
        pass

class CreditCard(Payment):
    def pay(self, amount):
        self.amount = amount
        print(f"Payment: {amount}")

class PayPal(Payment):
    def pay(self, amount):
        self.amount = amount
        print(f"Payment: {amount}")

ob1 = CreditCard()
ob1.pay(5000)

ob2 = PayPal()
ob2.pay(3000)