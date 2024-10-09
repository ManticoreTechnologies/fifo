from flask import jsonify, request
from startup import app
from database import get_order as get_order_from_database

@app.route("/get_order", methods=['POST'])
def get_order():
    """
    Get an order by order ID.
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
    order = get_order_from_database(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    
    return jsonify({"order": order}), 200
