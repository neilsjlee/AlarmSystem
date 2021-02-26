import threading
import time


class StateManager(threading.Thread):
    # StateManager stores current status of the system

    def __init__(self, server_queue, task_manager):
        threading.Thread.__init__(self)
        self.server_queue = server_queue
        self.tm = task_manager

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