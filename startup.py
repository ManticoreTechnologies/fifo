# Import utilities
import time
from rpc import send_command
from utils import create_logger, get_data_from_redis, welcome_message, config, SERVICE_NAME

# Create a logger
logger = create_logger()

# Import Flask
from flask import Flask

# Create flask application
app = Flask(f"Manticore {SERVICE_NAME}")

# Print the welcome message
print(welcome_message)


import routes  # Import routes

if __name__ == "__main__":
    import zmq

    # Set up a ZMQ context and socket to listen for zmqpubrawtx
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://127.0.0.1:29332")
    socket.setsockopt_string(zmq.SUBSCRIBE, '')

    while True:
        message = socket.recv_string()
        print(f"Received raw transaction: {message}")
        time.sleep(5)

