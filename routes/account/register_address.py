from startup import app
from flask import request, jsonify
from rpc import authenticate_message
from utils import get_data_from_redis
from database import register_address as register_address_on_database

@app.route("/register_address", methods=["POST"])
def register_address():

    # Get the data from the request
    data = request.json

    # Get the address and signature from the data
    address = data.get("address")
    signature = data.get("signature")

    # TODO: Validate the address

    # If the address or signature is not provided, return an error
    if not address or not signature:
        return jsonify({"error": "Address and signature are required"}), 400

    # Authenticate the message
    authenticated = authenticate_message(address, signature, "register_address")
    if not authenticated:
        return jsonify({"error": "Invalid signature"}), 401

    # Get the account from Redis, keyed by the address
    account = get_data_from_redis(f"account:{address}")

    # If the account is not None, return an error
    if account:
        return jsonify({"error": "Address already registered"}), 400
    
    # Register the address on the database
    new_account = register_address_on_database(address)
    
    # Return the new account
    return jsonify(new_account), 200

