import threading
import time
import json

##########################################################
#   State Manager
#
#   Device Types: "Camera", "PIRSensor", "DoorLock"
system_status_file_path = "./system_current_status.json"


class StateManager:
    # StateManager stores current status of the system

    def __init__(self, server_queue, task_manager):
        self.server_queue = server_queue
        self.tm = task_manager
        self.devices_list_json = {}
        self.lock = threading.Lock()

        try:
            with open(system_status_file_path, "r") as read_file:
                try:
                    self.devices_list_json = json.load(read_file)
                    print(self.devices_list_json)
                except:
                    print("json file corrupted")
        except:
            with open(system_status_file_path, "w") as read_file:
                print("New 'system_current_status.json' file created")

    def restore_devices_from_saved_file(self, saved_data):
        self.p()
        for each in saved_data['devices']:
            self.add_new_device(each['device_type'], each['device_id'], each['device_ip'])
        self.v()

    def add_new_device(self, device_type, device_id, device_ip):
        self.p()
        self.devices_list_json[device_id] = {"device_type": device_type,
                                             "device_id": device_id,
                                             "device_ip": device_ip,
                                             "device_power": True,
                                             "last_status_update_time": time.ctime(),
                                             "up_time": time.ctime(),
                                             "armed": False
                                             }
        # self.update_json_file()
        self.v()

    def remove_device(self, target_device_id):
        self.p()
        ip = self.devices_list_json[target_device_id]['device_ip']
        del self.devices_list_json[target_device_id]
        # self.update_json_file()
        self.v()
        return ip

    def get_ip_address_by_device_id(self, did):
        self.p()
        temp = self.devices_list_json[did]['device_ip']
        self.v()
        return temp

    def get_all_ip_addresses(self):
        self.p()
        temp = []
        for each in self.devices_list_json:
            temp.append(self.devices_list_json[each]['device_ip'])
        print("get_all_ip_addresses: ", temp)
        self.v()
        return temp

    def update_state_for_a_device(self, did, data):
        self.p()
        self.devices_list_json[did] = json(data)
        self.v()

    def update_json_file(self):
        with open(system_status_file_path, 'w') as file_write:
            json.dump(self.devices_list_json, file_write)

    def p(self):
        self.lock.acquire()

    def v(self):
        self.lock.release()
