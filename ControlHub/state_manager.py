import threading
import time
import json

##########################################################
#   State Manager
#
#   Device Types: "Camera", "PIRSensor", "DoorLock"
system_status_file_path = "./system_current_status.json"


class StateManager(threading.Thread):
    # StateManager stores current status of the system

    def __init__(self, server_queue, task_manager):
        threading.Thread.__init__(self)
        self.server_queue = server_queue
        self.tm = task_manager
        self.devices_list = []
        self.status_json = {}

        try:
            with open(system_status_file_path, "r") as read_file:
                try:
                    json_data = json.load(read_file)
                    print(json_data)
                    self.restore_devices_from_saved_file(json_data)
                except:
                    print("json file corrupted")
        except:
            with open(system_status_file_path, "w") as read_file:
                print("New 'system_current_status.json' file created")

    def run(self):
        print("[StateManager]: Type 'P' to pause / Type 'R' to resume")
        while (True):
            a = input()
            if a == "R":
                self.tm.resume()
                print("[StateManager]: R", self.tm.run_task_switch)
            if a == "P":
                self.tm.pause()
                print("[StateManager]: P", self.tm.run_task_switch)

            time.sleep(0.1)

    def restore_devices_from_saved_file(self, saved_data):
        for each in saved_data['devices']:
            self.add_new_device(each['device_type'], each['device_id'], each['device_ip'])

    def add_new_device(self, device_type, device_id, device_ip):
        if device_type == "DoorLock":
            self.devices_list.append(DoorLock(device_id, device_ip))
        elif device_type == "Camera":
            self.devices_list.append(Sensor(device_id, device_ip, "Camera"))
        elif device_type == "PIRSensor":
            self.devices_list.append(Sensor(device_id, device_ip, "PIRSensor"))

        json_data = {}

        with open(system_status_file_path, 'r') as file_read:
            try:
                json_data = json.load(file_read)
            except:
                print("JSON file is empty or corrupted.")
        try:
            json_data['devices'].append({
                "device_type": device_type,
                "device_id": device_id,
                "device_ip": device_ip
            })
        except:
            json_data['devices'] = []
            json_data['devices'].append({
                "device_type": device_type,
                "device_id": device_id,
                "device_ip": device_ip
            })

        with open(system_status_file_path, 'w') as file_write:
            json.dump(json_data, file_write)

    def remove_device(self, target_device_id):
        for each_device in self.devices_list:
            if each_device.device_id == target_device_id:
                self.devices_list.remove(each_device)


class Sensor:
    # 'device_id' = Each device should have a unique ID from product line.
    def __init__(self, device_id, device_ip, sensor_type):
        self.sensor_id = device_id
        self.sensor_ip = device_ip
        self.sensor_type = sensor_type
        self.power = None
        self.last_status_update_time = None
        self.up_time = None
        self.armed = None

    def update_status(self, power, last_status_update_time, up_time, armed):
        self.power = power
        self.last_status_update_time = last_status_update_time
        self.up_time = up_time
        self.armed = armed


class DoorLock:
    def __init__(self, device_id, device_ip):
        self.sensor_id = device_id
        self.sensor_ip = device_ip
        self.power = None
        self.last_status_update_time = None
        self.up_time = None
        self.locked = None

    def update_status(self, power, last_status_update_time, up_time, locked):
        self.power = power
        self.last_status_update_time = last_status_update_time
        self.up_time = up_time
        self.locked = locked

