"""
GROUP 8: Farm Produce Inventory and Sales System

A console program for a farm / agricultural cooperative.

Main ideas used (each is marked in the code with a  >>> tag):
    >>> ABSTRACTION     : Produce is an abstract class with abstract methods
    >>> INHERITANCE     : CropProduce, DairyProduce, PoultryProduce extend Produce
    >>> POLYMORPHISM    : calculate_price() behaves differently in each subclass
    >>> ENCAPSULATION   : private/protected attributes + @property validation
    >>> RELATIONSHIPS   : association, aggregation, composition, dependency
    >>> COLLABORATION   : FarmSystem coordinates objects; the menu has no logic

Currency used: UGX (Uganda Shillings)
"""
import math
from abc import ABC, abstractmethod
from datetime import datetime


def is_valid_positive_number(value):
    """Return True only for finite positive numbers and Reject bools, NaN, inf, and <= 0."""
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value > 0


# CUSTOM ERROR  (gives clear messages for invalid operations)

class InsufficientStockError(Exception):
    """Raised when a customer wants more produce than we have."""
    pass



# 1. PRODUCE CLASSES  (abstraction + inheritance + polymorphism)

class Produce(ABC):
    """
    >>> ABSTRACTION
    Abstract base class. We never create a plain 'Produce';
    we create CropProduce, DairyProduce or PoultryProduce.
    It holds everything the subclasses have in common.
    """

    _next_id = 1  # class attribute: gives every produce item a unique id

    def __init__(self, name, price_per_unit, stock=0):
        # Validate first, so a failed attempt does not waste a produce id.
        if not name or not name.strip():
            raise ValueError("Produce name cannot be empty.")
        if stock < 0:
            raise ValueError("Starting stock cannot be negative.")

        # >>> ENCAPSULATION: protected attributes (single underscore).
        # They are set through the property setters so validation always runs.
        self._price_per_unit = 0
        self._stock = 0
        self.price_per_unit = price_per_unit   # uses the validated setter below

        # public attributes (safe to read/change freely)
        self.produce_id = Produce._next_id
        Produce._next_id += 1
        self.name = name.strip()
        if stock > 0:
            self.increase_stock(stock)

    #  encapsulated price 
    @property
    def price_per_unit(self):
        """Read the price (outside code cannot skip validation)."""
        return self._price_per_unit

    @price_per_unit.setter
    def price_per_unit(self, value):
        """Change the price, but only if it is a positive finite number."""
        if not is_valid_positive_number(value):
            raise ValueError("Price must be a number greater than 0.")
        self._price_per_unit = value

    #  encapsulated stock (read-only property) 
    @property
    def stock(self):
        """Stock can be READ here, but only changed by the methods below."""
        return self._stock

    def increase_stock(self, quantity):
        """Add newly received produce to stock."""
        if not is_valid_positive_number(quantity):
            raise ValueError("Quantity to add must be greater than 0.")
        self._stock += quantity

    def reduce_stock(self, quantity):
        """Remove sold produce from stock. Refuses to go below zero."""
        if not is_valid_positive_number(quantity):
            raise ValueError("Quantity to sell must be greater than 0.")
        if quantity > self._stock:
            raise InsufficientStockError(
                f"Only {self._stock:g} {self.unit} of {self.name} available, "
                f"but {quantity} requested."
            )
        self._stock -= quantity

    #  abstract parts: every subclass MUST implement these 
    @property
    @abstractmethod
    def unit(self):
        """The unit of measurement (kg, litre, piece...)."""

    @property
    @abstractmethod
    def category(self):
        """The category name (Crop, Dairy, Poultry)."""

    @abstractmethod
    def calculate_price(self, quantity):
        """Work out the total selling price for this quantity."""

    @abstractmethod
    def pricing_rule(self):
        """Return a short text explaining how this category is priced."""

    def __str__(self):
        return (f"[{self.produce_id}] {self.name:<12} {self.category:<8} "
                f"Stock: {self._stock:>7g} {self.unit:<6} "
                f"Price: {self._price_per_unit:,.0f} UGX/{self.unit}")


