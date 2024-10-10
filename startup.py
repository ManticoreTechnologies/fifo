# Import utilities
import time
from rpc import send_command
from utils import create_logger, get_data_from_redis, welcome_message, config, SERVICE_NAME
import hashlib
import base58
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
    decoded_tx = {}

    # 1. Version (4 bytes)
    version = struct.unpack("<I", tx_data[offset:offset + 4])[0]
    offset += 4
    decoded_tx["version"] = version

    # 2. Input Count (varint)
    input_count, offset = read_varint(tx_data, offset)

    # 3. Inputs
    vin = []
    for i in range(input_count):
        input_data = {}
        prev_tx_hash = tx_data[offset:offset + 32][::-1].hex()  # Reverse the hash
        offset += 32
        prev_tx_index = struct.unpack("<I", tx_data[offset:offset + 4])[0]
        offset += 4
        script_len, offset = read_varint(tx_data, offset)
        script_sig = tx_data[offset:offset + script_len]
        script_sig_hex = script_sig.hex()
        script_sig_asm = decode_script_to_json(script_sig_hex)["asm"]
        offset += script_len
        sequence = struct.unpack("<I", tx_data[offset:offset + 4])[0]
        offset += 4

        input_data["txid"] = prev_tx_hash
        input_data["vout"] = prev_tx_index
        input_data["scriptSig"] = {
            "asm": script_sig_asm,
            "hex": script_sig_hex
        }
        input_data["sequence"] = sequence

        vin.append(input_data)
    decoded_tx["vin"] = vin

    # 4. Output Count (varint)
    output_count, offset = read_varint(tx_data, offset)

    # 5. Outputs
    vout = []
    for i in range(output_count):
        output_data = {}
        value = struct.unpack("<Q", tx_data[offset:offset + 8])[0]  # 8 bytes for value
        offset += 8
        script_len, offset = read_varint(tx_data, offset)
        script_pubkey = tx_data[offset:offset + script_len]
        script_pubkey_hex = script_pubkey.hex()
        script_pubkey_json = decode_script_to_json(script_pubkey_hex)
        offset += script_len

        output_data["value"] = value / 100000000  # Convert satoshis to BTC
        output_data["n"] = i
        output_data["scriptPubKey"] = {
            "asm": script_pubkey_json["asm"],
            "hex": script_pubkey_hex,
            "reqSigs": script_pubkey_json["reqSigs"],
            "type": script_pubkey_json["type"],
            "addresses": script_pubkey_json["addresses"]
        }

        vout.append(output_data)
    decoded_tx["vout"] = vout

    # 6. Lock Time (4 bytes)
    lock_time = struct.unpack("<I", tx_data[offset:offset + 4])[0]
    decoded_tx["locktime"] = lock_time

    # Add additional fields
    decoded_tx["txid"] = "c6f15501b6dbe691ccbd113c41beef2614950750a54f0a7ef692b2bbc2976125"  # Placeholder
    decoded_tx["hash"] = "c6f15501b6dbe691ccbd113c41beef2614950750a54f0a7ef692b2bbc2976125"  # Placeholder
    decoded_tx["size"] = len(tx_data)
    decoded_tx["vsize"] = len(tx_data)  # Assuming no witness data

    return decoded_tx


def hash160_to_address(pubkey_hash):
    """Convert the HASH160 public key hash to a base58check encoded address."""
    # Prefix for Evrmore address (0x21) - adjust based on the network you're working with
    prefix = b'\x21'
    h160_with_prefix = prefix + pubkey_hash
    checksum = hashlib.sha256(hashlib.sha256(h160_with_prefix).digest()).digest()[:4]
    address = base58.b58encode(h160_with_prefix + checksum).decode('utf-8')
    return address

def decode_script_to_json(script_hex):
    opcodes = {
        "76": "OP_DUP",
        "a9": "OP_HASH160",
        "88": "OP_EQUALVERIFY",
        "ac": "OP_CHECKSIG",
    }
    
    script_bytes = bytes.fromhex(script_hex)
    offset = 0
    asm = []
    addresses = []
    req_sigs = 1  # Default for P2PKH
    script_type = "pubkeyhash"

    while offset < len(script_bytes):
        byte = script_bytes[offset]
        offset += 1

        hex_byte = f"{byte:02x}"
        if hex_byte in opcodes:
            asm.append(opcodes[hex_byte])
        elif 1 <= byte <= 75:
            # If it's a push, get the number of bytes to push
            length = byte
            pushed_data = script_bytes[offset:offset + length]
            asm.append(pushed_data.hex())
            offset += length
            if length == 20:  # Likely a HASH160 (public key hash)
                pubkey_hash = pushed_data
                address = hash160_to_address(pubkey_hash)
                addresses.append(address)
        else:
            asm.append(f"UNKNOWN OPCODE: {hex_byte}")

    return {
        "asm": " ".join(asm),
        "reqSigs": req_sigs,
        "type": script_type,
        "addresses": addresses
    }

def on_hashtx(hashtx_message, node_tx_index):
    print(f"New transaction hash received.")

def on_rawtx(rawtx_message, node_tx_index):
    print("New raw transaction received.")
    decoded_transaction = decode_transaction(rawtx_message)
    vout = decoded_transaction["vout"]
    addresses = get_data_from_redis("addresses")
    for output in vout:
        if output["scriptPubKey"]["type"] == "pubkeyhash":
            address = output["scriptPubKey"]["addresses"][0]
            if address in addresses:
                print(f"Deposit detected: {address}")

def on_hashblock(hashblock_message, node_block_index):
    print("New hash block received.")

def on_rawblock(rawblock_message, node_block_index):
    print("New raw block received.")

def on_sequence(sequence_message):
    print("New sequence received.")

if __name__ == "__main__":
    from monitor import ZMQListener
    callbacks = {
        "zmqpubhashtx": on_hashtx,
        "zmqpubrawtx": on_rawtx,
        "zmqpubhashblock": on_hashblock,
        "zmqpubrawblock": on_rawblock,
        "zmqpubsequence": on_sequence,
    }
    zmq_listener = ZMQListener(callbacks)
    zmq_listener.listen()


