import hashlib
import struct
from .decodescript import decodescript  # Assuming decodescript exists for script decoding

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

def compute_txid(tx_data):
    """Computes the TXID by double hashing the transaction data (excluding witness)."""
    txid_hash = hashlib.sha256(hashlib.sha256(tx_data).digest()).digest()
    return txid_hash[::-1].hex()  # reverse for little-endian display

def decodecoinbasetransaction(tx_data):
    """Decodes a raw Evrmore coinbase transaction and returns it in the required format."""
    offset = 0
    decoded_tx = {}

    
    # 1. Version (4 bytes)
    version = struct.unpack("<I", tx_data[offset:offset + 4])[0]
    offset += 4
    decoded_tx["version"] = version
    print("Version",version)
    # Store a copy for computing the txid excluding witness data
    txid_data = tx_data[:4]  # Start with version number
    print("Txid Data",txid_data)
    # 2. Marker and Flag for Segregated Witness (2 bytes)
    marker = tx_data[offset]
    flag = tx_data[offset + 1]
    offset += 2
    print("Marker",marker)
    print("Flag",flag)
    # Dont include witness data in txid_data

    if marker != 0x00 or flag != 0x01:
        raise ValueError("Invalid marker and flag for Segregated Witness transaction")

    # 3. Input Count (varint)
    input_count, offset = read_varint(tx_data, offset)
    print("Input Count",input_count)

    # 4. Previous txid 
    prev_txid = tx_data[offset:offset + 32][::-1].hex()  # Reverse the hash for display
    offset += 32
    print("Prev Txid",prev_txid)

    vout_index = tx_data[offset:offset + 4]
    offset += 4

    script_len, offset = read_varint(tx_data, offset)

    coinbase_data = tx_data[offset:offset + script_len]
    offset += script_len


    sequence = struct.unpack("<I", tx_data[offset:offset + 4])[0]
    offset += 4
    print("Sequence",sequence) 


    

    decoded_tx["vin"] = [{
        "coinbase": coinbase_data.hex(),
        "sequence": sequence
    }]

    # 5. Output Count (varint)
    output_count, offset = read_varint(tx_data, offset)
    print("Output Count",output_count)


    # 6. Outputs (Includes dev fee and miner rewards)
    vout = []
    for i in range(output_count):
        output_data = {}
        value = tx_data[offset:offset + 8]  # 8 bytes for value

        txid_data+=value # Add value to txid_data

        offset += 8

        print("Value",value.hex())
        __offset = offset
        script_len, offset = read_varint(tx_data, offset)
        print("Script Length",script_len)
        txid_data += tx_data[__offset:offset]
        script_pubkey_bytes = tx_data[offset:offset + script_len]
        offset += script_len

        txid_data+=script_pubkey_bytes # Add script_pubkey_bytes to txid_data
        
        script_pubkey_hex = script_pubkey_bytes.hex()
        print("Script Pubkey",script_pubkey_hex)

        output_data["value"] = int.from_bytes(value, "little") / 100000000 #Convert from little endian to hex
        output_data["n"] = i
        output_data["scriptPubKey"] = {
            "hex": script_pubkey_hex # Convert to string
        }

        # Decode the script to get the asm and other details
        decoded_script = decodescript(script_pubkey_hex)
        output_data["scriptPubKey"].update(decoded_script)

        vout.append(output_data)

    decoded_tx["vout"] = vout
    print(vout)

    # Get segwit data  (4 bytes)
    segwit_data = tx_data[offset:offset + 4]
    offset += 4
    print("Segwit Data",segwit_data.hex())

    # 7. Lock Time (4 bytes)
    lock_time = struct.unpack("<I", tx_data[offset:offset + 4])[0]  # Correctly read as little-endian unsigned int
    decoded_tx["locktime"] = lock_time

    offset += 4
    print("Lock Time:", lock_time)

    # Compute the txid by hashing the serialized transaction (excluding witness data)
    txid = compute_txid(txid_data)

    decoded_tx["txid"] = txid

    # Since the witness data is present, compute the transaction hash as well
    hash_tx = hashlib.sha256(hashlib.sha256(tx_data).digest()).digest()[::-1].hex()
    decoded_tx["hash"] = hash_tx

    decoded_tx["size"] = len(tx_data)
    # Calculate the weight and vsize
    base_size = len(txid_data)  # txid_data is the transaction data excluding witness
    total_size = len(tx_data)
    weight = base_size * 3 + total_size
    decoded_tx["vsize"] = (weight + 3) // 4  # Round up division

    print(decoded_tx)

    return decoded_tx
