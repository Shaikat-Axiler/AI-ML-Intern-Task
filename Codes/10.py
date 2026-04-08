# Write a program that will take user input of cost price and selling price and determines whether its a loss or a profit

cost = float(input("Enter the cost: "))

sell = float(input("Enter the sell price: "))

if sell-cost > 0:
    print(f"The profit is: {sell-cost}")
else:
    print(f"The loss is {cost-sell}")