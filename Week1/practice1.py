# Encapsulation — Bank Account
# Problem: Create a BankAccount class

# Private balance
# Methods: deposit, withdraw, get_balance
# Prevent negative withdrawal

amount = int(input("Enter the amount: "))

class BankAccount:
    def __init__(self, balance):
        self.balance = balance

    def deposit(self, amount):
        self.amount = amount
        print(f"{self.amount} deposited")

    def withdraw(self, amount):
        self.amount = amount

        if (self.balance - self.amount < 0):
            print("Balance is low.")
        else:
            print(f"Withdrawal of amount {self.balance - self.amount} successful")

    def get_balance(self, amount):
        self.amount = amount
        final_balance = balance - amount
        print(f"Balance: {final_balance}")
    


ob1 = BankAccount(amount)
ob1.deposit(5000)
ob1.withdraw(30000)
ob1.get_balance