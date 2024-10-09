from flask import jsonify, request
from startup import app
from utils import get_data_from_redis
from rpc import authenticate_message
@app.route("/account", methods=["POST"])
def get_account():
    data = request.json
    address = data.get("address")
    signature = data.get("signature")
    authenticated = authenticate_message(address, signature, "account")
    if not authenticated:
        return jsonify({"error": "Invalid signature"}), 401
    
    account = get_data_from_redis(f"account:{address}")
    return jsonify(account)
