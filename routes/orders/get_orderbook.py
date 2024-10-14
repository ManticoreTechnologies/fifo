from startup import app
from flask import jsonify
from utils import get_data_from_redis
from database import get_orderbook as get_orderbook_from_db

# Redis structure:
# orderbook:
# {
#   "symbol": {
#     "bids": {
#       "price": {
#         "order_id": order
#       }
#     },
#     "asks": {


@app.route("/orderbook", methods=["GET"])
def get_orderbook():
    orderbook = get_orderbook_from_db()
    if orderbook is None:
        return jsonify({"error": "Orderbook not found"}), 404
    return jsonify(orderbook), 200

@app.route("/orderbook/<symbol>", methods=["GET"])
def get_orderbook_by_symbol(symbol):
    orderbook = get_orderbook_from_db()
    if orderbook is None:
        return jsonify({"error": "Orderbook not found"}), 404
    if symbol not in orderbook:
        return jsonify({"error": "Symbol not found in orderbook"}), 404
    return jsonify(orderbook[symbol]), 200

