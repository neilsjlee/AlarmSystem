import paho.mqtt.client as mqtt


class MqttPublisher:
    def __init__(self):
        self.mqtt = mqtt.Client("system_pub")

    def publish_message(self, data):
        self.mqtt.connect("192.168.1.195", 2005)
        self.mqtt.publish("system_to_mobile_app", data)
        print("mqtt 1")
        self.mqtt.loop(1)
        return True
