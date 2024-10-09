
from utils import get_data_from_redis


def list_orders(user_address):
    """
    List all orders for a user.
    """
    # Get all the orders from Redis
    orders = get_data_from_redis(f"orders:{user_address}")
    return orders