import random
from Market import Market
from Order import Order
from Price import Price
#####
symbol = "BTC-USDT" # The symbol of the market, this is used to identify the market and must be in this format "AAA...-BBB..."
units = 0 # The number of units the market is divided into, 0-8 for example 8 would have pip size 0.00000001


# Create a new market, This should be only done by admin and serialized into redis as a hashmap
market = Market("BTCUSDT")

# Populate with some bids only
market.add_order(Order("address1", "BTCUSDT", "bid", 10000, 1, "order1"))
market.add_order(Order("address2", "BTCUSDT", "bid", 10001, 1, "order2"))
market.add_order(Order("address3", "BTCUSDT", "bid", 10002, 1, "order3"))
market.add_order(Order("address4", "BTCUSDT", "bid", 10003, 1, "order4"))
market.add_order(Order("address5", "BTCUSDT", "bid", 10004, 1, "order5"))
market.add_order(Order("address6", "BTCUSDT", "bid", 10005, 1, "order6"))

# Populate with some asks only, all higher than bids
market.add_order(Order("address7", "BTCUSDT", "ask", 10006, 10, "order7"))
market.add_order(Order("address8", "BTCUSDT", "ask", 10007, 1, "order8"))
market.add_order(Order("address9", "BTCUSDT", "ask", 10008, 1, "order9"))
market.add_order(Order("address10", "BTCUSDT", "ask", 10009, 1, "order10"))

# Now test matching by placing a bid at 10006, this should fill both order 11 and order 7 since they are the same quantity
market.add_order(Order("address11", "BTCUSDT", "bid", 10005, 10, "order11"))
# Now test matching by placing a bid at 10006, this should fill both order 11 and order 7 since they are the same quantity
market.add_order(Order("address12", "BTCUSDT", "ask", 10000, 1, "order12"))

# So when printing the order book it should have a gap at 10006
market.pretty_print_order_book()

# Function to interactively place orders
def interactive_order_placement(market):
    while True:
        print("\nCurrent Order Book:")
        market.pretty_print_order_book()
        
        order_type = input("Enter order type (bid/ask) or 'exit' to quit: ").strip().lower()
        if order_type == 'exit':
            break
        if order_type not in ['bid', 'ask']:
            print("Invalid order type. Please enter 'bid' or 'ask'.")
            continue
        
        try:
            price = float(input("Enter price: ").strip())
            quantity = int(input("Enter quantity: ").strip())
        except ValueError:
            print("Invalid input. Please enter numeric values for price and quantity.")
            continue
        
        # Use a constant address for all orders
        address = "constant_address"
        order_id = f"order{random.randint(100, 999)}"
        
        market.add_order(Order(address, "BTCUSDT", order_type, price, quantity, order_id))
        print(f"Order {order_id} added: {order_type} {quantity} @ {price}")

# Call the interactive function
interactive_order_placement(market)
