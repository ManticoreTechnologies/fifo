import json

class Price:
    
    def __init__(self, price):
        self.price = int(price)
        self.orders = []

    def add_order(self, order):
        self.orders.append(order)

    def side(self):
        if len(self.orders) > 0:
            return self.orders[0].side
        else:
            return None

    def match_order(self, order):
        # This will be a recursive function that will match orders until the order is filled or no more matches are possible
        first_order = self.get_first_order()
        
        if first_order is None:
            print("Price level has no more order to match with")
            return order, order.quantity == 0
        
        if order.quantity == 0:
            print("Order has been filled")
            return order, True

        print("Matching order: ", order.order_id, " with ", first_order.order_id)
        if order.side == "bid":
            print("A bid is buying from an ask")
            if order.quantity >= first_order.quantity:
                print("The bid wants the same or more quantity than the ask has")
                print(order.quantity)
                order.quantity -= first_order.quantity
                print(first_order.quantity)
                # Since the bid has taken all the quantity of the ask, the ask is now filled and should be removed
                self.orders.pop(0)
                return self.match_order(order)
            else:
                print("The bid wants less than the ask has")
                first_order.quantity -= order.quantity
                order.quantity = 0
                print("Order has been partially filled")
                print("Market bid has been filled ")
                return order, True
        else:
            print("An ask is selling to a bid")
            if order.quantity >= first_order.quantity:
                print("The ask wants the same or more quantity than the bid has")
                order.quantity -= first_order.quantity
                self.orders.pop(0)
                return self.match_order(order)
            else:
                print("The ask wants less than the bid has")
                first_order.quantity -= order.quantity
                order.quantity = 0
                print("Order has been partially filled")
                print("Market ask has been filled ")
                return order, True
            
    def get_first_order(self):
        try:
            return self.orders[0]
        except IndexError:
            return None

    def get_total_quantity(self):
        return sum(order.quantity for order in self.orders)
