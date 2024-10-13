import hashlib
import base58  # type: ignore
def hex_to_ipfs_cidv0(hex_str):
    # Convert the hex string into bytes
    hash_bytes = bytes.fromhex(hex_str)
    
    # Add the multicodec prefix for SHA-256 (0x12 0x20)
    prefixed_hash = b'\x12\x20' + hash_bytes
    
    # Base58-encode the prefixed hash to get the CIDv0
    cid = base58.b58encode(prefixed_hash).decode('utf-8')
    
    return cid
def hash160(data):
    """SHA256 followed by RIPEMD-160 (HASH160)."""
    sha256_hash = hashlib.sha256(data).digest()
    ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
    return ripemd160_hash

def hash160_to_address(pubkey_hash, prefix=b'\x21'):
    """Convert the HASH160 public key hash to a base58check encoded address."""
    h160_with_prefix = prefix + pubkey_hash
    checksum = hashlib.sha256(hashlib.sha256(h160_with_prefix).digest()).digest()[:4]
    address = base58.b58encode(h160_with_prefix + checksum).decode('utf-8')
    return address

def script_to_p2sh(script_hex):
    """Convert the script into a P2SH address."""
    script_bytes = bytes.fromhex(script_hex)
    script_hash = hash160(script_bytes)  # HASH160 of the script
    prefix = b'\x5c'  # Prefix for Evrmore P2SH addresses
    prefixed_hash = prefix + script_hash
    checksum = hashlib.sha256(hashlib.sha256(prefixed_hash).digest()).digest()[:4]
    p2sh_address = base58.b58encode(prefixed_hash + checksum).decode('utf-8')
    return p2sh_address
def decode_transfer_asset_script(asset_data_hex, asset_data_offset):
    
    # Grab the asset name length
    asset_name_len = asset_data_hex[asset_data_offset:asset_data_offset+2]
    asset_name_len = int(asset_name_len, 16)
    asset_data_offset += 2

    # Now get the asset name
    asset_name = bytes.fromhex(asset_data_hex[asset_data_offset:asset_data_offset+asset_name_len*2])
    # Decode the asset name from hex to ascii
    asset_name = asset_name.decode('utf-8')
    asset_data_offset += asset_name_len*2

    # Now get the amount
    asset_amount = bytes.fromhex(asset_data_hex[asset_data_offset:asset_data_offset+16])
    asset_amount = int.from_bytes(asset_amount, "little") / 100000000
    asset_data_offset += 16

    return {"name": asset_name, "amount": asset_amount, "units": 0, "reissuable": False, "hasIPFS": False}, asset_data_offset

def decode_reissue_asset_script(asset_data_hex, asset_data_offset):
    asset = {}
    # Grab the asset name length
    asset_name_len = asset_data_hex[asset_data_offset:asset_data_offset+2]
    asset_name_len = int(asset_name_len, 16)
    asset_data_offset += 2

    # Now get the asset name
    asset_name = bytes.fromhex(asset_data_hex[asset_data_offset:asset_data_offset+asset_name_len*2])
    asset["name"] = asset_name.decode('utf-8')
    asset_data_offset += asset_name_len*2

    # Now get the amount
    asset_amount = bytes.fromhex(asset_data_hex[asset_data_offset:asset_data_offset+16])
    asset_amount = int.from_bytes(asset_amount, "little") / 100000000
    asset_data_offset += 16
    asset["amount"] = asset_amount


    asset_units = asset_data_hex[asset_data_offset:asset_data_offset+2]
    asset_data_offset += 2

    if asset_units == 'ff':
        # If the asset units are FF then this is a reissuable asset and following is the user data 
        asset["reissuable"] = True
    else:
        # Otherwise the asset units are updated
        asset_units = int(asset_units, 16)
        asset["units"] = asset_units
        # And the reissuable flag is next
        asset_reissuable = asset_data_hex[asset_data_offset:asset_data_offset+2]
        asset_reissuable = int(asset_reissuable, 16)
        asset["reissuable"] = asset_reissuable


    # Has user data?
    user_data_flag = asset_data_hex[asset_data_offset:asset_data_offset+2]
    user_data_flag = int(user_data_flag, 16)
    asset_data_offset += 2
    if user_data_flag == 1:
        asset["hasIPFS"] = True
        # Get user data type
        user_data_type = asset_data_hex[asset_data_offset:asset_data_offset+2]
        user_data_type = int(user_data_type, 16)
        asset_data_offset += 2

        # Get user data length
        user_data_len = asset_data_hex[asset_data_offset:asset_data_offset+2]
        user_data_len = int(user_data_len, 16)
        asset_data_offset += 2

        user_data = asset_data_hex[asset_data_offset:asset_data_offset+user_data_len*2]
        asset_data_offset += user_data_len*2
        if user_data_type == 18:
            # If the user data type is 0x12 = 18 then the user data is an IPFS
            # Decode the hex into bytes and then to base58
            user_data = hex_to_ipfs_cidv0(user_data)
            asset["ipfs_hash"] = user_data
        elif user_data_type == 84:
            # If the user data type is 0x54 = 84 then the user data is a base58 encoded string
            # 
            print(f"User data is a transaction txid: {user_data}")
        

    return asset, asset_data_offset

