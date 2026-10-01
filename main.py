"""
main.py - Menu-driven interface for the Farm Produce Inventory and Sales System.

This file only handles user input and output. The actual data and rules
(customers, produce, stock, sales) live in models.py and system.py.
"""
# Classes for the things we store: customers and the three kinds of produce
from models import Customer, CropProduce, DairyProduce, PoultryProduce
# FarmSystem holds all the data and business logic
from system import FarmSystem 


def read_number(message):
    try:
        return float(input(message))
    except ValueError:
        raise ValueError("Please enter a valid number.")


def add_new_produce(system):
    produce_id = input("Produce ID: ").strip()
    name = input("Produce name: ").strip()
    produce_type = input("Type (crop/dairy/poultry): ").strip().lower()
    stock = read_number("Opening stock: ")
    price = read_number("Base price: $")

    if produce_type == "crop":
        produce = CropProduce(produce_id, name, stock, price)
    elif produce_type == "dairy":
        produce = DairyProduce(produce_id, name, stock, price)
    elif produce_type == "poultry":
        produce = PoultryProduce(produce_id, name, stock, price)
    else:
        raise ValueError("Type must be crop, dairy or poultry.")

    system.add_produce(produce)
    print("Produce added successfully.")


def display_search_results(system):
    search_text = input("Enter produce name to search: ").strip()
    results = system.search_produce(search_text)
    if not results:
        print("No matching produce was found.")
        return
    for produce in results:
        print(produce.name, ":", produce.stock, produce.unit, "available")


def run_menu():
    system = FarmSystem()

    while True:
        print("\nFARM PRODUCE INVENTORY AND SALES SYSTEM")
        print("1. Register customer")
        print("2. Add produce")
        print("3. Receive more stock")
        print("4. Record sale")
        print("5. Display inventory")
        print("6. Search produce")
        print("7. Customer purchase history")
        print("8. Display summary")
        print("9. Exit")
        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                customer = Customer(
                    input("Customer ID: ").strip(),
                    input("Customer name: ").strip(),
                    input("Phone: ").strip(),
                )
                system.register_customer(customer)
                print("Customer registered successfully.")
            elif choice == "2":
                add_new_produce(system)
            elif choice == "3":
                produce_id = input("Produce ID: ").strip()
                quantity = read_number("Quantity received: ")
                system.receive_stock(produce_id, quantity)
                print("Stock updated successfully.")
            elif choice == "4":
                customer_id = input("Customer ID: ").strip()
                produce_id = input("Produce ID: ").strip()
                quantity = read_number("Quantity sold: ")
                sale = system.make_sale(customer_id, produce_id, quantity)
                print("Sale recorded. Total: $", round(sale.total, 2))
            elif choice == "5":
                system.display_inventory()
            elif choice == "6":
                display_search_results(system)
            elif choice == "7":
                customer_id = input("Customer ID: ").strip()
                if customer_id not in system.customers:
                    raise ValueError("Customer was not found.")
                system.customers[customer_id].show_purchases()
            elif choice == "8":
                system.display_summary()
            elif choice == "9":
                print("Thank you for using the system.")
                break
            else:
                print("Invalid option. Please choose from 1 to 9.")
        except ValueError as error:
            print("Error:", error)


if __name__ == "__main__":
    run_menu()
