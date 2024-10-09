from utils import get_data_from_redis

def get_order(order_id):
    """
    Get an order by order ID.
    """
    return get_data_from_redis(f"order:{order_id}")