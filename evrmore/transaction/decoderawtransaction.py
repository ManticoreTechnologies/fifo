import hashlib
import struct
from .decodescript import decodescript  # Assuming this is the correct import path for your decodescript function

def clean_script(output_data):
    try:
        del output_data['scriptPubKey']["p2sh"]
    except:
        pass
    try:
        del output_data['scriptPubKey']["new_ipfs_hash"]
    except:
        pass
    try:
        del output_data['scriptPubKey']["reissuable"]
    except:
        pass
    try:
        del output_data['scriptPubKey']["amount"]
    except:
        pass
    try:
        del output_data['scriptPubKey']["asset_name"]
    except:
        pass
    return output_data
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

def decoderawtransaction(tx_data, offset=0, block=False):
    
    if isinstance(tx_data, str):
        tx_data = bytes.fromhex(tx_data)

    print(f"Decoding transaction: {tx_data.hex()}")
    start_offset = offset
    """Decodes a raw transaction (handles both legacy and SegWit) and computes the txid."""
    decoded_tx = {}
    is_segwit = False
    is_coinbase = False
    # Store a copy for computing txid later (this should exclude witness data)
    txid_data = tx_data[:]

    # 1. Version (4 bytes)
    version = struct.unpack("<I", tx_data[offset:offset + 4])[0]
    offset += 4
    decoded_tx["version"] = version
    print(f"Version: {version}")
    # 2. Check for Marker and Flag for SegWit (2 bytes)
    marker = tx_data[offset]
    flag = tx_data[offset + 1]

    if marker == 0x00 and flag == 0x01:
        is_segwit = True
        # Remove the marker and flag from txid_data but include the rest            
        txid_data = tx_data[:offset] + tx_data[offset + 2:]
        offset+=2
    # 3. Input Count (varint)
    input_count, offset = read_varint(tx_data, offset)
    print(f"Input count: {input_count}")
    # 4. Inputs
    vin = []
    for i in range(input_count):
        input_data = {}
        prev_tx_hash = tx_data[offset:offset + 32][::-1].hex()  # Reverse the hash for display
        offset += 32
        offset_start = offset
        prev_tx_index = struct.unpack("<I", tx_data[offset:offset + 4])[0]
        offset += 4
        
        # Check if it's a coinbase transaction (prev_tx_hash is all zeros)
        if prev_tx_hash == '00' * 32:
            is_coinbase = True
            # Handle coinbase input
            script_len, offset = read_varint(tx_data, offset)
            coinbase_data = tx_data[offset:offset + script_len]
            offset += script_len
            sequence = struct.unpack("<I", tx_data[offset:offset + 4])[0]
            offset += 4
            input_data["coinbase"] = coinbase_data.hex()
            input_data["sequence"] = sequence
            # Remove coinbase data from txid_data
            txid_data = txid_data[:offset_start] + txid_data[offset:]

        else:
            # Handle regular inputs
            script_len, offset = read_varint(tx_data, offset)
            script_sig = tx_data[offset:offset + script_len]
            script_sig_hex = script_sig.hex()
            offset += script_len
            sequence = struct.unpack("<I", tx_data[offset:offset + 4])[0]
            offset += 4

            input_data["txid"] = prev_tx_hash
            input_data["vout"] = prev_tx_index
            input_data["scriptSig"] = {
                "hex": script_sig_hex
            }
            input_data["sequence"] = sequence
            print(f"Decoding scriptSig: {script_sig_hex}")
            decoded_script = decodescript(script_sig_hex, True)
            
            input_data["scriptSig"].update(decoded_script)
            print(input_data["scriptSig"])
        vin.append(input_data)

    decoded_tx["vin"] = vin
    


    # 6. Output Count (varint)
    output_count, offset = read_varint(tx_data, offset)

    # 7. Outputs
    vout = []
    for i in range(output_count):
        output_data = {}
        value = struct.unpack("<Q", tx_data[offset:offset + 8])[0]  # 8 bytes for value
        offset += 8
        script_len, offset = read_varint(tx_data, offset)
        script_pubkey = tx_data[offset:offset + script_len]
        script_pubkey_hex = script_pubkey.hex()
        offset += script_len

        output_data["value"] = value / 100000000  # Convert satoshis to BTC
        output_data["n"] = i
        output_data["scriptPubKey"] = {
            "hex": script_pubkey_hex
        }
        
        decoded_script = decodescript(script_pubkey_hex)
        output_data["scriptPubKey"].update(decoded_script)
        output_data = clean_script(output_data)
        vout.append(output_data)
    decoded_tx["vout"] = vout

    # Check for witness data
    if is_segwit:
        # Get the flag and marker
        flag = tx_data[offset]
        marker = tx_data[offset + 1]
        txid_data = txid_data[:offset] + txid_data[offset + 2:]
        offset += 2
    if is_coinbase:
        offset+=32

    # 8. Lock Time (4 bytes)
    print(tx_data[offset:offset+4].hex())
    lock_time = struct.unpack("<I", tx_data[offset:offset + 4])[0]
    decoded_tx["locktime"] = lock_time
    offset += 4

    # Compute the txid by hashing the serialized transaction (no witness data)
    txid = compute_txid(tx_data[start_offset:offset])
    decoded_tx["txid"] = txid
    decoded_tx["hash"] = hashlib.sha256(hashlib.sha256(tx_data[start_offset:offset]).digest()).digest()[::-1].hex()


    decoded_tx["size"] = len(tx_data[start_offset:offset])
    if is_segwit:
        base_size = len(tx_data[start_offset:offset])  # txid_data excludes witness data
        total_size = len(tx_data[start_offset:offset])
        weight = base_size * 3 + total_size
        decoded_tx["vsize"] = (weight + 3) // 4  # Round up division for vsize
    else:
        decoded_tx["vsize"] = len(tx_data[start_offset:offset])

    if block:
        decoded_tx["hex"] = tx_data.hex()


    
    return decoded_tx
