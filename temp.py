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

# refill tokens for a client based on the time passed since the last refill
def refill_tokens(client_id, current_tokens, last_refill_time, limit, refill_rate=5):
    current_time = time.time()
    elapse_time = current_time - last_refill_time
    new_tokens = int(elapse_time // refill_rate)

    if new_tokens > 0:
        # make sure tokens doens't exceed bucket limit
        new_total = min(current_tokens + new_tokens, limit)
        # set timestamp = current time
        redis_client.hset(client_id, mapping={"tokens": new_total, "timestamp": current_time})
        return new_total
    
    return current_tokens


@app.route('/check_limit', methods=['GET'])
def check_limit():
    client_id = request.headers.get('x-ms-clientId')
    if not client_id:
        return jsonify({'error': 'Client ID required'}), 400
    
    limit = 10 # max quota of each client

    token_data = redis_client.hgetall(client_id)
    if not token_data: # new client
        tokens = limit
        last_refill_time = time.time()
        redis_client.hset(client_id, mapping={"tokens": tokens, "timestamp": last_refill_time})
    else:
        # redis stores data as byte-string
        tokens = int(token_data[b'tokens'])
        last_refill_time = float(token_data[b'timestamp'])
        tokens = refill_tokens(client_id, tokens, last_refill_time, limit)

    # consume a token for the request
    if tokens > 0:
        new_tokens = tokens - 1
        redis_client.hset(client_id, "tokens", new_tokens)
        return jsonify({'allowed': True, 'quota_left': new_tokens}), 200
    else:
        return jsonify({'allowed': False, 'quota_left': 0}), 429
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
