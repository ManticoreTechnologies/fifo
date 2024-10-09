from flask import jsonify, request
from startup import app
from database import save_order
from utils import validate_data
from rpc import authenticate_message
import uuid

@app.route("/place_order", methods=['POST'])
def place_order():

    # Get the data from the request
    data = request.json

    # Validate the data
    validate_data(data)

    # Separate the data
    address = data.get('address')
    symbol = data.get('symbol')
    side = data.get('side')
    price = data.get('price')
    quantity = data.get('quantity')
    signature = data.get('signature')

    # Authenticate the message
    authenticated = authenticate_message(address, signature, "place_order")

    if not authenticated:
        return jsonify({"error": "Invalid signature"}), 401

    # Create the order 
    order = {
        "order_id": str(uuid.uuid4()),
        "user_address": address,
        "symbol": symbol,
        "side": side,
        "price": price,
        "quantity": quantity
    }

    # Save the order to Redis
    save_order(order)

    # Return the order
    return jsonify({"message": "Order added to redis", "order": order}), 200


