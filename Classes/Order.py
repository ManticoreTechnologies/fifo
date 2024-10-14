from datetime import datetime
import uuid

class Order:
    def __init__(self, user_address, symbol, side, price, quantity, order_id=None):
        self.order_id = order_id if order_id else str(uuid.uuid4())
        self.user_address = user_address
        self.symbol = symbol
        self.side = side
        self.price = int(price)
        self.quantity = quantity
        self.created_at = datetime.now().isoformat()
    
    
    def to_dict(self):
        return {
            "order_id": self.order_id,
            "user_address": self.user_address,
            "symbol": self.symbol,
            "side": self.side,
            "price": self.price,
            "quantity": self.quantity,
            "created_at": self.created_at
        }
    
    def from_dict(self, order_dict):
        self.order_id = order_dict["order_id"]
        self.user_address = order_dict["user_address"]
        self.symbol = order_dict["symbol"]
        self.side = order_dict["side"]
        self.price = order_dict["price"]
        self.quantity = order_dict["quantity"]
        self.created_at = order_dict["created_at"]
        return self
    
    def can_match(self, order):
        return self.side != order.side and self.price == order.price and self.symbol == order.symbol
    
    def get_price(self):
        return int(self.price)
    
    def __str__(self):
        return f"Order(order_id={self.order_id}, user_address={self.user_address}, symbol={self.symbol}, side={self.side}, price={self.price}, quantity={self.quantity}, created_at={self.created_at})"

    def __repr__(self):
        return str(self.quantity)
    
    def __eq__(self, other):
        return self.price == other.price

    def __ne__(self, other):
        return self.price != other.price

    def __hash__(self):
        return hash(self.price)
    
    def __lt__(self, other):
        return self.price < other.price

    def __le__(self, other):
        return self.price <= other.price

    def __gt__(self, other):
        return self.price > other.price

    def __ge__(self, other):
        return self.price >= other.price
        