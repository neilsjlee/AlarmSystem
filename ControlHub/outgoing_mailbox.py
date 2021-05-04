# Mailbox implementation for outgoing messages.
# Implemented using Ring Buffer

import threading

MAX_MAILBOX_SIZE = 128


class OutgoingMailbox:
    def __init__(self):
        self.head = 0
        self.tail = 0
        self.number_of_items = 0
        self.list = []
        self.lock = threading.Lock()
        self.init()

    def init(self):
        temp = 0
        while temp < MAX_MAILBOX_SIZE:
            self.list.append([])
            temp = temp + 1

    def assign_new_mailbox_number(self):
        self.p()
        self.head_go_next()
        while self.list[self.head] != []:
            # Overflow
            self.head_go_next()
        i_temp = self.head
        self.v()
        return i_temp

    def put(self, addr, items_list):
        self.p()
        self.list[addr] = items_list
        print("OutgoingMailbox.put(", items_list, ")")
        print(self.list)
        self.number_of_items = self.number_of_items + 1
        self.v()
        return

    def pull_next_outgoing_mailbox(self):
        self.p()
        self.tail_go_next()
        x = self.tail
        y = self.list[self.tail]
        print("OUTGOING_MAILBOX - PULL: ", x, y)
        self.list[self.tail] = []
        self.number_of_items = self.number_of_items - 1
        self.v()
        return x, y

    def head_go_next(self):
        self.head = self.head + 1
        if self.head >= MAX_MAILBOX_SIZE:
            self.head = self.head - MAX_MAILBOX_SIZE

    def tail_go_next(self):
        self.tail = self.tail + 1
        if self.tail >= MAX_MAILBOX_SIZE:
            self.tail = self.tail - MAX_MAILBOX_SIZE

    def p(self):
        self.lock.acquire()

    def v(self):
        self.lock.release()

