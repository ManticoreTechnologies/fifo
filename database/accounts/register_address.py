from utils import save_data_to_redis, get_data_from_redis
from rpc import send_command

def register_address(address):
    
    # Create a new address
    new_address = send_command("getnewaddress", {})
    
    # Map the address to the user_address
    save_data_to_redis(f"address:{address}", new_address)

    # Save the address to the addresses to monitor for new transactions
    save_data_to_redis(f"addresses", [])
    addresses = get_data_from_redis("addresses")
    if addresses is None:
        addresses = []
    addresses.append(new_address)
    save_data_to_redis("addresses", addresses)

    # Initialize the account
    account = {
        "address": new_address,
        "balances": {"evr": 0},
        "orders": {"bids": {}, "asks": {}} # order_id: order
    }

    # Save the account to Redis
    save_data_to_redis(f"account:{address}", account)

    return new_address