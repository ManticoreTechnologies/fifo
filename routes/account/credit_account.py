from flask import jsonify, request
from startup import app
from utils import get_data_from_redis, save_data_to_redis
from rpc import authenticate_message

@app.route("/credit_account", methods=["POST"])
def credit_account():
    data = request.json
    address = data.get("address")
    signature = data.get("signature")
    asset_name = data.get("assetName")
    quantity = data.get("quantity")
    
    if not address or not signature or not asset_name or not quantity:
        return jsonify({"error": "Address, signature, assetName, and quantity are required"}), 400

    authenticated = authenticate_message(address, signature, "credit_account")
    if not authenticated:
        return jsonify({"error": "Invalid signature"}), 401
    
    account = get_data_from_redis(f"account:{address}")
    if not account:
        return jsonify({"error": "Account not found"}), 404
    
    if asset_name in account["balances"]:
        account["balances"][asset_name] += quantity
    else:
        account["balances"][asset_name] = quantity
    
    save_data_to_redis(f"account:{address}", account)
    
    return jsonify(account)