class CropProduce(Produce):
    """>>> INHERITANCE: crops (maize, beans...) are sold by the KILOGRAM."""

    @property
    def unit(self):
        return "kg"

    @property
    def category(self):
        return "Crop"

    # >>> POLYMORPHISM: same method name, crop-specific behaviour
    def calculate_price(self, quantity):
        total = quantity * self._price_per_unit
        if quantity >= 50:              # bulk discount
            total *= 0.90               # 10% off
        return round(total)

    def pricing_rule(self):
        return "Per kg. 10% discount when buying 50 kg or more."


class DairyProduce(Produce):
    """>>> INHERITANCE: dairy (milk, yoghurt...) is sold by the LITRE."""

    COLD_CHAIN_FEE = 500  # flat fee per sale to keep dairy cold

    @property
    def unit(self):
        return "litre"

    @property
    def category(self):
        return "Dairy"

    # >>> POLYMORPHISM: dairy adds a fixed cold-storage fee
    def calculate_price(self, quantity):
        total = quantity * self._price_per_unit + self.COLD_CHAIN_FEE
        return round(total)

    def pricing_rule(self):
        return f"Per litre + flat cold-chain fee of {self.COLD_CHAIN_FEE} UGX per sale."


class PoultryProduce(Produce):
    """>>> INHERITANCE: poultry (chicken, eggs...) is sold by the PIECE."""

    @property
    def unit(self):
        return "piece"

    @property
    def category(self):
        return "Poultry"

    # >>> POLYMORPHISM: poultry needs whole pieces and has a small discount
    def calculate_price(self, quantity):
        if quantity != int(quantity):
            raise ValueError("Poultry must be sold in whole pieces.")
        total = quantity * self._price_per_unit
        if quantity >= 10:              # small discount
            total *= 0.95               # 5% off
        return round(total)

    def pricing_rule(self):
        return "Per piece (whole numbers only). 5% discount for 10 pieces or more."
        
    def increase_stock(self, quantity):
        # Poultry stock must be whole pieces
        if quantity != int(quantity):
            raise ValueError("Poultry stock must be in whole pieces.")
        super().increase_stock(quantity)



# 2. CUSTOMER  (encapsulation with validation)

class Customer:
    """A registered customer. Keeps a private list of their purchases."""

    _next_id = 1

    def __init__(self, name, phone):
        self._name = ""
        self._phone = ""
        self.name = name        # goes through the validated setter
        self.phone = phone      # goes through the validated setter
        self.customer_id = Customer._next_id   # id only given if validation passed
        Customer._next_id += 1

        # >>> ENCAPSULATION: private attribute (double underscore)
        self.__purchases = []   # list of Sale objects

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if value is None or not str(value).strip():
            raise ValueError("Customer name cannot be empty.")
        self._name = str(value).strip()

    @property
    def phone(self):
        return self._phone

     @phone.setter
    def phone(self, value):
        text = value.strip()
        # Remove the plus sign before checking the digits
        digits = text[1:] if text.startswith("+") else text
        if not digits.isdigit() or not (9 <= len(digits) <= 13):
            raise ValueError("Phone must contain 9 to 13 digits (e.g. 0772123456).")
        self._phone = text


    @property
    def purchases(self):
        """Return a COPY so outside code cannot edit the private list."""
        return list(self.__purchases)

    def add_purchase(self, sale):
        """Called by FarmSystem after a successful sale."""
        self.__purchases.append(sale)

    def __str__(self):
        return f"[{self.customer_id}] {self._name} ({self._phone})"



# 3. SALE  (a record of one transaction)

