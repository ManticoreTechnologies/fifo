from startup import app
from flask import jsonify, request
from rpc import authenticate_message
from utils import get_data_from_redis


@app.route("/account", methods=["POST"])
def get_account():

    # Get the data from the request
    data = request.json

    # Get the address and signature from the data
    address = data.get("address")
    signature = data.get("signature")

    # TODO: Validate the address

    # Authenticate the signature TODO: Add a nonce to the message to prevent replay attacks
    authenticated = authenticate_message(address, signature, "account")

    # If the signature is not valid, return an error
    if not authenticated:
        return jsonify({"error": "Invalid signature"}), 401
    
    # Get the account from Redis, keyed by the address
    account = get_data_from_redis(f"account:{address}")

    # If the account is null or None, return an error
    if account is None:
        return jsonify({"error": "Address not registered"}), 404

    # Otherwise, return the account
    return jsonify(account)
