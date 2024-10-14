from utils import get_data_from_redis

def get_orderbook():
    """
    Get the orderbook for a symbol.
    """
    return get_data_from_redis(f"orderbook")