import threading
import time


class TaskManager(threading.Thread):
    # When the server receives TaskManager

    def __init__(self, server_queue):
        threading.Thread.__init__(self)
        self.server_q = server_queue
        self.run_task_switch = False       # Switch variable to pause/resume tasks
        self.state_manager = None

    def get_state_manager(self, sm):
        self.state_manager = sm

    ### TASK HANDLER ###################################################################################################
    def device_register_request(self, message):
        print("[TASK MANAGER] REGISTER MESSAGE RECEIVED - ")
        self.state_manager.add_new_device(message.data["device_type"], message.data["device_id"], message.address)
        #start here

    def device_deregister_request(self, message):
        print("[TASK MANAGER] DEREGISTER MESSAGE RECEIVED - ")
        # self.state_manager.add_new_device(message.data["device_id"])

    def arm_request(self, message):
        print("[TASK MANAGER] SINGLE DEVICE ARM REQUEST MESSAGE RECEIVED - ")
        # self.state_manager.add_new_device(message.data["device_id"])

    def disarm_request(self, message):
        print("[TASK MANAGER] SINGLE DEVICE DISARM REQUEST MESSAGE RECEIVED - ")
        # self.state_manager.add_new_device(message.data["device_id"])

    def all_arm_request(self, message):
        print("[TASK MANAGER] ALL ARM REQUEST MESSAGE RECEIVED - ")

    def all_disarm_request(self, message):
        print("[TASK MANAGER] ALL DISARM REQUEST MESSAGE RECEIVED - ")

    def status_check_manual_request(self, message):
        print("[TASK MANAGER] SINGLE DEVICE STATUS CHECK REQUEST MESSAGE RECEIVED - ")
        # self.state_manager.add_new_device(message.data["device_id"])

    def all_device_status_check_manual_request(self, message):
        print("[TASK MANAGER] SINGLE DEVICE STATUS CHECK REQUEST MESSAGE RECEIVED - ")
        # self.state_manager.add_new_device(message.data["device_id"])
    ####################################################################################################################

    def pop_server_queue(self):
        received_message = self.server_q.get()
        if received_message.uri == 'register':
            self.device_register_request(received_message)
        print("Priority Level: ", received_message.priority, ", Time: ", received_message.timestamp, ", Sender: ", received_message.address, ", Data: ", received_message.data)

    def pause(self):
        self.run_task_switch = False
        print("[TaskManager]: Run Task Switch = ", self.run_task_switch)

    def resume(self):
        self.run_task_switch = True
        print("[TaskManager]: Run Task Switch = ", self.run_task_switch)

    def run(self):

        while(True):
            if self.run_task_switch:
                self.pop_server_queue()

            time.sleep(0.01)

