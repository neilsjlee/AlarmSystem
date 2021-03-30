from flask import Flask, request, jsonify
import time
import json


# Server receives HTTP requests from Mobile App or Sensors and transfers the requests to TaskManager.
# Each type of requests should have priority level,
# so that TaskManager can process higher priority tasks faster than lower priority tasks.


task_queue_handler = None
outgoing_mailbox_handler = None
mqtt_publisher = None

server = Flask(__name__)

MAX_BUFFER_SIZE = 100


# '/register': Sensors should send Register request to this URI
# Data should contain the sensor's type(e.g. Camera, IR Sensor)
@server.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    push_task_queue('register', 5, time.ctime(), request.remote_addr, data)
    return jsonify(data)


@server.route('/deregister', methods=['POST'])
def deregister():
    data = request.get_json()
    push_task_queue('deregister', 5, time.ctime(), request.remote_addr, data)
    return jsonify(data)


# '/alert': Sensors should send "Alert" message to this URI
@server.route('/alert', methods=['POST'])
def alert():
    # ALERT MESSAGE RECEIVED.
    # Alert message does not go into task queue.
    # The server thread handles the alert by itself right away.
    print("Alert received")
    data = request.get_json()
    print("{\"message_type\":\"alert\",\"device_id\":\"", data['device_id'], "\"}")
    mqtt_publisher.publish_message("{\"message_type\":\"alert\",\"device_id\":\""+data['device_id']+"\"}")
    return jsonify(data)


@server.route('/current_status', methods=['GET'])
def current_status():
    with open("./system_current_status.json", 'r') as most_recent_status:
        try:
            json_data = json.load(most_recent_status)
            print("AAAAA:", json_data)
            return jsonify(json_data)
        except:
            return ""


@server.route('/scr_manual_single', methods=['POST'])
def scr_manual_single():
    data = request.get_json()
    push_task_queue('scr_manual_single', 3, time.ctime(), request.remote_addr, data)
    return jsonify(data)


def run_server():
    print("Start Server")
    server.run(host='0.0.0.0', port=2002)


def get_task_queue(task_q):
    global task_queue_handler
    task_queue_handler = task_q


def get_outgoing_mailbox(om):
    global outgoing_mailbox_handler
    outgoing_mailbox_handler = om


def get_mqtt_publisher(mqtt_p):
    global mqtt_publisher
    mqtt_publisher = mqtt_p


def push_task_queue(arg1, arg2, arg3, arg4, arg5):
    task_queue_handler.put(arg1, arg2, arg3, arg4, arg5)


class ReceivedRequest:
    def __init__(self, uri, priority, timestamp, address, data):
        self.uri = uri
        self.priority = priority
        self.timestamp = timestamp
        self.address = address
        self.data = data

    def __lt__(self, other):
        return self.priority < other.priority



