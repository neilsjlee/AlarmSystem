from flask import Flask, request, jsonify, render_template, send_file, send_from_directory
import time
import json
import binascii
from speaker import *
import os
import datetime

# Server receives HTTP requests from Mobile App or Sensors and transfers the requests to TaskManager.
# Each type of requests should have priority level,
# so that TaskManager can process higher priority tasks faster than lower priority tasks.

task_queue_handler = None
outgoing_mailbox_handler = None
mqtt_publisher = None
speaker = Speaker()
speaker.start()

server = Flask(__name__)

MAX_BUFFER_SIZE = 100


def get_task_queue(task_q):
    global task_queue_handler
    task_queue_handler = task_q


def get_outgoing_mailbox(om):
    global outgoing_mailbox_handler
    outgoing_mailbox_handler = om


def get_mqtt_publisher(mqtt_p):
    global mqtt_publisher
    mqtt_publisher = mqtt_p


# '/alert': Sensors should send "Alert" message to this URI
@server.route('/alert', methods=['POST'])
def alert():
    time1 = datetime.datetime.now()
    # ALERT MESSAGE RECEIVED.
    # Alert message does not go into task queue.
    # The server thread handles the alert by itself right away.
    speaker.buzzer_on()
    time2 = datetime.datetime.now()
    data = request.get_json()
    mqtt_publisher.publish_message("{\"message_type\":\"alert\",\"device_id\":\""+data['device_id']+"\"}")
    time3 = datetime.datetime.now()
    print("Alert received")
    print(data)
    print("{\"message_type\":\"alert\",\"device_id\":\"", data['device_id'], "\"}")
    print("Alert - Speaker On - Time Taken: ", time2 - time1)
    print("Alert - MQTT Message - Time Taken: ", time3 - time1)
    return jsonify(data)


# '/alert': Sensors should send "Alert" message to this URI
@server.route('/buzzer_off', methods=['POST'])
def buzzer_off():
    time1 = datetime.datetime.now()
    # ALERT MESSAGE RECEIVED.
    # Alert message does not go into task queue.
    # The server thread handles the alert by itself right away.
    print("Buzzer Off received")
    speaker.buzzer_off()
    data = request.get_json()
    time2 = datetime.datetime.now()
    print("Buzzer Off Time Taken: ", time2 - time1)
    return jsonify(data)


# '/door_unlocked': Sensors should send "Alert" message to this URI
@server.route('/door_unlocked', methods=['POST'])
def door_unlocked():
    # ALERT MESSAGE RECEIVED.
    # Alert message does not go into task queue.
    # The server thread handles the alert by itself right away.
    print("Door Unlocked received")
    data = request.get_json()
    print(data)
    # print("{\"message_type\":\"alert\",\"device_id\":\"", data['device_id'], "\"}")
    mqtt_publisher.publish_message("{\"message_type\":\"door_unlocked\",\"device_id\":\""+data['device_id']+"\"}")
    return jsonify(data)


# '/door_locked': Sensors should send "Alert" message to this URI
@server.route('/door_locked', methods=['POST'])
def door_locked():
    # ALERT MESSAGE RECEIVED.
    # Alert message does not go into task queue.
    # The server thread handles the alert by itself right away.
    print("Door Locked received")
    data = request.get_json()
    print(data)
    # print("{\"message_type\":\"alert\",\"device_id\":\"", data['device_id'], "\"}")
    mqtt_publisher.publish_message("{\"message_type\":\"door_locked\",\"device_id\":\""+data['device_id']+"\"}")
    return jsonify(data)


# Returning the most recent status saved in double buffer to the mobile app.
#     - Main buffer is saved in StateManager().devices_list_json
#     - Secondary buffer is saved in "system_current_status.json" file
# This request is to promptly respond back to the mobile app only on the mobile app's loading phase.
@server.route('/current_status', methods=['GET'])
def current_status():
    with open("./system_current_status.json", 'r') as most_recent_status:
        try:
            json_data = json.load(most_recent_status)
            print("AAAAA:", json_data)
            return jsonify(json_data)
        except:
            return ""


# Register/Deregister Requests (Priority # 1)
@server.route('/register', methods=['POST'])
def register():
    print("REGISTER REQUEST: ", request)

    data = request.get_json()
    print("RECEIVED MESSAGE: ", data)
    push_task_queue('register', 1, time.ctime(), "no mailbox", data)
    return jsonify(data)


