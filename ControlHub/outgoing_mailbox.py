# Mailbox implementation for outgoing messages.

import threading

MAX_MAILBOX_SIZE = 256


class OutgoingMailbox:
    def __init__(self):
        self.i = 0
        self.list = [MAX_MAILBOX_SIZE]
        self.lock = threading.Lock()
        self.init()

    def init(self):
        i = 0
        while i < MAX_MAILBOX_SIZE:
            self.list.append([])
            i = i + 1

    def get_new_mailbox_number(self):
        self.p()
        self.go_next()
        while self.list[self.i] != []:
            self.go_next()
        j = self.i
        self.v()
        return j

    def go_next(self):
        self.i = self.i + 1
        if self.i >= MAX_MAILBOX_SIZE:
            self.i = self.i - MAX_MAILBOX_SIZE

    def p(self):
        self.lock.acquire()

    def v(self):
        self.lock.release()

