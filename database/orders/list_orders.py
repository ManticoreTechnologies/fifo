
from utils import get_data_from_redis


def list_orders(user_address):
    """
    List all orders for a user.
    """
    # Get all the orders from Redis
    orders = {"asks": get_data_from_redis(f"orders:asks:{user_address}"), "bids": get_data_from_redis(f"orders:bids:{user_address}")}
    if orders["asks"] is None:
        orders["asks"] = []
    if orders["bids"] is None:
        orders["bids"] = []
        
    return orders
