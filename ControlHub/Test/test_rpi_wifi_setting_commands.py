import os
import json

wifi_ssid = "ATTb3hjRMS"
wifi_pw = "kz7hwdt7jtpy"
mobile_app_private_ip = ""

system_setting_file_path = "./system_setting.json"

# WPA_SUPPLICANT_CONF_FILE_PATH = "/etc/wpa_supplicant/wpa_supplicant.conf"
WPA_SUPPLICANT_CONF_FILE_PATH = "./wpa_supplicant.conf" # Test Purpose


def rpi_wifi_setting(ssid, pw):
    # Setting up Wi-Fi for Raspberry Pi
    with open(WPA_SUPPLICANT_CONF_FILE_PATH, 'w') as wpa_supplicant_file:
        wpa_supplicant_file.writelines(["ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n",
                                        "update_config=1\n",
                                        "country=US\n\n",
                                        "network={\n",
                                        "\tssid=\"", wifi_ssid, "\"\n",
                                        "\tpsk=\"", wifi_pw, "\"\n",
                                        "\tkey_mgmt=WPA-PSK\n",
                                        "}\n"])
    response = os.system("sudo wpa_cli -i wlan0 reconfigure")


def get_setting_info_from_nfc():
    # Wait for Mobile App to pass Wi-Fi SSID, Wi-Fi PW, and Mobile App's IP address

    return


def check_internet_connection():
    hostname = "google.com"
    response = os.system("ping -c 1 " + hostname)
    # and then check the response...
    if response == 0:
        ping_status = "Network Active"
    else:
        ping_status = "Network Error"
    return ping_status


get_setting_info_from_nfc()
rpi_wifi_setting(wifi_ssid, wifi_pw)

if check_internet_connection() == "Network Active":
    print("Network Active")
else:
    print("Network Error - ")
    # rpi_wifi_setting(wifi_ssid, wifi_pw)

with open(system_setting_file_path, 'w') as opened_system_setting_file:
    new_setting = {"wifi_ssid": wifi_ssid, "wifi_pw": wifi_pw, "mobile_app_private_ip": mobile_app_private_ip}
    json.dump(new_setting, opened_system_setting_file)