from startup import app
from flask import jsonify
from utils import get_data_from_redis
@app.route("/orderbook/<symbol>", methods=["GET"])
def get_orderbook(symbol):
    orderbook = get_data_from_redis(f"orderbook:{symbol}")
    return jsonify({"orderbook": orderbook}), 200

