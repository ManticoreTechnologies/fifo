# Manticore Technologies LLC
# (c) 2024 
# Manticore Crypto Faucet
#       utils.py 


# Logging #
import logging
import colorlog
import os

from flask import jsonify, request
import redis



# Get the name of parent folder
SERVICE_NAME = os.path.basename(os.path.dirname(__file__))


def create_logger():
    logger = logging.getLogger(os.path.basename(__file__))

    # Set the logging level from the argument
    logger.setLevel(config['General']['log_level'])

    # Clear existing handlers if any
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create a stream handler with color formatting
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = colorlog.ColoredFormatter(
        fmt=(
            "%(log_color)s%(asctime)s - %(name)-15s - %(levelname)-8s - %(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
    )
    fh = logging.FileHandler(f'./{SERVICE_NAME}.log')
    fh.setLevel(config['General']['log_level'])

    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    return logger

# Arguments #
import argparse

def parse_args():
    # Get the logging level argument
    parser = argparse.ArgumentParser(
        prog=f'{SERVICE_NAME}',
        description='Service for {SERVICE_NAME}',
        epilog='Manticore Technologies LLC'
    )
    parser.add_argument('--log-level', 
                        choices=['DEBUG', 'WARNING', 'CRITICAL', 'INFO', 'ERROR'], 
                        default='CRITICAL', 
                        help='Set the logging level (default: INFO)')

    return parser.parse_args()

# Settings #
import configparser
import os
import shutil

config = configparser.ConfigParser()
config_path = f'../{SERVICE_NAME}.conf'
example_config_path = './example.conf'

if not os.path.exists(config_path):
    shutil.copy(example_config_path, config_path)

config.read(config_path)


# Welcome #
welcome_message =(
        f"\n"
        "========================================\n"
        f"              {SERVICE_NAME}            \n"
        "========================================\n"
        "  (c) 2024 Manticore Technologies LLC   \n"
        "----------------------------------------\n"
        f"Welcome to the {SERVICE_NAME}! \n"
        "This service is ready with redis and ready to serve requests.\n"
        "----------------------------------------\n"
)

import json 

redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))


# Initialize Redis connection
redis_client = redis.Redis(host=redis_host, port=redis_port, db=0)  # Adjust host/port/db if necessary

# Initialize the logger
logger = create_logger()

def save_data_to_redis(key, data):
    """
    Save generalized data to Redis as JSON.
    """
    try:
        # Prepend SERVICE_NAME to the key to ensure uniqueness
        namespaced_key = f"{SERVICE_NAME}:{key}"
        data_str = json.dumps(data)  # Convert data to JSON string
        redis_client.set(namespaced_key, data_str)  # Save to Redis
        logger.debug(f"Data saved to Redis with key: {namespaced_key}.")
    except Exception as e:
        logger.error(f"Failed to save data to Redis with key {namespaced_key}: {str(e)}")


def remove_data_from_redis(key):
    """
    Remove data from Redis.
    """
    try:
        # Prepend SERVICE_NAME to the key to ensure uniqueness
        namespaced_key = f"{SERVICE_NAME}:{key}"
        redis_client.delete(namespaced_key)
    except Exception as e:
        logger.error(f"Failed to remove data from Redis with key {namespaced_key}: {str(e)}")


def get_data_from_redis(key):
    """
    Retrieve data from Redis.
    """
    try:
        # Prepend SERVICE_NAME to the key to ensure uniqueness
        namespaced_key = f"{SERVICE_NAME}:{key}"
        data_str = redis_client.get(namespaced_key)
        if data_str:
            return json.loads(data_str)  # Convert back to Python dict
        return None
    except Exception as e:
        logger.error(f"Failed to retrieve data from Redis with key {namespaced_key}: {str(e)}")



def validate_data(data):

    if request.content_type != 'application/json':
        return jsonify({"error": "Content-Type must be application/json"}), 415

    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400
    


