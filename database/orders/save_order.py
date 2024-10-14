from utils import save_data_to_redis, get_data_from_redis


# TODO: Split orders into buy and sell orders
# TODO: Add order matching logic

# Redis structure:
# account:
# {
#   "orders": {
#     "bids": {
#       "price": {
#         "order_id": order
#       }
#     }
#   }
# }

def save_order_to_account(order, address):
    # Save the order to the users account
    account = get_data_from_redis(f"account:{address}")

    try:
        assert account["orders"]
    except KeyError:
        account["orders"] = {
            "bids": {},
            "asks": {}
        }
    try:
        assert account["orders"][order["side"]+'s'][order["price"]]
    except KeyError:
        account["orders"][order["side"]+'s'][order["price"]] = {}
        
    try:
        account["orders"][order["side"]+'s'][order["price"]][order["order_id"]] = order
    except KeyError:
        account["orders"][order["side"]+'s'][order["price"]] = {}
        account["orders"][order["side"]+'s'][order["price"]][order["order_id"]] = order

    save_data_to_redis(f"account:{address}", account)


# Redis structure:
# orderbook:
# {
#   "symbol": {
#     "bids": {
#       "price": {
#         "order_id": order
#       }
#     },
#     "asks": {


def save_order_to_orderbook(order):
    # Save the order to the orderbook
    # Orderbook is a dict with bids and asks
    # Each is a dict with price level as key and list of orders as value
    # The list of orders is First in First out (FIFO)

    # Get the orderbook from Redis
    orderbook = get_data_from_redis("orderbook")
    if orderbook is None:
        # If the orderbook is not in Redis, create it
        orderbook = {}
    try:
        # Check if the symbol is in the orderbook
        assert orderbook[order["symbol"]]
    except KeyError:
        # If the symbol is not in the orderbook, create it
        orderbook[order["symbol"]] = {
            "bids": {},
            "asks": {}
        }

    # Add the order to the orderbook
    try:
        # Try to append the order to the list of orders at the price level
        orderbook[order["symbol"]][order["side"]+'s'][str(order["price"])][order["order_id"]] = order
    except KeyError:
        # If the price level is not in the orderbook, create it
        orderbook[order["symbol"]][order["side"]+'s'][str(order["price"])] = {}
        orderbook[order["symbol"]][order["side"]+'s'][str(order["price"])][order["order_id"]] = order


    # Update the total quantity at the price level
    try:
        orderbook[order["symbol"]][order["side"]+'s'][str(order['price'])]["total"] += order["quantity"]
    except KeyError:
        orderbook[order["symbol"]][order["side"]+'s'][str(order['price'])]["total"] = order["quantity"]

    # Save the orderbook to Redis, keyed by "orderbook"
    save_data_to_redis(f"orderbook", orderbook)


def save_order(order):
    """
    Save an order to Redis.
    """

    # Get the side of the order
    side = order.get("side")



    # Save the order to the orderbook
    save_order_to_orderbook(order)

    # Saves the order to the account in the account hash
    save_order_to_account(order, order["user_address"]) # account:address = {orders: {"bids": {...}, "asks": {...}}, balances: {...}}
