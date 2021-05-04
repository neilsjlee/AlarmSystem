from test_extra_thread import *
from http_server import *
from task_manager import *
from state_manager import *
import json
import requests
from priority_queue import *
from mqtt_publisher import MqttPublisher
from outgoing_mailbox import *
from message_sender import *
import socket
import os
import sys
# from queue import PriorityQueue

# main.py should state
# - Setup Wi-Fi connection
# - System restart process
# -


# Shared Resources
task_queue = MyPriorityQueue()
outgoing_mailbox = OutgoingMailbox()

# Global Variables
wifi_ssid = ""
wifi_pw = ""

mobile_app_private_ip = ""

private_ip = ""
public_ip = ""

# FILE PATHS
# WPA_SUPPLICANT_CONF_FILE_PATH = "./wpa_supplicant.conf" # Test Purpose
WPA_SUPPLICANT_CONF_FILE_PATH = "/etc/wpa_supplicant/wpa_supplicant.conf"
SYSTEM_SETTIGN_FILE_PATH = "./system_setting.json"


def load_previous_setting():
    try:
        with open(SYSTEM_SETTIGN_FILE_PATH, 'r') as __opened_system_setting_file:
            try:
                setting_json = json.load(__opened_system_setting_file)
                print(setting_json)
                global wifi_ssid, wifi_pw
                wifi_ssid = setting_json['wifi_ssid']
                wifi_pw = setting_json['wifi_pw']
            except:
                print("system_setting.json file exists, but JSON data is corrupted or missing.")
    except:
        print("system_setting.json file is missing.")


def rpi_wifi_setting():
    # Setting up Wi-Fi for Raspberry Pi
    not_connected = True
    internet_check_interval = 10
    timeout_interval = 60

    os.system("sudo chmod 777 " + WPA_SUPPLICANT_CONF_FILE_PATH)
    with open(WPA_SUPPLICANT_CONF_FILE_PATH, 'w') as wpa_supplicant_file:
        wpa_supplicant_file.writelines(["ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n",
                                        "update_config=1\n",
                                        "country=US\n\n",
                                        "network={\n",
                                        "\tssid=\"", wifi_ssid, "\"\n",
                                        "\tpsk=\"", wifi_pw, "\"\n",
                                        "\tkey_mgmt=WPA-PSK\n",
                                        "}\n"])
    os.system("sudo wpa_cli -i wlan0 reconfigure")
    while not_connected and (timeout_interval > 0):
        if check_internet_connection() == "Network Active":
            not_connected = False
        elif check_internet_connection() == "Network Error":
            time.sleep(internet_check_interval)
            timeout_interval = timeout_interval - internet_check_interval

    if not_connected:
        get_setting_info_from_nfc()


def get_setting_info_from_nfc():
    global wifi_ssid, wifi_pw, mobile_app_private_ip
    os.system("rm data_from_nfc.txt")
    os.system("python3 ./android_beam/beam.py --device tty:S0:pn532 recv save data_from_nfc.txt")
    with open("./data_from_nfc.txt", 'r', errors='ignore') as opened_file:
        data = opened_file.read()
        data2 = "{" + data.split('{')[1]
        try:
            data_json = json.loads(data2)
            wifi_ssid = data_json["SSID"]
            wifi_pw = data_json["PW"]
            mobile_app_private_ip = data_json["IP"]
            print("get_setting_info_from_nfc ['wifi_ssid', 'wifi_pw', 'mobile_app_private_ip'] = ", wifi_ssid, wifi_pw, mobile_app_private_ip)
            result = True
        except:
            print("error")
            result = False
            get_setting_info_from_nfc()
    return result


def send_ack_and_setting_socket():
    HOST = mobile_app_private_ip
    PORT = 3000

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    data = {
        'public_ip': public_ip,
        'private_ip': private_ip
    }
    data_string = json.dumps(data)
    client_socket.sendall(data_string.encode('utf-8'))
    client_socket.close()


def check_internet_connection():
    hostname = "google.com"
    response = os.system("ping -c 1 " + hostname)
    # and then check the response...
    if response == 0:
        ping_status = "Network Active"
    else:
        ping_status = "Network Error"
    return ping_status


def get_my_ip_addresses():
    global public_ip, private_ip
    public_ip = requests.get('https://api.ipify.org').text
    print("My Public IP is ", public_ip)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 3
    s.connect(('8.8.8.8', 0))
    private_ip = s.getsockname()[0]
    s.close()
    print("My Private IP is ", private_ip)


def init():
    # Start HTTP Server
    server_thread = threading.Thread(target=run_server)
    get_task_queue(task_queue)
    get_outgoing_mailbox(outgoing_mailbox)
    server_thread.start()

    dummy_function_thread = threading.Thread(target=dummy_function)
    dummy_function_thread.start()

    # Start "Task Manager"
    task_manager = TaskManager(task_queue, outgoing_mailbox)

    # Create "State Manager"
    state_manager = StateManager(task_queue, task_manager)

    # Pass 'State Manager' instance to Task Manager
    task_manager.get_state_manager(state_manager)
    task_manager.start()

    # Start "MQTT Publisher"
    mqtt_publisher_ = MqttPublisher()
    # mqtt_publisher_.update_broker_ip("192.168.1.195")
    mqtt_publisher_.update_broker_ip(private_ip)

    # Pass 'MQTT Publisher' instance to Task Manager & Server
    task_manager.get_mqtt_publisher(mqtt_publisher_)
    get_mqtt_publisher(mqtt_publisher_)

    # MessageSender
    message_sender = MessageSender()
    message_sender.get_outgoing_mailbox(outgoing_mailbox)
    message_sender.get_state_manager(state_manager)
    message_sender.get_mqtt_publisher(mqtt_publisher_)
    message_sender.start()

    #
    print(outgoing_mailbox.list)


if __name__ == "__main__":
    load_previous_setting()

    if sys.platform == "linux": # Run below lines only on linux.
        if wifi_ssid == "": # If there's no previous setting exist,
            get_setting_info_from_nfc()
            rpi_wifi_setting()
            time.sleep(5)
            get_my_ip_addresses()
            send_ack_and_setting_socket()

            with open(SYSTEM_SETTIGN_FILE_PATH, 'w') as opened_system_setting_file:
                new_setting = {"wifi_ssid": wifi_ssid, "wifi_pw": wifi_pw, "mobile_app_private_ip": mobile_app_private_ip}
                json.dump(new_setting, opened_system_setting_file)
        elif wifi_ssid != "":
            if check_internet_connection() == "Network Active":
                print("Network Active")
                os.system("sudo systemctl restart mosquitto")

            else:
                print("Network Error - ")
                rpi_wifi_setting(wifi_ssid, wifi_pw)

    get_my_ip_addresses()

    init()

