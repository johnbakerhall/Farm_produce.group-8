from abc import ABC, abstractmethod
from datetime import date


class Customer:
    def __init__(self, customer_id, name, phone):
        self.customer_id = customer_id
        self.name = name
        self.phone = phone
        self.__purchases = []

    def add_purchase(self, sale):
        self.__purchases.append(sale)

    def show_purchases(self):
        if not self.__purchases:
            print("This customer has no purchases.")
            return

        for sale in self.__purchases:
            print(sale.produce.name, "|", sale.quantity, sale.produce.unit,
                  "| $", round(sale.total, 2), "|", sale.sale_date)


class Produce(ABC):
    _category = "produce"

    def __init__(self, produce_id, name, stock, price):
        self.produce_id = produce_id
        self.name = name
        self.__stock = 0
        self.__price = 0
        self.stock = stock
        self.price = price

    @property
    def stock(self):
        return self.__stock

    @stock.setter
    def stock(self, value):
        if value < 0:
            raise ValueError("Stock cannot be negative.")
        self.__stock = value

    @property
    def price(self):
        return self.__price

    @price.setter
    def price(self, value):
        if value <= 0:
            raise ValueError("Price must be greater than zero.")
        self.__price = value

    def add_stock(self, quantity):
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
        self.stock += quantity

    def remove_stock(self, quantity):
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
        if quantity > self.stock:
            raise ValueError("Sale rejected: not enough stock available.")
        self.stock -= quantity

    @abstractmethod
    def calculate_price(self, quantity):
        pass

    @property
    @abstractmethod
    def unit(self):
        pass


class CropProduce(Produce):
    _category = "crop"

    def calculate_price(self, quantity):
        return quantity * self.price

    @property
    def unit(self):
        return "kg"


class DairyProduce(Produce):
    _category = "dairy"

    def calculate_price(self, quantity):
        return quantity * self.price * 1.10

    @property
    def unit(self):
        return "litres"


class PoultryProduce(Produce):
    _category = "poultry"

    def calculate_price(self, quantity):
        return quantity * self.price * 1.05

    @property
    def unit(self):
        return "birds"


class Sale:
    def __init__(self, customer, produce, quantity):
        self.customer = customer
        self.produce = produce
        self.quantity = quantity
        self.total = produce.calculate_price(quantity)
        self.sale_date = date.today().isoformat()