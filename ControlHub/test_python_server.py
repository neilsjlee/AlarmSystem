from flask import Flask, request, jsonify
from queue import PriorityQueue
import time


server_queue = PriorityQueue()

server = Flask(__name__)


@server.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    server_queue.put(ReceivedRequest(5, time.time(), request.remote_addr, data))
    return jsonify(data)


@server.route('/alert', methods=['POST'])
def alert():
    data = request.get_json()
    server_queue.put(ReceivedRequest(1, time.time(), request.remote_addr, data))
    return jsonify(data)


def run_server():
    print("Start Server")
    server.run(host='0.0.0.0', port=2002)


class ReceivedRequest:
    def __init__(self, priority, timestamp, address, data):
        self.priority = priority
        self.timestamp = timestamp
        self.address = address
        self.data = data

    def __lt__(self, other):
        return self.priority < other.priority


