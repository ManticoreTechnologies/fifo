import json
from Price import Price
from Order import Order
from Database import Database

class Market:

    def __init__(self, symbol):
        self.symbol = symbol
        self.prices = {}
        self.filled_orders = []  # New list to store filled orders
        self.db = Database()  # Initialize the database connection

    def add_price(self, price):
        self.prices[price] = Price(price)
        self.prices = dict(sorted(self.prices.items()))

    def add_order(self, order):
        price = order.price
        if price not in self.prices:
            self.add_price(price)
        
        if self.prices[price].side() is None:
            self._handle_new_price_level(order, price)
        elif order.side != self.prices[price].side():
            self._handle_opposite_side_order(order, price)
        else:
            self.prices[price].add_order(order)

        # Save the order to the database
        self.db.save_order(order)
        # Update the price level in the database
        self.db.save_price(price, self.symbol, self.prices[price].get_total_quantity())

    def _handle_new_price_level(self, order, price):
        if order.side == "bid":
            self._process_bid_order(order, price)
        elif order.side == "ask":
            self._process_ask_order(order, price)

    def _process_bid_order(self, order, price):
        print("Adding bid to price: ", price)
        lowest_ask = self.get_lowest_ask()
        if lowest_ask and order.price >= lowest_ask.price:
            self._attempt_match(order)
        else:
            self.prices[price].add_order(order)

    def _process_ask_order(self, order, price):
        print("Adding ask to price: ", price)
        highest_bid = self.get_highest_bid()
        if highest_bid and order.price <= highest_bid.price:
            self._attempt_match(order)
        else:
            self.prices[price].add_order(order)

    def _handle_opposite_side_order(self, order, price):
        print(f"A {order.side} was placed into a {self.prices[price].side()} territory")
        self._attempt_match(order)

    def _attempt_match(self, order):
        order, filled = self.match_order(order)
        if filled:
            print("Order filled: ", filled)
            return order, True
        else:
            print("Order not filled: ", filled)
            self.add_order(order)

    def match_order(self, order):
        print("Matching order: ", order.order_id)
        if order.side == "bid":
            return self._match_bid(order)
        elif order.side == "ask":
            return self._match_ask(order)

    def _match_bid(self, order):
        print("Order is a bid")
        lowest_ask = self.get_lowest_ask()
        if not lowest_ask or lowest_ask.price > order.price:
            print("No asks to match with")
            return order, False
        return self._execute_match(order, lowest_ask)

    def _match_ask(self, order):
        print("Order is an ask")
        highest_bid = self.get_highest_bid()
        if not highest_bid or highest_bid.price < order.price:
            print("No bids to match with")
            return order, False
        return self._execute_match(order, highest_bid)

    def _execute_match(self, order, opposite_order):
        order, filled = opposite_order.match_order(order)
        if filled:
            self.filled_orders.append(order)  # Save filled order
        print("Order after matching: ", order.order_id)
        if opposite_order.get_total_quantity() == 0:
            self.prices.pop(opposite_order.price)
        return order, filled

    def get_highest_bid(self):
        for price in reversed(self.prices):
            if self.prices[price].side() == "bid":
                return self.prices[price]
        return None

    def get_lowest_ask(self):
        for price in self.prices:
            if self.prices[price].side() == "ask":
                return self.prices[price]
        return None

    def get_bids(self):
        return [self.prices[price] for price in self.prices if self.prices[price].side() == "bid"]

    def get_asks(self):
        return [self.prices[price] for price in self.prices if self.prices[price].side() == "ask"]

    def get_order_book(self):
        return {price.price: price.get_total_quantity() for price in self.prices.values()}

    def pretty_print_order_book(self):
        order_book = self.get_order_book()
        print("Order Book:")
        for price in sorted(order_book.keys(), reverse=True):
            side = self.prices[price].side()
            color = "\033[42;37m" if side == "bid" else "\033[41;37m"
            print(f"{color}{str(price).center(10)} {str(order_book[price]).center(10)}\033[0m")

    def _handle_market_order(self, order):
        if order.side == "bid":
            self._match_bid(order)
        elif order.side == "ask":
            self._match_ask(order)

    def load_orders(self):
        # Load orders from the database and add them to the market
        orders = self.db.load_orders(self.symbol)
        for order in orders:
            self.add_order(order)

    def __del__(self):
        # Ensure the database connection is closed when the Market object is deleted
        self.db.close()
