from flask import Flask, jsonify
from Market import Market
from Database import Database

app = Flask(__name__)

# Initialize the market and load orders from the database
symbol = "BTCUSDT"
market = Market(symbol)
market.load_orders()  # Ensure orders are loaded from the database

@app.route('/orderbook', methods=['GET'])
def get_orderbook():
    # Retrieve the order book from the market
    order_book = market.get_order_book()
    return jsonify(order_book)

if __name__ == '__main__':
    app.run(debug=True)
