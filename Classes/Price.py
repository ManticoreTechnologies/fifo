import json

class Price:
    
    def __init__(self, price):
        self.price = int(price)
        self.orders = []

    def add_order(self, order):
        # Add an order to the list of orders at this price level
        self.orders.append(order)

    def side(self):
        # Return the side (bid/ask) of the first order in the list, or None if there are no orders
        return self.orders[0].side if self.orders else None

    def match_order(self, order):
        # Get the first order in the list to match with
        first_order = self.get_first_order()
        
        if first_order is None:
            # If there are no orders to match with, return the order and indicate it is not filled
            print("Price level has no more order to match with")
            return order, order.quantity == 0
        
        if order.quantity == 0:
            # If the order quantity is zero, it has been filled
            print("Order has been filled")
            return order, True

        print(f"Matching order: {order.order_id} with {first_order.order_id}")
        if order.side == "bid":
            # Process the bid order
            return self._process_bid(order, first_order)
        else:
            # Process the ask order
            return self._process_ask(order, first_order)

    def _process_bid(self, order, first_order):
        print("A bid is buying from an ask")
        if order.quantity >= first_order.quantity:
            # If the bid quantity is greater than or equal to the ask quantity, reduce the bid quantity
            print("The bid wants the same or more quantity than the ask has")
            order.quantity -= first_order.quantity
            self.orders.pop(0)  # Remove the first order as it has been fully matched
            return self.match_order(order)  # Recursively match the remaining quantity
        else:
            # If the bid quantity is less than the ask quantity, reduce the ask quantity
            print("The bid wants less than the ask has")
            first_order.quantity -= order.quantity
            order.quantity = 0  # The bid order is fully matched
            print("Order has been partially filled")
            return order, True

    def _process_ask(self, order, first_order):
        print("An ask is selling to a bid")
        if order.quantity >= first_order.quantity:
            # If the ask quantity is greater than or equal to the bid quantity, reduce the ask quantity
            print("The ask wants the same or more quantity than the bid has")
            order.quantity -= first_order.quantity
            self.orders.pop(0)  # Remove the first order as it has been fully matched
            return self.match_order(order)  # Recursively match the remaining quantity
        else:
            # If the ask quantity is less than the bid quantity, reduce the bid quantity
            print("The ask wants less than the bid has")
            first_order.quantity -= order.quantity
            order.quantity = 0  # The ask order is fully matched
            print("Order has been partially filled")
            return order, True

    def get_first_order(self):
        # Return the first order in the list, or None if there are no orders
        return self.orders[0] if self.orders else None

    def get_total_quantity(self):
        # Return the total quantity of all orders at this price level
        return sum(order.quantity for order in self.orders)
