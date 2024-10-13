from utils import save_data_to_redis, get_data_from_redis


# TODO: Split orders into buy and sell orders
# TODO: Add order matching logic

def save_order_to_account(order, address):
    # Save the order to the users account
    account = get_data_from_redis(f"account:{address}")
    # Orders is a dict with bids and asks 
    try:
        account["orders"][order["side"]+'s'][order["price"]][order["order_id"]] = order
    except KeyError:
        account["orders"][order["side"]+'s'][order["price"]] = {}
        account["orders"][order["side"]+'s'][order["price"]][order["order_id"]] = order
    save_data_to_redis(f"account:{address}", account)


def save_order(order):
    """
    Save an order to Redis.
    """
    side = order.get("side")
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
    save_data_to_redis(f"orders:{side}:{order['user_address']}", {})
    user_orders = get_data_from_redis(f"orders:{order['user_address']}")
    if user_orders is None:
        user_orders = {}
    user_orders[order["order_id"]] = order
    save_data_to_redis(f"orders:{side}:{order['user_address']}", user_orders)

    # Save the order to the orderbook dictionary
    save_data_to_redis(f"orderbook:{side}:{order['symbol']}", {})
    orderbook = get_data_from_redis(f"orderbook:{side}:{order['symbol']}")
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
    save_data_to_redis(f"orderbook:{side}:{order['symbol']}", orderbook)



    # Save the order to the orderbook for the symbol aggregate by price level
    save_data_to_redis(f"orderbook:{side}:{order['symbol']}:{order['price']}", [])
    orderbook_orders = get_data_from_redis(f"orderbook:{side}:{order['symbol']}:{order['price']}")
    if orderbook_orders is None:
        orderbook_orders = []
    orderbook_orders.append(order)
    save_data_to_redis(f"orderbook:{side}:{order['symbol']}:{order['price']}", orderbook_orders)

    save_order_to_account(order, order["user_address"])