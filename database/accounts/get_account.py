from utils import save_data_to_redis, get_data_from_redis
from rpc import send_command

def get_account(address):
    return get_data_from_redis(f"account:{address}")