from startup import app
from database import purge_redis
from flask import jsonify

@app.route("/purge_database", methods=["POST"])
def purge_database():
    """
    Purge the database.
    """
    purge_redis()
    return jsonify({"message": "Database purged"}), 200