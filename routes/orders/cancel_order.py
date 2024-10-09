from flask import jsonify, request
from startup import app
from database import remove_order
from utils import get_data_from_redis


@app.route("/cancel_order", methods=['POST'])
def cancel_order():
    """
    Cancel an order by order ID.
    """
    if request.content_type != 'application/json':
        return jsonify({"error": "Content-Type must be application/json"}), 415
    
    data = request.json
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400
    
    order_id = data.get('order_id')
    if not order_id:
        return jsonify({"error": "Order ID is required"}), 400
    
    # Get the order from Redis
    order = get_data_from_redis(f"order:{order_id}")
    if not order:
        return jsonify({"error": "Order not found"}), 404

    # Remove the order from Redis
    remove_order(order_id)
    
    return jsonify({"message": "Order canceled successfully"}), 200