@server.route('/deregister', methods=['POST'])
def deregister():
    data = request.get_json()
    mailbox_address = outgoing_mailbox_handler.assign_new_mailbox_number()
    push_task_queue('deregister', 1, time.ctime(), mailbox_address, data)
    return "{\"mailbox_addr\":\""+str(mailbox_address)+"\"}"


@server.route('/all_deregister', methods=['POST'])
def all_deregister():
    data = request.get_json()
    mailbox_address = outgoing_mailbox_handler.assign_new_mailbox_number()
    push_task_queue('all_deregister', 1, time.ctime(), mailbox_address, data)
    return "{\"mailbox_addr\":\""+str(mailbox_address)+"\"}"


# Arm/Disarm Requests (Priority # 2)
@server.route('/arm_request_single', methods=['POST'])
def arm_request_single():
    data = request.get_json()
    mailbox_address = outgoing_mailbox_handler.assign_new_mailbox_number()
    push_task_queue('arm_request_single', 2, time.ctime(), mailbox_address, data)
    return "{\"mailbox_addr\":\""+str(mailbox_address)+"\"}"


@server.route('/disarm_request_single', methods=['POST'])
def disarm_request_single():
    data = request.get_json()
    mailbox_address = outgoing_mailbox_handler.assign_new_mailbox_number()
    push_task_queue('disarm_request_single', 2, time.ctime(), mailbox_address, data)
    return "{\"mailbox_addr\":\""+str(mailbox_address)+"\"}"


@server.route('/arm_request_all', methods=['POST'])
def arm_request_all():
    data = request.get_json()
    mailbox_address = outgoing_mailbox_handler.assign_new_mailbox_number()
    push_task_queue('arm_request_all', 2, time.ctime(), mailbox_address, data)
    return "{\"mailbox_addr\":\""+str(mailbox_address)+"\"}"


@server.route('/disarm_request_all', methods=['POST'])
def disarm_request_all():
    data = request.get_json()
    mailbox_address = outgoing_mailbox_handler.assign_new_mailbox_number()
    push_task_queue('disarm_request_all', 2, time.ctime(), mailbox_address, data)
    return "{\"mailbox_addr\":\""+str(mailbox_address)+"\"}"


# SCR(Status Check Requests) (Priority # 3)
@server.route('/scr_manual_single', methods=['POST'])
def scr_manual_single():
    data = request.get_json()
    mailbox_address = outgoing_mailbox_handler.assign_new_mailbox_number()
    push_task_queue('scr_manual_single', 3, time.ctime(), mailbox_address, data)
    return "{\"mailbox_addr\":\""+str(mailbox_address)+"\"}"


@server.route('/scr_manual_all', methods=['POST'])
def scr_manual_all():
    time1 = datetime.datetime.now()
    data = request.get_json()
    mailbox_address = outgoing_mailbox_handler.assign_new_mailbox_number()
    push_task_queue('scr_manual_all', 3, time.ctime(), mailbox_address, data)
    time2 = datetime.datetime.now()
    print("SCR_MANUAL ALL Time Taken: ", time2 - time1)
    return "{\"mailbox_addr\":\""+str(mailbox_address)+"\"}"


@server.route('/cam_photo', methods=['POST', 'GET'])
def cam_photo():
    script_dir = os.path.dirname(__file__)
    rel_path = "photo/img.jpg"
    abs_file_path = os.path.join(script_dir, rel_path)

    if request.method == 'POST':
        print("Receiving photo from Camera")
        hex_data = request.data
        # print("CAM_PHOTO_POST_REQUEST: ", hex_data)
        # bin_data = binascii.unhexlify(hex_data)
        jpeg_data = hex_data
        with open(abs_file_path, 'wb') as out_file:
            out_file.write(jpeg_data)
        return "{\"mailbox_addr\":\"0\"}"

    if request.method == 'GET':
        print("cam_photo GET request received")
        filepath = './photo'
        filename = 'img.jpg'
        return send_from_directory(filepath, filename, as_attachment=True)


# -----------------------------


def run_server():
    print("Start Server")
    server.run(host='0.0.0.0', port=2002)


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