def decode_new_asset_script(asset_data_hex, asset_data_offset):
    # Grab the asset name length
    asset_name_len = asset_data_hex[asset_data_offset:asset_data_offset+2]
    asset_name_len = int(asset_name_len, 16)
    asset_data_offset += 2

    # Now get the asset name
    asset_name = bytes.fromhex(asset_data_hex[asset_data_offset:asset_data_offset+asset_name_len*2])
    # Decode the asset name from hex to ascii
    asset_name = asset_name.decode('utf-8')
    asset_data_offset += asset_name_len*2

    # Now get the amount
    asset_amount = bytes.fromhex(asset_data_hex[asset_data_offset:asset_data_offset+16])
    asset_amount = int.from_bytes(asset_amount, "little") / 100000000
    asset_data_offset += 16

    # Get the units
    asset_units = asset_data_hex[asset_data_offset:asset_data_offset+2]
    asset_units = int(asset_units, 16)
    asset_data_offset += 2

    # Get the reissuable flag
    asset_reissuable = asset_data_hex[asset_data_offset:asset_data_offset+2]
    asset_reissuable = int(asset_reissuable, 16)
    asset_data_offset += 2

    # Has user data?
    user_data_flag = asset_data_hex[asset_data_offset:asset_data_offset+2]
    user_data_flag = int(user_data_flag, 16)
    asset_data_offset += 2

    hasIPFS = False
    if user_data_flag == 1:
        hasIPFS = True
        # Get user data type
        user_data_type = asset_data_hex[asset_data_offset:asset_data_offset+2]
        user_data_type = int(user_data_type, 16)
        asset_data_offset += 2

        # Get user data length
        user_data_len = asset_data_hex[asset_data_offset:asset_data_offset+2]
        user_data_len = int(user_data_len, 16)
        asset_data_offset += 2

        # Get user data, minus OP_DROP
        user_data = asset_data_hex[asset_data_offset:asset_data_offset+user_data_len*2]
        asset_data_offset += user_data_len*2

    # Create the asset object
    asset = {
        "name": asset_name,
        "amount": asset_amount,
        "units": asset_units,
        "reissuable": asset_reissuable,
        "hasIPFS": hasIPFS
    }

    return asset, asset_data_offset

def decode_asset_script(asm):
    asset_script_hex = asm[asm.index("OP_EVR_ASSET") + 1]
    script_offset = 0
    # The first byte(s) indicate the length of the asset data
    # Option a: # of bytes not counting OP_DROP if #<75
    # Option b: 0x4c +# of bytes not counting OP_DROP if #>75
    # Check for 0x4c in the first two bytes
    if asset_script_hex[:2] == b'\x4c':
        # Option b: 0x4c +# of bytes not counting OP_DROP if #>75
        # Script is larger than 75 bytes
        length = int(asset_script_hex[2:4], 16)
    else:
        # Option a: # of bytes not counting OP_DROP if #<75
        # Script is 75 bytes or less
        length = int(asset_script_hex[:2], 16)
    
    # Now get the asset data
    asset_data_hex = asset_script_hex[2:length*2+2]
    asset_data_offset = 0
    # Next extract the asset type
    # Extract asset script type and determine the type of script
    asset_header = bytes.fromhex(asset_data_hex[:6])
    asset_data_offset += 6
    # Decode the asset header
    asset_header_ascii = asset_header.decode('utf-8')
    # The asset header MUST start with "evr"
    if not asset_header_ascii.startswith("evr"):
        raise ValueError("Invalid Evrmore asset header")
    
    # Determine the type of asset script
    asset_type = asset_data_hex[asset_data_offset:asset_data_offset+2]
    asset_data_offset += 2
    asset_type_ascii = chr(int(asset_type, 16)) 
    if asset_type_ascii == "q":
        script_type = "new_asset"
    elif asset_type_ascii == "t":
        script_type = "transfer_asset"
    elif asset_type_ascii == "o":
        script_type = "ownership_asset"
    elif asset_type_ascii == "r":
        script_type = "reissue_asset"
    else:
        raise ValueError("Invalid Evrmore asset type")
    
    # We have to decode the asset name differently depending on the script type
    if script_type == "new_asset":
        asset, asset_data_offset = decode_new_asset_script(asset_data_hex, asset_data_offset)
    elif script_type == "transfer_asset":
        asset, asset_data_offset = decode_transfer_asset_script(asset_data_hex, asset_data_offset)
    elif script_type == "reissue_asset":
        asset, asset_data_offset = decode_reissue_asset_script(asset_data_hex, asset_data_offset)
    

    asset['type'] = script_type

    return asset

