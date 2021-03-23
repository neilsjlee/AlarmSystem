from test_extra_thread import *
from test_python_server import *
from task_manager import *
from state_manager import *
import json
import os

# main.py should state
# - Setup Wi-Fi connection
# - System restart process
# -

wifi_ssid = ""
wifi_pw = ""

# WPA_SUPPLICANT_CONF_FILE_PATH = "/etc/wpa_supplicant/wpa_supplicant.conf"
WPA_SUPPLICANT_CONF_FILE_PATH = "./wpa_supplicant.conf" # Test Purpose

mobile_app_private_ip = ""

private_ip = ""
public_ip = ""

system_setting_file_path = "./system_setting.json"


def load_previous_setting():
    try:
        with open(system_setting_file_path, 'r') as opened_system_setting_file:
            try:
                setting_json = json.load(opened_system_setting_file)
                print(setting_json)
                global wifi_ssid, wifi_pw
                wifi_ssid = setting_json['wifi_ssid']
                wifi_pw = setting_json['wifi_pw']
            except:
                print("system_setting.json file exists, but JSON data is corrupted or missing.")
    except:
        print("system_setting.json file is missing.")


def rpi_wifi_setting(ssid, pw):
    with open(WPA_SUPPLICANT_CONF_FILE_PATH, 'w') as wpa_supplicant_file:
        wpa_supplicant_file.writelines(["ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n",
                                        "update_config=1\n",
                                        "country=US\n\n",
                                        "network={\n",
                                        "\tssid=\"", wifi_ssid, "\"\n",
                                        "\tpsk=\"", wifi_pw, "\"\n",
                                        "\tkey_mgmt=WPA-PSK\n",
                                        "}\n"])


def get_setting_info_from_nfc():
    # Wait for Mobile App to pass Wi-Fi SSID, Wi-Fi PW, and Mobile App's IP address

    return


if __name__ == "__main__":
    load_previous_setting()

    if wifi_ssid == "": # If there's no previous setting exist,
        get_setting_info_from_nfc()
        with open(system_setting_file_path, 'w') as opened_system_setting_file:
            new_setting = {"wifi_ssid": wifi_ssid, "wifi_pw": wifi_pw, "mobile_app_private_ip": mobile_app_private_ip}
            json.dump(new_setting, opened_system_setting_file)



    # Start HTTP Server
    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    dummy_function_thread = threading.Thread(target=dummy_function)
    dummy_function_thread.start()

    # Start "Task Manager"
    task_manager = TaskManager(server_queue)
    task_manager.start()

    # Start "State Manager"
    state_manager = StateManager(server_queue, task_manager)
    state_manager.start()

    # Pass 'State Manager' instance to Task Manager
    task_manager.get_state_manager(state_manager)