class Sale:
    """
    One sale record.
    >>> ASSOCIATION: a Sale is linked to ONE Customer and ONE Produce item.
    """

    _next_id = 1

    def __init__(self, customer, produce, quantity, total_price):
        self.sale_id = Sale._next_id
        Sale._next_id += 1
        self.customer = customer
        self.produce = produce
        self.quantity = quantity
        self.total_price = total_price
        self.date = datetime.now().strftime("%Y-%m-%d %H:%M")

    def __str__(self):
        return (f"Sale #{self.sale_id} | {self.date} | {self.customer.name} | "
                f"{self.produce.name} x {self.quantity} {self.produce.unit} | "
                f"Total: {self.total_price:,.0f} UGX")



# 4. INVENTORY  (holds all produce)

class Inventory:
    """
    >>> AGGREGATION: Inventory HOLDS Produce objects, but a Produce object
    can exist on its own (it is created outside and passed in).
    """

    def __init__(self):
        self._items = {}   # produce_id -> Produce object

    def add_produce(self, produce):
        self._items[produce.produce_id] = produce

    def get(self, produce_id):
        if produce_id not in self._items:
            raise ValueError(f"No produce found with ID {produce_id}.")
        return self._items[produce_id]

    def receive_stock(self, produce_id, quantity):
        """Increase stock when new produce arrives."""
        self.get(produce_id).increase_stock(quantity)

    def search(self, keyword):
        """Find produce whose name contains the keyword (not case sensitive)."""
        keyword = keyword.lower().strip()
        return [p for p in self._items.values() if keyword in p.name.lower()]

    def all_items(self):
        return list(self._items.values())

    def total_stock_value(self):
        return sum(p.stock * p.price_per_unit for p in self._items.values())



# 5. SALES LEDGER  (holds all sales)

class SalesLedger:
    """
    >>> COMPOSITION: the ledger OWNS its Sale records. Sales are created
    for the ledger and have no purpose outside of it.
    """

    def __init__(self):
        self._sales = []

    def add_sale(self, sale):
        self._sales.append(sale)

    def all_sales(self):
        return list(self._sales)

    def total_revenue(self):
        return sum(s.total_price for s in self._sales)

    def revenue_by_category(self):
        """Returns e.g. {'Crop': 50000, 'Dairy': 12000}"""
        result = {}
        for sale in self._sales:
            cat = sale.produce.category
            result[cat] = result.get(cat, 0) + sale.total_price
        return result



# 6. FARM SYSTEM  (the coordinator: objects collaborate here)

