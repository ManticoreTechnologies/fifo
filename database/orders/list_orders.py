
from utils import get_data_from_redis


def list_orders(user_address):
    """
    List all orders for a user.
    """
    # Get all the orders from Redis
    orders = {"sell": get_data_from_redis(f"orders:sell:{user_address}"), "buy": get_data_from_redis(f"orders:buy:{user_address}")}
    if orders["sell"] is None:
        orders["sell"] = []
    if orders["buy"] is None:
        orders["buy"] = []
        
    return orders
