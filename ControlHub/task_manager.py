import threading
import time


class TaskManager(threading.Thread):
    # When the server receives TaskManager

    def __init__(self, task_q):
        threading.Thread.__init__(self)
        self.task_queue = task_q
        self.run_task_switch = True       # Switch variable to pause/resume tasks
        self.state_manager = None
        self.mqtt_publisher = None

    def get_state_manager(self, sm):
        self.state_manager = sm

    def get_mqtt_publisher(self, mp):
        self.mqtt_publisher = mp

    # -- TASK HANDLER --------------------------------------------------------------------------------------------------
    def device_register_request_task(self, message):
        print("[TASK MANAGER] REGISTER MESSAGE RECEIVED.")
        self.state_manager.add_new_device(message.data["device_type"], message.data["device_id"], message.address)

    def device_deregister_request_task(self, message):
        print("[TASK MANAGER] DEREGISTER MESSAGE RECEIVED.")
        is_error = False
        try:
            self.state_manager.remove_device(message.data["device_id"])
        except:
            print("no_proper_key")
            is_error = True
        # Need to send deregister request to the device as well
        if is_error == False:
            self.mqtt_publisher.publish_message("ack")
        else:
            self.mqtt_publisher.publish_message("nack")

    def arm_request_task(self, message):
        print("[TASK MANAGER] SINGLE DEVICE ARM REQUEST MESSAGE RECEIVED.")
        # self.state_manager.add_new_device(message.data["device_id"])

    def disarm_request_task(self, message):
        print("[TASK MANAGER] SINGLE DEVICE DISARM REQUEST MESSAGE RECEIVED.")
        # self.state_manager.add_new_device(message.data["device_id"])

    def all_arm_request_task(self, message):
        print("[TASK MANAGER] ALL ARM REQUEST MESSAGE RECEIVED.")

    def all_disarm_request_task(self, message):
        print("[TASK MANAGER] ALL DISARM REQUEST MESSAGE RECEIVED.")

    def status_check_manual_request_task(self, message):
        print("[TASK MANAGER] SINGLE DEVICE STATUS CHECK REQUEST MESSAGE RECEIVED.")
        self.state_manager.get_ip_address_by_device_id(message.data["device_id"])
        # self.state_manager.add_new_device(message.data["device_id"])

    def all_device_status_check_manual_request_task(self, message):
        print("[TASK MANAGER] ALL DEVICE STATUS CHECK REQUEST MESSAGE RECEIVED.")
        # self.state_manager.add_new_device(message.data["device_id"])

    def periodic_status_check_request_task(self):
        print("[TASK MANAGER] PERIODIC STATUS CHECK")
        # self.state_manager.add_new_device(message.data["device_id"])

    def alert_message_task(self, message):
        print("[TASK MANAGER] ALERT MESSAGE RECEIVED.")
        # self.state_manager.add_new_device(message.data["device_id"])

    def buzzer_off_request_task(self):
        print("[TASK MANAGER] BUZZER OFF REQUEST RECEIVED.")
        # self.state_manager.add_new_device(message.data["device_id"])
    # ------------------------------------------------------------------------------------------------------------------

    def pop_server_queue(self):
        if self.task_queue.length() > 0:
            received_message = self.task_queue.get()
            if received_message.task_type == 'register':
                self.device_register_request_task(received_message)
            elif received_message.task_type == 'scr_manual_single':
                self.status_check_manual_request_task(received_message)
            elif received_message.task_type == 'deregister':
                self.device_deregister_request_task(received_message)
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

