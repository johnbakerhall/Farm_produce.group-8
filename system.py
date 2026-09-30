from models import Sale


class FarmSystem:
    def __init__(self):
        self.customers = {}
        self.inventory = {}
        self.sales = []

    def register_customer(self, customer):
        if customer.customer_id in self.customers:
            raise ValueError("Customer ID already exists.")
        self.customers[customer.customer_id] = customer

    def add_produce(self, produce):
        if produce.produce_id in self.inventory:
            raise ValueError("Produce ID already exists.")
        self.inventory[produce.produce_id] = produce

    def receive_stock(self, produce_id, quantity):
        produce = self.find_produce(produce_id)
        produce.add_stock(quantity)

    def make_sale(self, customer_id, produce_id, quantity):
        if customer_id not in self.customers:
            raise ValueError("Customer was not found.")
        produce = self.find_produce(produce_id)
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")

        produce.remove_stock(quantity)
        sale = Sale(self.customers[customer_id], produce, quantity)
        self.sales.append(sale)
        self.customers[customer_id].add_purchase(sale)
        return sale

    def find_produce(self, produce_id):
        if produce_id not in self.inventory:
            raise ValueError("Produce was not found.")
        return self.inventory[produce_id]

    def search_produce(self, search_text):
        search_text = search_text.lower()
        results = []
        for produce in self.inventory.values():
            if search_text in produce.name.lower():
                results.append(produce)
        return results

    def display_inventory(self):
        if not self.inventory:
            print("No produce has been added.")
            return
        print("\nINVENTORY")
        for produce in self.inventory.values():
            print(produce.produce_id, ":", produce.name, "(",
                  produce._category, ") | Stock:", produce.stock,
                  produce.unit, "| Base price: $", round(produce.price, 2))

    def display_summary(self):
        total_value = 0
        for sale in self.sales:
            total_value += sale.total
        print("\nSUMMARY")
        print("Customers:", len(self.customers))
        print("Produce items:", len(self.inventory))
        print("Sales made:", len(self.sales))
        print("Total sales value: $", round(total_value, 2))