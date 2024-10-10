from utils import save_data_to_redis, get_data_from_redis




def save_order(order):
    """
    Save an order to Redis.
    """

    # Map the order by its order_id
    save_data_to_redis(f"order:{order['order_id']}", order)

    # Add the order to the orders dictionary
    save_data_to_redis(f"orders", {})
    orders = get_data_from_redis("orders")
    if orders is None:
        orders = {}
    orders[order["order_id"]] = order
    save_data_to_redis("orders", orders)

    # Save the order to the users orders
    save_data_to_redis(f"orders:{order['user_address']}", {})
    user_orders = get_data_from_redis(f"orders:{order['user_address']}")
    if user_orders is None:
        user_orders = {}
    user_orders[order["order_id"]] = order
    save_data_to_redis(f"orders:{order['user_address']}", user_orders)

    # Save the order to the orderbook dictionary
    save_data_to_redis(f"orderbook:{order['symbol']}", {})
    orderbook = get_data_from_redis(f"orderbook:{order['symbol']}")
    if orderbook is None:
        orderbook = {}
    try:
        orders = orderbook[order["price"]]
    except KeyError:
        orders = {}
    
    if orders is None:
        orders = {}
    orders[order["order_id"]] = order
    orderbook[order["price"]] = orders
    save_data_to_redis(f"orderbook:{order['symbol']}", orderbook)



    # Save the order to the orderbook for the symbol aggregate by price level
    save_data_to_redis(f"orderbook:{order['symbol']}:{order['price']}", [])
    orderbook_orders = get_data_from_redis(f"orderbook:{order['symbol']}:{order['price']}")
    if orderbook_orders is None:
        orderbook_orders = []
    orderbook_orders.append(order)
    save_data_to_redis(f"orderbook:{order['symbol']}:{order['price']}", orderbook_orders)

    # Save the order to the user account
    account = get_data_from_redis(f"account:{order['user_address']}")
    account["orders"][order["order_id"]] = order
    save_data_to_redis(f"account:{order['user_address']}", account)
