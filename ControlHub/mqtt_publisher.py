import paho.mqtt.client as mqtt


class MqttPublisher:
    def __init__(self):
        self.mqtt = mqtt.Client("system_pub")
        self.broker_ip = ""

    def update_broker_ip(self, new_ip):
        self.broker_ip = new_ip

    def publish_message(self, data):
        self.mqtt.connect(self.broker_ip, 2005)
        self.mqtt.publish("system_to_mobile_app", data)
        print("mqtt 1")
        self.mqtt.loop(1)
        return True
