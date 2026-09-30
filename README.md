FARM PRODUCE INVENTORY AND SALES SYSTEM

The system manages farm produce, customers, stock and sales.

RUNNING THE PROGRAM

Open the terminal in this folder and type:

python farm.py

FILES

models.py contains the main classes.
system.py manages the customers, stock and sales.
main.py contains the menu.
farm.py starts the program.

MAIN CLASSES

Customer stores customer details and purchases.

Produce is the abstract parent class for the produce types.

CropProduce, DairyProduce and PoultryProduce are the produce types.

Sale stores information about one sale.

FarmSystem manages the customers, inventory and sales.

OOP CONCEPTS USED

1. Encapsulation
Stock and price are private in the Produce class. Properties are used to
check the values.

2. Inheritance
CropProduce, DairyProduce and PoultryProduce inherit from Produce.

3. Abstraction
Produce is an abstract class with abstract methods.

4. Polymorphism
Each produce type has its own calculate_price method.

5. Relationships
A Sale connects a Customer to a Produce item. FarmSystem stores customers,
produce and sales.

MENU OPTIONS

1. Register a customer
2. Add produce
3. Receive more stock
4. Record a sale
5. Display inventory
6. Search for produce
7. View customer purchases
8. View a summary
9. Exit

VALIDATION

The program checks for invalid quantities, duplicate IDs, missing records and
sales that are greater than the available stock.

DEMONSTRATION

1. Register a customer.
2. Add some produce.
3. Display the inventory.
4. Record a sale.
5. View the customer purchase history.
6. Try to sell more stock than is available.
7. Display the summary.