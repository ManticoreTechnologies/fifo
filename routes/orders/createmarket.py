from flask import jsonify, request
from Classes import Market
from startup import app

@app.route("/market/create", methods=["POST"])
def create_market():
    """
    Create a new market.
    """
    data = request.json
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    market = Market(data["symbol"])
    market.cancel_order(data["order_id"])
    return jsonify({"message": "Order canceled successfully"}), 200

@app.route("/market/<symbol>", methods=["GET"])
def get_market(symbol):
    """
    Get a market.
    """
    market = Market(symbol)
    return jsonify({"market": market}), 200

