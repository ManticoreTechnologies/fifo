from flask import request, jsonify
from startup import app
from utils import get_data_from_redis
from database import register_address as register_address_on_database
from rpc import authenticate_message


@app.route("/register_address", methods=["POST"])
def register_address():
    data = request.json
    address = data.get("address")
    signature = data.get("signature")
    if not address or not signature:
        return jsonify({"error": "Address and signature are required"}), 400

    # Authenticate the message
    authenticated = authenticate_message(address, signature, "register_address")
    if not authenticated:
        return jsonify({"error": "Invalid signature"}), 401


    account = get_data_from_redis(f"address:{address}")
    print(account)
    if account:
        return jsonify({"error": "Address already registered"}), 400
    

    
    new_address = register_address_on_database(address)
    
    return jsonify({"address": new_address}), 200

