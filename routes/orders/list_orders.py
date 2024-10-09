from flask import jsonify, request
from startup import app
from database import list_orders as list_orders_from_db
from utils import validate_data
from rpc import authenticate_message

@app.route("/list_orders", methods=['GET'])
def list_orders():
    """
    List all orders.
    """

    data = request.json
    validate_data(data)

    address = data.get("address")
    signature = data.get("signature")

    if not address or not signature:
        return jsonify({"error": "Invalid address or signature"}), 400

    # Authenticate the message
    authenticated = authenticate_message(address, signature, "list_orders")

    if not authenticated:
        return jsonify({"error": "Invalid signature"}), 401


    return jsonify({"orders": list_orders_from_db(address)}), 200