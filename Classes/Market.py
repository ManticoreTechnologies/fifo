import json
from Price import Price
from Order import Order

class Market:

    def __init__(self, symbol):
        self.symbol = symbol
        self.prices = {}

    def add_price(self, price):
        self.prices[price] = Price(price)
        # Sort the prices
        self.prices = dict(sorted(self.prices.items()))

    # Add an order to the market, this will match the order with the order book and add it to the correct price level
    def add_order(self, order):

        # Get the price of the order
        price = order.price

        # If the price is not in the order book, add it
        if price not in self.prices:
            self.add_price(price)
        
        # If the price is not on the same side as the order, match the order
        if self.prices[price].side() is None:

            # If the order is a bid
            if order.side == "bid":

                #### Matchin a bid #####
                print("Adding bid to price: ", price)
                lowest_ask = self.get_lowest_ask() # Get the lowest ask
                if lowest_ask is not None and order.price >= lowest_ask.price:
                    order, filled = self.match_order(order)
                    if filled:
                        print("Order filled: ", filled)
                        return order, True
                    else:
                        print("Order not filled: ", filled)
                        self.add_order(order)
                else:
                    self.prices[price].add_order(order)
                ### End of matching a bid ###

                    
            elif order.side == "ask":

                #### Matching an ask ####
                print("Adding ask to price: ", price)
                highest_bid = self.get_highest_bid()
                if highest_bid is not None and order.price <= highest_bid.price:
                    order, filled = self.match_order(order)
                    if filled:
                        print("Order filled: ", filled)
                        return order, True
                    else:
                        print("Order not filled: ", filled)
                        self.add_order(order)
                else:
                    self.prices[price].add_order(order)
                ### End of matching an ask ###

        elif order.side != self.prices[price].side():
            print(f"A {order.side} was placed into a {self.prices[price].side()} territory")
            order, filled = self.match_order(order)
            if filled:
                print("Order filled: ", filled)
                return order, True
            else:
                print("Order not filled: ", filled)
                self.add_order(order)
        elif self.prices[price].side() == order.side:
            # Order is on same side, add to price level; FIFO style
            self.prices[price].add_order(order)

    def match_order(self, order):
        print("Matching order: ", order.order_id)
        print("Order side: ", order.side)
        if order.side == "bid":
            print("Order is a bid")
            lowest_ask = self.get_lowest_ask()
            if lowest_ask is None:
                print("No asks to match with bitch")
                return order, False
            if lowest_ask.price > order.price:
                print("No asks to match with bitch")
                return order, False
            order, filled = lowest_ask.match_order(order)
            print("Order after matching: ", order.order_id)
            if lowest_ask.get_total_quantity() == 0:
                self.prices.pop(lowest_ask.price)
            if filled:
                print("Order filled: ", filled)
                return order, True
            else:
                print("Order not filled: ", filled)
                return self.match_order(order)
            
        elif order.side == "ask":
            print("Order is an ask")
            highest_bid = self.get_highest_bid()
            if highest_bid is None:
                print("No bids to match with bitch")
                return order, False
            if highest_bid.price < order.price:
                print("No bids to match with bitch")
                return order, False
            order, filled = highest_bid.match_order(order)
            print("Order after matching: ", order.order_id)
            if highest_bid.get_total_quantity() == 0:
                self.prices.pop(highest_bid.price)
            if filled:
                print("Order filled: ", filled)
                return order, True
            else:
                print("Order not filled: ", filled)
                return self.match_order(order)

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
        bids = []
        for price in self.prices:
            if self.prices[price].side() == "bid":
                bids.append(self.prices[price])
        return reversed(bids)

    def get_asks(self):
        asks = []
        for price in self.prices:
            if self.prices[price].side() == "ask":
                asks.append(self.prices[price])
        return asks

    def get_order_book(self):
        return {price.price: price.get_total_quantity() for price in self.prices.values()}

    def pretty_print_order_book(self):
        order_book = self.get_order_book()
        print("Order Book:")
        for price in sorted(order_book.keys(), reverse=True):
            side = self.prices[price].side()
            if side == "bid":
                print(f"\033[42;37m{str(price).center(10)} {str(order_book[price]).center(10)}\033[0m")
            else:
                print(f"\033[41;37m{str(price).center(10)} {str(order_book[price]).center(10)}\033[0m")
