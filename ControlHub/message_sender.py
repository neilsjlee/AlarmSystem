import asyncio
import aiohttp
import threading
import json


class MessageSender(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.outgoing_mailbox = None
        self.state_manager = None
        self.mqtt_publisher = None
        self.buffer = []

    def get_outgoing_mailbox(self, om):
        self.outgoing_mailbox = om

    def get_state_manager(self, sm):
        self.state_manager = sm

    def get_mqtt_publisher(self, mp):
        self.mqtt_publisher = mp

    def get_task_from_outgoing_mailbox(self):
        if self.outgoing_mailbox.number_of_items > 0:
            mailbox_address, outgoing_message = self.outgoing_mailbox.pull_next_outgoing_mailbox()
            self.send_task(mailbox_address, outgoing_message)

    def send_task(self, mailbox_address, outgoing_messages):
        print("MessageSender.send_task(): ", outgoing_messages)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        tasks = []
        for each in outgoing_messages:
            each_json = json.loads(each)
            if each_json['message_type'] == "status":
                task = asyncio.ensure_future(self.send_get_message(each_json['device_id'], each_json['device_ip'], each_json['message_type']))
            else:
                task = asyncio.ensure_future(self.send_post_message(each_json['device_id'], each_json['device_ip'], each_json['message_type']))
            tasks.append(task)
        loop.run_until_complete(asyncio.wait(tasks))
        print("RESPONSE BUFFER: ", self.buffer)
        for each_response in self.buffer:
            if each_response[2] == "ok":
                if each_response[1] == "arm":
                    self.state_manager.update_state_for_a_device(each_response[0], True)
                elif each_response[1] == "disarm":
                    self.state_manager.update_state_for_a_device(each_response[0], False)
                elif each_response[1] == "deregi":
                    self.state_manager.remove_device(each_response[0])
                elif each_response[1] == "status":
                    self.state_manager.update_state_for_a_device(each_response[0], each_response[3])
            elif each_response[2] == "ng":
                if each_response[1] == "status":
                    self.state_manager.remove_device(each_response[0])
        self.buffer.clear()
        self.mqtt_publisher.publish_message(str(mailbox_address)+"*"+self.state_manager.return_current_state())

    async def send_post_message(self, did, ip, message_type):
        print("Sending Post message")
        async with aiohttp.ClientSession() as session:
            async with session.post("http://"+ip+"/"+message_type, data="{\"data\":\"empty\"}") as response:
                if response.status == 200:
                    self.buffer.append([did, message_type, "ok"])
                else:
                    self.buffer.append([did, message_type, "ok"])

    async def send_get_message(self, did, ip, message_type):
        print("Sending GET message")
        async with aiohttp.ClientSession() as session:
            async with session.get("http://"+ip+"/"+message_type) as response:
                received_text = await response.text()
                if response.status < 300:
                    print("RECEIVED GET RESPONSE:", json.loads(received_text))
                    self.buffer.append([did, message_type, "ok", json.loads(received_text)['armed']])
                else:
                    self.buffer.append([did, message_type, "ng"])

    def run(self):
        while(True):
            self.get_task_from_outgoing_mailbox()