class FarmSystem:
    """
    Brings the objects together. All business logic lives here,
    NOT in the menu.
    >>> COMPOSITION: FarmSystem creates and owns an Inventory and a SalesLedger.
    >>> AGGREGATION: FarmSystem keeps a collection of Customer objects.
    """

    def __init__(self):
        self.inventory = Inventory()
        self.ledger = SalesLedger()
        self._customers = {}   # customer_id -> Customer

    # ---- requirement 1: register customers ----
    def register_customer(self, name, phone):
        customer = Customer(name, phone)
        self._customers[customer.customer_id] = customer
        return customer

    def get_customer(self, customer_id):
        if customer_id not in self._customers:
            raise ValueError(f"No customer found with ID {customer_id}.")
        return self._customers[customer_id]

    def all_customers(self):
        return list(self._customers.values())

    # ---- requirement 2: add produce ----
    def add_produce(self, produce):
        self.inventory.add_produce(produce)
        return produce

    # ---- requirement 3: receive more stock ----
    def receive_stock(self, produce_id, quantity):
        self.inventory.receive_stock(produce_id, quantity)

    # ---- requirements 4, 5, 7, 8: record a sale ----
    def record_sale(self, customer_id, produce_id, quantity):
        """
        Steps:
          1. find customer and produce
          2. check stock (rejects the sale if not enough)
          3. ask the produce object for the price  (polymorphism!)
          4. reduce stock, save the Sale, update customer history
        >>> DEPENDENCY: this method only USES Produce.calculate_price();
            it does not keep the produce permanently.
        """
        customer = self.get_customer(customer_id)
        produce = self.inventory.get(produce_id)

        if not isinstance(quantity, (int, float)) or isinstance(quantity, bool) or not math.isfinite(quantity) or quantity <= 0:
            raise ValueError("Quantity must be greater than 0.")
        if quantity > produce.stock:
            raise InsufficientStockError(
                f"Sale rejected: only {produce.stock:g} {produce.unit} of "
                f"{produce.name} in stock, but {quantity} requested."
            )

        # Polymorphism: we do NOT check the type of produce.
        # Each subclass calculates its own price.
        total = produce.calculate_price(quantity)

        produce.reduce_stock(quantity)
        sale = Sale(customer, produce, quantity, total)
        self.ledger.add_sale(sale)
        customer.add_purchase(sale)
        return sale

    # ---- requirement 6: search ----
    def search_produce(self, keyword):
        return self.inventory.search(keyword)

    # ---- requirement 9: summary ----
    def summary_text(self):
        lines = ["=" * 60, "INVENTORY AND SALES SUMMARY", "=" * 60]
        items = self.inventory.all_items()
        lines.append(f"Produce types in stock : {len(items)}")
        lines.append(f"Registered customers   : {len(self._customers)}")
        lines.append(f"Total sales made       : {len(self.ledger.all_sales())}")
        lines.append(f"Stock value (UGX)      : {self.inventory.total_stock_value():,.0f}")
        lines.append(f"Total revenue (UGX)    : {self.ledger.total_revenue():,.0f}")
        lines.append("Revenue by category:")
        by_cat = self.ledger.revenue_by_category()
        if not by_cat:
            lines.append("   (no sales yet)")
        for cat, amount in by_cat.items():
            lines.append(f"   {cat:<8}: {amount:,.0f} UGX")
        lines.append("Low stock warning (below 10 units):")
        low = [p for p in items if p.stock < 10]
        if not low:
            lines.append("   none")
        for p in low:
            lines.append(f"   {p.name}: {p.stock} {p.unit}")
        lines.append("=" * 60)
        return "\n".join(lines)



# 7. MENU  (only talks to the user, then calls FarmSystem)

