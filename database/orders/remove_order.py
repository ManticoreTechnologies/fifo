from utils import remove_data_from_redis, save_data_to_redis, get_data_from_redis

def remove_order(order_id):
    """
    Remove an order from Redis.
    """

    # Get the order from Redis
    order = get_data_from_redis(f"order:{order_id}")
    if order is None:
        return

    # Remove the order from Redis
    remove_data_from_redis(f"order:{order_id}")

    # Remove the order from the orders dictionary
    orders = get_data_from_redis("orders")
    if orders is not None:
        del orders[order_id]
        save_data_to_redis("orders", orders)

    # Remove the order from the orderbook
    orderbook = get_data_from_redis(f"orderbook:{order['symbol']}")
    if orderbook is not None:
        del orderbook[str(order["price"])][order_id]
        save_data_to_redis(f"orderbook:{order['symbol']}", orderbook)

    # Remove the order from the orderbook for the symbol aggregate by price level
    orderbook_orders = get_data_from_redis(f"orderbook:{order['symbol']}:{order['price']}")
    if orderbook_orders is not None:
        orderbook_orders.remove(order)
        save_data_to_redis(f"orderbook:{order['symbol']}:{order['price']}", orderbook_orders)

    # Remove the order from the user account
    account = get_data_from_redis(f"account:{order['user_address']}")
    del account["orders"][order_id]
    save_data_to_redis(f"account:{order['user_address']}", account)
