from utils import save_data_to_redis, get_data_from_redis
from rpc import send_command

def register_address(address):
    
    # Create a new address
    new_address = send_command("getnewaddress", {})

    # Initialize the account
    account = {
        "address": new_address,
        "balances": {"evr": 0},
        "orders": {"bids": {}, "asks": {}} # order_id: order
    }

    # Save the account to Redis
    save_data_to_redis(f"account:{address}", account)
    
    return account