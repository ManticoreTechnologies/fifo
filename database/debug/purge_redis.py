import redis
from flask import jsonify

def purge_redis():
    redis_client = redis.Redis(host="localhost", port=6379, db=0)
    redis_client.flushall()
    return jsonify({"message": "Redis database purged"}), 200   