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

import routes
import zmq
import time

import struct


def read_varint(data, offset):
    """Reads a variable-length integer from the transaction data."""
    first = data[offset]
    if first < 0xfd:
        return first, offset + 1
    elif first == 0xfd:
        return struct.unpack("<H", data[offset + 1:offset + 3])[0], offset + 3
    elif first == 0xfe:
        return struct.unpack("<I", data[offset + 1:offset + 5])[0], offset + 5
    else:
        return struct.unpack("<Q", data[offset + 1:offset + 9])[0], offset + 9

def decode_transaction(tx_data):
    """Decodes a raw Bitcoin-style transaction."""
    offset = 0

    # 1. Version (4 bytes)
    version = struct.unpack("<I", tx_data[offset:offset + 4])[0]
    offset += 4
    print(f"Version: {version}")

    # 2. Input Count (varint)
    input_count, offset = read_varint(tx_data, offset)
    print(f"Input Count: {input_count}")

    # 3. Inputs
    for i in range(input_count):
        print(f"\nInput #{i}:")
        prev_tx_hash = tx_data[offset:offset + 32][::-1].hex()  # Reverse the hash
        offset += 32
        prev_tx_index = struct.unpack("<I", tx_data[offset:offset + 4])[0]
        offset += 4
        script_len, offset = read_varint(tx_data, offset)
        script_sig = tx_data[offset:offset + script_len].hex()
        offset += script_len
        sequence = struct.unpack("<I", tx_data[offset:offset + 4])[0]
        offset += 4

        print(f"  Previous TX Hash: {prev_tx_hash}")
        print(f"  Previous TX Index: {prev_tx_index}")
        print(f"  Script Length: {script_len}")
        print(f"  ScriptSig: {script_sig}")
        print(f"  Sequence: {sequence}")

    # 4. Output Count (varint)
    output_count, offset = read_varint(tx_data, offset)
    print(f"\nOutput Count: {output_count}")

    # 5. Outputs
    for i in range(output_count):
        print(f"\nOutput #{i}:")
        value = struct.unpack("<Q", tx_data[offset:offset + 8])[0]  # 8 bytes for value
        offset += 8
        script_len, offset = read_varint(tx_data, offset)
        script_pubkey = tx_data[offset:offset + script_len].hex()
        offset += script_len

        print(f"  Value (satoshis): {value}")
        print(f"  Script Length: {script_len}")
        print(f"  ScriptPubKey: {script_pubkey}")

    # 6. Lock Time (4 bytes)
    lock_time = struct.unpack("<I", tx_data[offset:offset + 4])[0]
    print(f"\nLock Time: {lock_time}")





if __name__ == "__main__":
    # Initialize ZeroMQ context and sockets
    context = zmq.Context()
    
    sockets = {
        "zmqpubhashtx": context.socket(zmq.SUB),
        "zmqpubrawblock": context.socket(zmq.SUB),
        "zmqpubsequence": context.socket(zmq.SUB),
        "zmqpubrawtx": context.socket(zmq.SUB),
        "zmqpubhashblock": context.socket(zmq.SUB)
    }
    
    addresses = {
        "zmqpubhashtx": "tcp://127.0.0.1:2936",
        "zmqpubrawblock": "tcp://127.0.0.1:2935",
        "zmqpubsequence": "tcp://127.0.0.1:2934",
        "zmqpubrawtx": "tcp://127.0.0.1:29332",
        "zmqpubhashblock": "tcp://127.0.0.1:29333"
    }
    
    for key, socket in sockets.items():
        socket.connect(addresses[key])
        socket.setsockopt_string(zmq.SUBSCRIBE, '')
        socket.setsockopt(zmq.RCVTIMEO, 1000)  # Set a timeout of 1000ms (1 second)
    
    print("Listening for messages...")

    while True:
        try:
            for key, socket in sockets.items():
                try:
                    # Receive the raw bytes message in non-blocking mode
                    message = socket.recv(flags=zmq.NOBLOCK)
                    if message == bytes("rawtx", "utf-8"):
                        print(f"Received rawtx message on {key}")
                        # Receive the next message which is the raw transaction in hex
                        raw_tx_message = socket.recv(flags=zmq.NOBLOCK)
                        node_tx_index = socket.recv(flags=zmq.NOBLOCK)
                        print(f"Raw transaction received: {len(raw_tx_message.hex())}: {int.from_bytes(node_tx_index, byteorder='little')}")
                    elif message == bytes("hashtx", "utf-8"):
                        print(f"Received hashtx message on {key}")
                        # Receive the next message which is the raw transaction in hex
                        hashtx_message = socket.recv(flags=zmq.NOBLOCK)
                        node_tx_index = socket.recv(flags=zmq.NOBLOCK)
                        print(f"Hash transaction received: {len(hashtx_message.hex())}: {int.from_bytes(node_tx_index, byteorder='little')}")
                    elif message == bytes("rawblock", "utf-8"):
                        print(f"Received rawblock message on {key}")
                        # Receive the next message which is the raw block in hex
                        rawblock_message = socket.recv(flags=zmq.NOBLOCK)
                        node_block_index = socket.recv(flags=zmq.NOBLOCK)
                        print(f"Raw block received: {len(rawblock_message.hex())}: {int.from_bytes(node_block_index, byteorder='little')}")
                    elif message == bytes("sequence", "utf-8"):
                        print(f"Received sequence message on {key}")
                        # Receive the next message which is the sequence in hex
                        sequence_message = socket.recv(flags=zmq.NOBLOCK)
                        print(f"Sequence: {sequence_message.hex()}")
                    elif message == bytes("hashblock", "utf-8"):
                        print(f"Received hashblock message on {key}")
                        # Receive the next message which is the hashblock in hex
                        hashblock_message = socket.recv(flags=zmq.NOBLOCK)
                        node_block_index = socket.recv(flags=zmq.NOBLOCK)
                        print(f"Hash block received: {len(hashblock_message.hex())}: {int.from_bytes(node_block_index, byteorder='little')}")
                    else:
                        print(f"Received unknown message on {key}: {int.from_bytes(message, byteorder='little')}")
                        
                except zmq.Again:
                    # No message was ready to be received
                    continue

        except Exception as e:
            print(f"Error receiving message: {e}")

