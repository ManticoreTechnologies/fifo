from datetime import datetime
import uuid

class Order:
    def __init__(self, user_address, symbol, side, price, quantity, order_id=None, order_type="limit", quantity_filled=0, created_at=None, status="open"):
        # Generate a unique order ID if not provided
        self.order_id = order_id if order_id else str(uuid.uuid4())
        self.user_address = user_address
        self.symbol = symbol
        self.side = side
        self.price = int(price)
        self.quantity = quantity
        self.quantity_filled = quantity_filled  # New field to track filled quantity
        self.created_at = created_at if created_at else datetime.now().isoformat()
        self.status = status  # New field to track order status
        self.order_type = order_type  # New field to track order type
    
    def to_dict(self):
        # Convert the order object to a dictionary
        return {
            "order_id": self.order_id,
            "user_address": self.user_address,
            "symbol": self.symbol,
            "side": self.side,
            "price": self.price,
            "quantity": self.quantity,
            "quantity_filled": self.quantity_filled,  # Include new field
            "created_at": self.created_at,
            "status": self.status,  # Include status field
            "order_type": self.order_type  # Include order type
        }
    
    def from_dict(self, order_dict):
        # Populate the order object from a dictionary
        self.order_id = order_dict["order_id"]
        self.user_address = order_dict["user_address"]
        self.symbol = order_dict["symbol"]
        self.side = order_dict["side"]
        self.price = order_dict["price"]
        self.quantity = order_dict["quantity"]
        self.quantity_filled = order_dict.get("quantity_filled", 0)  # Handle new field
        self.created_at = order_dict.get("created_at", datetime.now().isoformat())
        self.status = order_dict.get("status", "open")  # Handle status field
        self.order_type = order_dict.get("order_type", "limit")  # Handle order type
        return self
    
    def can_match(self, order):
        # Check if two orders can be matched
        return self.side != order.side and self.price == order.price and self.symbol == order.symbol
    
    def get_price(self):
        # Return the price as an integer
        return int(self.price)
    
    def __str__(self):
        # String representation of the order
        return (f"Order(order_id={self.order_id}, user_address={self.user_address}, "
                f"symbol={self.symbol}, side={self.side}, price={self.price}, "
                f"quantity={self.quantity}, quantity_filled={self.quantity_filled}, "
                f"created_at={self.created_at}, status={self.status})")

    def __repr__(self):
        # Representation of the order for debugging
        return str(self.quantity)
    
    def __eq__(self, other):
        # Equality based on price
        return self.price == other.price

    def __ne__(self, other):
        # Inequality based on price
        return self.price != other.price

    def __hash__(self):
        # Hash based on price
        return hash(self.price)
    
    def __lt__(self, other):
        # Less than comparison based on price
        return self.price < other.price

    def __le__(self, other):
        # Less than or equal comparison based on price
        return self.price <= other.price

    def __gt__(self, other):
        # Greater than comparison based on price
        return self.price > other.price

    def __ge__(self, other):
        # Greater than or equal comparison based on price
        return self.price >= other.price
