from flask import Flask, jsonify
import redis
import os

app = Flask(__name__)

# Connect to Redis using env vars from docker-compose.yml
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))
r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to DubeBox 🚀", "status": "running"})

@app.route('/set/<key>/<value>')
def set_value(key, value):
    r.set(key, value)
    return jsonify({"message": f"Stored {key} → {value} in Redis"})

@app.route('/get/<key>')
def get_value(key):
    value = r.get(key)
    return jsonify({"key": key, "value": value})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