def decodescript(script_hex, is_script_sig=False):
    print("DeCodingDScript")
    print(script_hex)
    """Decode a script hex into a JSON object."""

    opcodes = {
        "76": "OP_DUP",
        "a9": "OP_HASH160",
        "88": "OP_EQUALVERIFY",
        "ac": "OP_CHECKSIG",
        "6a": "OP_RETURN",
        "87": "OP_EQUAL",
        "c0": "OP_EVR_ASSET"
    }
    
    script_bytes = bytes.fromhex(script_hex)
    offset = 0
    asm = []
    addresses = []
    req_sigs = 1  # Default for P2PKH
    script_type = "nonstandard"
    asset = None


    while offset < len(script_bytes):
        byte = script_bytes[offset]
        
        offset += 1

        hex_byte = f"{byte:02x}"

        
        if hex_byte in opcodes:
            asm.append(opcodes[hex_byte])
        elif hex_byte == "75":
            pass
        elif 1 <= byte <= 75:
            length = byte
            pushed_data = script_bytes[offset:offset + length]
            if len(asm) > 0 and asm[-1] == "OP_EVR_ASSET":
                pushed_data = script_bytes[offset-1:offset + length+1]
            asm.append(pushed_data.hex())
            offset += length


    result = {
        "asm": " ".join(asm),
    }
    if "OP_RETURN" in asm:
        script_type = "nulldata"
    elif "OP_DUP" in asm and "OP_HASH160" in asm and "OP_EQUALVERIFY" in asm and "OP_CHECKSIG" in asm:
        script_type = "pubkeyhash"
        address_hash = asm[asm.index("OP_HASH160") + 1]
        addresses.append(hash160_to_address(bytes.fromhex(address_hash)))
    elif "OP_HASH160" in asm and "OP_EQUAL" in asm:
        script_type = "scripthash"
        address_hash = asm[asm.index("OP_HASH160") + 1]
        addresses.append(hash160_to_address(bytes.fromhex(address_hash), prefix=b'\x5c'))
        p2sh_address = script_to_p2sh(script_hex)

    print(script_type)
    # Decode the asset script if present
    if "OP_EVR_ASSET" in asm:
        asset = decode_asset_script(asm)
        script_type = asset["type"]
        asset_name = asset["name"]
        amount = asset["amount"]
        reissuable = asset["reissuable"] == 1
    

    
    if not is_script_sig:
        result["type"] = script_type
        p2sh_address = script_to_p2sh(script_hex)
        if not script_type == "scripthash":
            result["p2sh"] = p2sh_address
    if is_script_sig and script_type == "nonstandard" and script_hex[0:2] not in opcodes:
        result["asm"] = script_hex[2:].replace("0121", "[ALL] ")
    if script_type in ["pubkeyhash", "scripthash", "transfer_asset", "new_asset", "reissue_asset"]:
        result["reqSigs"] = req_sigs
        result["addresses"] = addresses

    if asset:
        result["asset"] = asset
        result["addresses"] = addresses
        result["hasIPFS"] = asset["hasIPFS"]
        result["amount"] = amount
        if "units" in asset:
            result["units"] = asset["units"]
        result["reissuable"] = reissuable
        result["asset_name"] = asset_name    
        del result["asset"]["hasIPFS"]
        del result["asset"]["type"]

    if script_type == "transfer_asset":
        del result["asset"]["reissuable"]
        del result["asset"]["units"]
        del result["hasIPFS"]
        del result["units"]
        del result["reissuable"]

    if script_type == "reissue_asset":
        result["new_ipfs_hash"] = asset["ipfs_hash"]
        del result["hasIPFS"]

    return result


if __name__ == "__main__":
    import json
    print(json.dumps(decodescript("76a9146f00b7b316eacccb25e5840e8c4bdcaa8c07ac0888acc01a657672710a4d414e5449464f52474500e1f5050000000000010075"), indent=4))
