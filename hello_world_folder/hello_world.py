from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# get the service name and port from environment
RATE_LIMITER_SERVICE_URL = (
    f"http://{os.environ['RATE_LIMITER_SERVICE_HOST']}:"
    f"{os.environ['RATE_LIMITER_SERVICE_PORT']}/check_limit"
)

@app.route('/helloworld', methods=['GET'])
def hello_world():
    client_id = request.headers.get('x-ms-clientId')
    if not client_id:
        return jsonify({'error': 'Client ID required'}), 400
    
    response = requests.get(RATE_LIMITER_SERVICE_URL, headers={'x-ms-clientId': client_id})
    
    if response.status_code == 429:
        return jsonify({'error': 'Rate limit exceeded'}), 429
    
    data = response.json()
    return jsonify({'message': 'Hello World', 'quota_left': data.get('quota_left', 0)}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
