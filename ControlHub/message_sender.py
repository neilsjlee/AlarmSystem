import asyncio
import aiohttp
import threading
import json


class MessageSender(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.outgoing_mailbox = None
        self.state_manager = None
        self.buffer = []

    async def send_post_message(self, ip, message_type):
        async with aiohttp.ClientSession() as session:
            # async with session.post("http://"+ip+"/"+message_type, data="{\"data\":\"empty\"}") as response:
            async with session.post("https://ptsv2.com/t/wzki5-1617494735/post", data="{\"data\":\"empty\"}") as response:
                data = await response.text()
                print("DATA: ", data)
                self.buffer.append(data)

    def send_task(self, outgoing_messages):
        print("MessageSender.send_task(): ", outgoing_messages)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        tasks = []
        for each in outgoing_messages:
            each_json = json.loads(each)
            task = asyncio.ensure_future(self.send_post_message(each_json['device_ip'], each_json['message_type']))
            tasks.append(task)
        loop.run_until_complete(asyncio.wait(tasks))


    def get_task_from_outgoing_mailbox(self):
        if self.outgoing_mailbox.number_of_items > 0:
            mailbox_address, outgoing_message = self.outgoing_mailbox.pull_next_outgoing_mailbox()
            self.send_task(outgoing_message)

    def get_outgoing_mailbox(self, om):
        self.outgoing_mailbox = om

    def get_state_manager(self, sm):
        self.state_manager = sm

    def run(self):
        while(True):
            self.get_task_from_outgoing_mailbox()