class FarmMenu:
    """Console menu. It asks questions and shows answers; nothing more."""

    def __init__(self, system):
        self.system = system

    # ---------- small input helpers ----------
    def ask_number(self, prompt):
        """Keep asking until the user types a valid finite number."""
        while True:
            try:
                value = float(input(prompt))
                if not math.isfinite(value):
                    raise ValueError
                return value
            except ValueError:
                print("  ! Please enter a valid number.")

    def ask_whole_number(self, prompt):
        while True:
            try:
                return int(input(prompt))
            except ValueError:
                print("  ! Please enter a whole number (e.g. 1, 2, 3).")

    @staticmethod
    def tidy(number):
        """Show 5.0 as 5 but keep 2.5 as 2.5."""
        return int(number) if number == int(number) else number

    # ---------- menu screens ----------
    def show_menu(self):
        print("\n" + "=" * 45)
        print("   FARM PRODUCE INVENTORY AND SALES SYSTEM")
        print("=" * 45)
        print(" 1. Register customer")
        print(" 2. Add farm produce to inventory")
        print(" 3. Receive new stock")
        print(" 4. Record a sale")
        print(" 5. Search produce / show current stock")
        print(" 6. Show all stock")
        print(" 7. Show customer purchase history")
        print(" 8. Show inventory and sales summary")
        print(" 9. Guided demo (you enter the data)")
        print(" 0. Exit")

    def register_customer(self):
        name = input("Customer name: ")
        phone = input("Phone number: ")
        customer = self.system.register_customer(name, phone)
        print(f"  Registered: {customer}")

    def add_produce(self):
        print("Category: 1) Crop  2) Dairy  3) Poultry")
        choice = self.ask_whole_number("Choose category: ")
        classes = {1: CropProduce, 2: DairyProduce, 3: PoultryProduce}
        if choice not in classes:
            print("  ! Invalid category.")
            return
        name = input("Produce name: ")
        price = self.ask_number("Price per unit (UGX): ")
        stock = self.ask_number("Starting stock: ")
        # The class chosen decides which subclass object is created.
        produce = classes[choice](name, price, stock)
        self.system.add_produce(produce)
        print(f"  Added: {produce}")
        print(f"  Pricing rule: {produce.pricing_rule()}")

    def receive_stock(self):
        produce_id = self.ask_whole_number("Produce ID: ")
        quantity = self.ask_number("Quantity received: ")
        self.system.receive_stock(produce_id, quantity)
        print(f"  Stock updated: {self.system.inventory.get(produce_id)}")

    def record_sale(self):
        customer_id = self.ask_whole_number("Customer ID: ")
        produce_id = self.ask_whole_number("Produce ID: ")
        quantity = self.ask_number("Quantity to buy: ")
        quantity = self.tidy(quantity)
        sale = self.system.record_sale(customer_id, produce_id, quantity)
        print(f"  SUCCESS -> {sale}")

    def search_produce(self):
        keyword = input("Search for produce: ")
        results = self.system.search_produce(keyword)
        if not results:
            print("  No produce found.")
        for produce in results:
            print("  " + str(produce))

    def show_all_stock(self):
        items = self.system.inventory.all_items()
        if not items:
            print("  Inventory is empty.")
        for produce in items:
            print("  " + str(produce))

    def show_history(self):
        customer_id = self.ask_whole_number("Customer ID: ")
        customer = self.system.get_customer(customer_id)
        print(f"  Purchase history for {customer}:")
        if not customer.purchases:
            print("   (no purchases yet)")
        for sale in customer.purchases:
            print("   " + str(sale))

    # ---------- guided demo: EVERY value is typed by the user ----------
    def retry_until_valid(self, step):
        """
        Runs step() again and again until it works.
        Every failure prints a REJECTED message, which shows validation live.
        """
        while True:
            try:
                return step()
            except (ValueError, KeyError, InsufficientStockError) as error:
                print(f"  REJECTED: {error}  -> please try again.")

    def demo_heading(self, text):
        print("\n" + "-" * 60)
        print(text)
        print("-" * 60)

    def demo_add_produce(self, produce_class, label):
        """Ask for one produce item of the given category and add it."""
        def step():
            name = input(f"  {label} name: ")
            price = self.ask_number("  Price per unit (UGX): ")
            stock = self.ask_number("  Starting stock: ")
            produce = produce_class(name, price, stock)   # validation happens here
            self.system.add_produce(produce)
            return produce
        produce = self.retry_until_valid(step)
        print(f"  Added: {produce}")
        print(f"  Pricing rule: {produce.pricing_rule()}")
        return produce

    def run_demo(self):
        """Guided demo. The program explains each step and the user types the data."""
        print("\nGUIDED DEMO - type your own data at each step.")

        # Step 1: register a customer (try a bad phone number to see validation)
        self.demo_heading("STEP 1: Register a customer")
        customer = self.retry_until_valid(lambda: self.system.register_customer(
            input("  Customer name: "), input("  Phone number: ")))
        print(f"  Registered: {customer}")

        # Step 2: one produce item from each subclass
        self.demo_heading("STEP 2: Add one produce item from each category")
        print("  Crop (sold per kg)")
        crop = self.demo_add_produce(CropProduce, "Crop")
        print("  Dairy (sold per litre)")
        dairy = self.demo_add_produce(DairyProduce, "Dairy")
        print("  Poultry (sold per piece)")
        poultry = self.demo_add_produce(PoultryProduce, "Poultry")
        items = [crop, dairy, poultry]

        # Step 3: polymorphism
        self.demo_heading("STEP 3: Polymorphism - same method, different prices")
        quantity = self.ask_number("  Enter a quantity to compare (e.g. 20, try 60 too): ")
        for item in items:
            try:
                price = item.calculate_price(quantity)
                print(f"  {item.category:<8} {item.name:<10} calculate_price({self.tidy(quantity)}) = {price:,} UGX")
            except ValueError as error:
                print(f"  {item.category:<8} {item.name:<10} -> {error}")

        # Step 4: a valid sale
        self.demo_heading("STEP 4: Record a sale")
        for item in items:
            print("  " + str(item))

        def sale_step():
            produce_id = self.ask_whole_number("  Produce ID to buy: ")
            qty = self.tidy(self.ask_number("  Quantity: "))
            return self.system.record_sale(customer.customer_id, produce_id, qty)
        sale = self.retry_until_valid(sale_step)
        print(f"  SUCCESS -> {sale}")

        # Step 5: rejected sale (more than the stock)
        self.demo_heading("STEP 5: Try to buy MORE than the available stock")
        for item in items:
            print("  " + str(item))
        print("  Enter a quantity bigger than the stock shown above.")
        while True:
            try:
                produce_id = self.ask_whole_number("  Produce ID: ")
                qty = self.tidy(self.ask_number("  Quantity: "))
                sale = self.system.record_sale(customer.customer_id, produce_id, qty)
                print(f"  That was within stock, so it was accepted: {sale}")
                print("  Try again with a bigger quantity.")
            except InsufficientStockError as error:
                print(f"  REJECTED: {error}")
                break
            except (ValueError, KeyError) as error:
                print(f"  REJECTED: {error}  -> please try again.")

        # Step 6: rejected price (encapsulation)
        self.demo_heading("STEP 6: Try to set an INVALID price (encapsulation)")
        print("  Enter 0 or a negative number as the new price.")
        while True:
            try:
                produce = self.system.inventory.get(self.ask_whole_number("  Produce ID: "))
                produce.price_per_unit = self.ask_number("  New price per unit: ")
                print(f"  That price was valid and accepted: {produce}")
                print("  Try again with 0 or a negative number.")
            except (ValueError, KeyError) as error:
                print(f"  REJECTED: {error}")
                break

        # Step 7: receive new stock
        self.demo_heading("STEP 7: Receive new stock")

        def stock_step():
            produce_id = self.ask_whole_number("  Produce ID: ")
            qty = self.ask_number("  Quantity received: ")
            self.system.receive_stock(produce_id, qty)
            return self.system.inventory.get(produce_id)
        print(f"  Stock updated: {self.retry_until_valid(stock_step)}")

        # Step 8: history and summary
        self.demo_heading("STEP 8: Customer history and summary")
        print(f"  Purchases by {customer.name}:")
        for past_sale in customer.purchases:
            print("   " + str(past_sale))
        print(self.system.summary_text())
        print("Demo finished. You can keep using the menu.")

    # ---------- main loop ----------
    def run(self):
        # Map each menu number to the method that handles it.
        actions = {
            "1": self.register_customer,
            "2": self.add_produce,
            "3": self.receive_stock,
            "4": self.record_sale,
            "5": self.search_produce,
            "6": self.show_all_stock,
            "7": self.show_history,
            "8": lambda: print(self.system.summary_text()),
            "9": self.run_demo,
        }
        while True:
            self.show_menu()
            choice = input("Choose an option: ").strip()
            if choice == "0":
                print("Goodbye!")
                break
            action = actions.get(choice)
            if action is None:
                print("  ! Invalid option, try again.")
                continue
            # One place to catch every validation/stock error with a clear message.
            try:
                action()
            except (ValueError, KeyError, InsufficientStockError) as error:
                print(f"  ! Operation failed: {error}")



# PROGRAM START

if __name__ == "__main__":
    FarmMenu(FarmSystem()).run()
