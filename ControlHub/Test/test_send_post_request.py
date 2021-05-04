import requests

# r = requests.post('http://127.0.0.1:2002/register', json="{\"device_id\":\"00000001\", \"device_type\":\"PIRSensor\", \"ip\":\"192.168.1.231\"}")
# r = requests.post('http://127.0.0.1:2002/register', json={"device_type": "Camera", "device_id": "00000002", "ip":"192.168.1.55"})
# r = requests.post('http://127.0.0.1:2002/alert', json={"device_id": "00000002"})
# r = requests.post('http://127.0.0.1:2002/scr_manual_single', json={"device_id": "00000002"})
# r = requests.post('http://127.0.0.1:2002/scr_manual_all', json={"device_id": "DOESN'T MATTER"})
# r = requests.post('http://127.0.0.1:2002/arm_request_all', json={"device_id": "DOESN'T MATTER"})

# r = requests.post('http://127.0.0.1:2002/deregister', json={"device_id": "00000001"})

# r = requests.post('http://192.168.1.195:2002/alert', json={"device_id": "00000001"})
# r = requests.post('http://99.105.193.244:2002/alert', json={"data1": "value1"})

# print(r.text)

# r = requests.post('http://192.168.1.231/arm', json={"device_type": "Camera", "device_id": "00000003", "ip":"192.168.1.57"})
# r = requests.post('http://192.168.1.231/disarm', json={"device_type": "Camera", "device_id": "00000003", "ip":"192.168.1.57"})
# r = requests.post('http://192.168.1.231/dregi', json={"device_type": "Camera", "device_id": "00000003", "ip":"192.168.1.57"})
# r = requests.get('http://192.168.1.231/status')
# print("r: ", r)
# data = r.json()
# print("data: ", data)


# r = requests.post('http://99.105.193.244:2002/register', json={"device_type": "Camera", "device_id": "00000003", "ip":"192.168.1.57"})
# r = requests.post('http://99.105.193.244:2002/deregister', json={"device_type": "PIRSensor", "device_id": "00000001"})
# r = requests.post('http://99.105.193.244:2002/scr_manual_single', json={"device_id": "00000001"})
# r = requests.post('http://99.105.193.244:2002/arm_request_all', json={"device_id": "00000001"})

# r = requests.get('http://192.168.1.195:2002/current_status')
# r = requests.post('http://192.168.1.195:2002/scr_manual_all', json={"device_id": "00000001"})

# r = requests.post('http://127.0.0.1:2002/scr_manual_all', json={"device_id": "00000001"})
# r = requests.get('http://127.0.0.1:2002/current_status')
# print("r: ", r)
# data = r.json()
# print("data: ", data)

r = requests.get('http://192.168.1.195:2002/cam_photo')
print("r: ", r)
# print("data: ", data)
hex_data = r.content
jpeg_data = hex_data
with open('out.jpg', 'wb') as out_file:
    out_file.write(jpeg_data)


# r = requests.post('https://ptsv2.com/t/ra4ej-1616855109/post', json={"device_type": "PIRSensor", "device_id": "00000001"})
# r = requests.post('http://webhook.site/df44f30b-c491-4336-8f11-8740631e0639', json={"device_type": "PIRSensor", "device_id": "00000001"})
# r = requests.get('https://webhook.site/df44f30b-c491-4336-8f11-8740631e0639')