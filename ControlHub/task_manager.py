import threading
import time


class TaskManager(threading.Thread):
    # When the server receives TaskManager

    def __init__(self, task_q, outgoing_mbox):
        threading.Thread.__init__(self)
        self.task_queue = task_q
        self.outgoing_mailbox = outgoing_mbox
        self.run_task_switch = True       # Switch variable to pause/resume tasks
        self.state_manager = None
        self.mqtt_publisher = None
        self.background_go_flag = True
        self.last_run_time = time.ctime()

    def get_state_manager(self, sm):
        self.state_manager = sm

    def get_mqtt_publisher(self, mp):
        self.mqtt_publisher = mp

    # -- TASK HANDLER --------------------------------------------------------------------------------------------------
    def device_register_request_task(self, message):
        print("[TASK MANAGER] REGISTER MESSAGE RECEIVED.")
        self.state_manager.add_new_device(message.data["device_type"], message.data["device_id"], message.data["ip"])

    def device_deregister_request_task(self, message):
        print("[TASK MANAGER] DEREGISTER MESSAGE RECEIVED.")
        did = message.data["device_id"]
        outgoing_message = ["{\"message_type\":\"deregi\",\"device_ip\":\"" + self.state_manager.get_ip_address_by_device_id(did) + "\", \"device_id\":\""+did+"\"}"]
        self.outgoing_mailbox.put(message.address, outgoing_message)

    def all_device_deregister_request_task(self, message):
        print("[TASK MANAGER] DEREGISTER MESSAGE RECEIVED.")
        outgoing_messages = []
        all_ip_addresses = self.state_manager.get_all_ip_addresses()
        if len(all_ip_addresses) != 0:
            for a in all_ip_addresses:
                outgoing_messages.append("{\"message_type\":\"deregi\",\"device_ip\":\"" + a[1] + "\", \"device_id\":\""+a[0]+"\"}")
            self.outgoing_mailbox.put(message.address, outgoing_messages)

    def arm_request_task(self, message):
        print("[TASK MANAGER] SINGLE DEVICE ARM REQUEST MESSAGE RECEIVED.")
        did = message.data["device_id"]
        outgoing_message = ["{\"message_type\":\"arm\",\"device_ip\":\"" + self.state_manager.get_ip_address_by_device_id(did) + "\", \"device_id\":\""+did+"\"}"]
        self.outgoing_mailbox.put(message.address, outgoing_message)

    def disarm_request_task(self, message):
        print("[TASK MANAGER] SINGLE DEVICE DISARM REQUEST MESSAGE RECEIVED.")
        did = message.data["device_id"]
        outgoing_message = ["{\"message_type\":\"disarm\",\"device_ip\":\"" + self.state_manager.get_ip_address_by_device_id(did) + "\", \"device_id\":\""+did+"\"}"]
        self.outgoing_mailbox.put(message.address, outgoing_message)

    def all_arm_request_task(self, message):
        print("[TASK MANAGER] ALL ARM REQUEST MESSAGE RECEIVED.")
        outgoing_messages = []
        all_ip_addresses = self.state_manager.get_all_ip_addresses()
        if len(all_ip_addresses) != 0:
            for a in all_ip_addresses:
                outgoing_messages.append("{\"message_type\":\"arm\",\"device_ip\":\"" + a[1] + "\", \"device_id\":\""+ a[0] +"\"}")
            self.outgoing_mailbox.put(message.address, outgoing_messages)

    def all_disarm_request_task(self, message):
        print("[TASK MANAGER] ALL DISARM REQUEST MESSAGE RECEIVED.")
        outgoing_messages = []
        all_ip_addresses = self.state_manager.get_all_ip_addresses()
        if len(all_ip_addresses) != 0:
            for a in all_ip_addresses:
                outgoing_messages.append("{\"message_type\":\"disarm\",\"device_ip\":\"" + a[1] + "\", \"device_id\":\""+a[0]+"\"}")
            self.outgoing_mailbox.put(message.address, outgoing_messages)

    def status_check_manual_request_task(self, message):
        print("[TASK MANAGER] SINGLE DEVICE STATUS CHECK REQUEST MESSAGE RECEIVED.")
        did = message.data["device_id"]
        outgoing_message = ["{\"message_type\":\"status\",\"device_ip\":\"" + self.state_manager.get_ip_address_by_device_id(did) + "\", \"device_id\":\"" + did + "\"}"]
        self.outgoing_mailbox.put(message.address, outgoing_message)

        # self.state_manager.add_new_device(message.data["device_id"])

    def all_device_status_check_manual_request_task(self, message):
        print("[TASK MANAGER] ALL DEVICE STATUS CHECK REQUEST MESSAGE RECEIVED.")
        outgoing_messages = []
        all_ip_addresses = self.state_manager.get_all_ip_addresses()
        if len(all_ip_addresses) != 0:
            for a in all_ip_addresses:
                outgoing_messages.append("{\"message_type\":\"status\",\"device_ip\":\"" + a[1] + "\", \"device_id\":\""+a[0]+"\"}")
            self.outgoing_mailbox.put(message.address, outgoing_messages)

    def periodic_status_check_request_task(self):
        print("[TASK MANAGER] PERIODIC STATUS CHECK")
        # self.state_manager.add_new_device(message.data["device_id"])
    # ------------------------------------------------------------------------------------------------------------------

    def pop_task_queue(self):
        if self.task_queue.length() > 0:
            new_task = self.task_queue.get()
            if new_task.task_type == 'register':
                self.device_register_request_task(new_task)
            elif new_task.task_type == 'deregister':
                self.device_deregister_request_task(new_task)
            elif new_task.task_type == 'all_deregister':
                self.all_device_deregister_request_task(new_task)
            elif new_task.task_type == 'arm_request_single':
                self.arm_request_task(new_task)
            elif new_task.task_type == 'disarm_request_single':
                self.disarm_request_task(new_task)
            elif new_task.task_type == 'arm_request_all':
                self.all_arm_request_task(new_task)
            elif new_task.task_type == 'disarm_request_all':
                self.all_disarm_request_task(new_task)
            elif new_task.task_type == 'scr_manual_single':
                self.status_check_manual_request_task(new_task)
            elif new_task.task_type == 'scr_manual_all':
                self.all_device_status_check_manual_request_task(new_task)
            print("Priority Level: ", new_task.priority, ", Time: ", new_task.timestamp, ", Mailbox Address: ", new_task.address, ", Data: ", new_task.data)
            self.last_run_time = time.ctime()
            self.background_go_flag = True
        else:
            # Run background tasks once
            if self.background_go_flag == True:
                print("TASK MANAGER - BACKGROUND TASK")
                self.state_manager.update_json_file()
                self.background_go_flag = False

    def pause(self):
        self.run_task_switch = False
        print("[TaskManager]: Run Task Switch = ", self.run_task_switch)

    def resume(self):
        self.run_task_switch = True
        print("[TaskManager]: Run Task Switch = ", self.run_task_switch)

    def run(self):
        while(True):
            if self.run_task_switch:
                self.pop_task_queue()


