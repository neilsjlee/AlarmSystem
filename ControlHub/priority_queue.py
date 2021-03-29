# Implementing Priority Queue using List data type

import copy


class MyPriorityQueue:
    def __init__(self):
        self.queue_list = []
        self.queue_size = 0

    def put(self, task_type, priority, timestamp, address, data):
        i = 0
        found_the_right_place = False
        current_queue_size = len(self.queue_list)
        if current_queue_size > 0:
            while (not found_the_right_place) and i < current_queue_size:
                if self.queue_list[i].priority > priority:
                    found_the_right_place = True
                else:
                    i = i + 1
            self.queue_list.insert(i, QueueTask(task_type, priority, timestamp, address, data))
        else:
            self.queue_list.append(QueueTask(task_type, priority, timestamp, address, data))
        self.queue_size = self.queue_size + 1

    def get(self):
        if len(self.queue_list) > 0:
            first_item = self.queue_list[0]
            self.queue_list.pop(0)
            self.queue_size = self.queue_size - 1
            return first_item

    def length(self):
        return self.queue_size


class QueueTask:
    def __init__(self, task_type, priority, timestamp, address, data):
        self.task_type = task_type
        self.priority = priority
        self.timestamp = timestamp
        self.address = address
        self.data = data