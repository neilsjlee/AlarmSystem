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
        for each in saved_data['devices']:
            self.add_new_device(each['device_type'], each['device_id'], each['device_ip'])

    def add_new_device(self, device_type, device_id, device_ip):
        self.devices_list_json[device_id] = {"device_type": device_type,
                                             "device_id": device_id,
                                             "device_ip": device_ip,
                                             "device_power": True,
                                             "last_status_update_time": time.ctime(),
                                             "up_time": time.ctime(),
                                             "armed": False
                                             }
        '''
        self.devices_list_json.append({device_id: {"device_type": device_type,
                                                   "device_id": device_id,
                                                   "device_ip": device_ip,
                                                   "device_power": True,
                                                   "last_status_update_time": time.ctime(),
                                                   "up_time": time.ctime(),
                                                   "armed": False
                                                   }})
        '''
        self.update_json_file()

    def remove_device(self, target_device_id):
        del self.devices_list_json[target_device_id]
        self.update_json_file()

    def get_ip_address_by_device_id(self, did):
        # print("get_ip_address_by_device_id", self.devices_list_json[did]['device_ip'])
        return self.devices_list_json[did]['device_ip']

    def update_json_file(self):
        with open(system_status_file_path, 'w') as file_write:
            json.dump(self.devices_list_json, file_write)
