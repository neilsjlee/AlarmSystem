import threading
import time


class TaskManager(threading.Thread):
    # When the server receives TaskManager

    def __init__(self, server_queue):
        threading.Thread.__init__(self)
        self.server_q = server_queue
        self.run_task_switch = False       # Switch variable to pause/resume tasks

    def pop_server_queue(self):
        received_message = self.server_q.get()
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
                if self.server_q.qsize() > 0:
                    self.pop_server_queue()

            time.sleep(0.01)

