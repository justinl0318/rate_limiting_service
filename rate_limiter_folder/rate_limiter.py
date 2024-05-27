from flask import Flask, request, jsonify
import redis
import os, time

app = Flask(__name__)

# Connect to Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# redis element structure: hashset
# client_id:
# 1. tokens: tokens
# 2. timestamp: timestamp

with open("token_bucket.lua", "r") as file:
    token_script = file.read()


@app.route('/check_limit', methods=['GET'])
def check_limit():
    client_id = request.headers.get('x-ms-clientId')
    if not client_id:
        return jsonify({'error': 'Client ID required'}), 400
    
    current_time = time.time()
    limit = 10 # max quota of each client
    refill_rate = 5 # refill 1 token per 5 seconds

    new_tokens = redis_client.eval(token_script, 1, client_id, current_time, refill_rate, limit)

    if new_tokens >= 0:
        return jsonify({'allowed': True, 'quota_left': new_tokens}), 200
    else:
        return jsonify({'allowed': False, 'quota_left': 0}), 429
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
