from flask import Flask, request, jsonify
from queue import PriorityQueue
import time
import json
import requests

# Server receives HTTP requests from Mobile App or Sensors and transfers the requests to TaskManager.
# Each type of requests should have priority level, so that TaskManager can process higher priority tasks faster than lower priority tasks.


server_queue = PriorityQueue()

server = Flask(__name__)


# '/register': Sensors should send Register request to this URI
# Data should contain the sensor's type(e.g. Camera, IR Sensor)
@server.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    server_queue.put(ReceivedRequest('register', 5, time.time(), request.remote_addr, data))
    return jsonify(data)


# '/alert': Sensors should send "Alert" message to this URI
@server.route('/alert', methods=['POST'])
def alert():
    data = request.get_json()
    server_queue.put(ReceivedRequest('alert', 1, time.time(), request.remote_addr, data))
    return jsonify(data)


@server.route('/current_status', methods=['GET'])
def current_status():
    with open("./system_current_status.json", 'r') as most_recent_status:
        json_data = json.load(most_recent_status)
        print("AAAAA:", json_data)
        return json_data


def run_server():
    print("Start Server")
    server.run(host='0.0.0.0', port=2002)


class ReceivedRequest:
    def __init__(self, uri, priority, timestamp, address, data):
        self.uri = uri
        self.priority = priority
        self.timestamp = timestamp
        self.address = address
        self.data = data

    def __lt__(self, other):
        return self.priority < other.priority


