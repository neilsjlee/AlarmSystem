import requests

# r = requests.post('http://127.0.0.1:2002/register', json={"device_type": "PIRSensor", "device_id": "00000001"})
# r = requests.post('http://127.0.0.1:2002/register', json={"device_type": "Camera", "device_id": "00000002"})
# r = requests.post('http://192.168.1.195:2002/alert', json={"data1": "value1"})
# r = requests.post('http://99.105.193.244:2002/alert', json={"data1": "value1"})

r = requests.get('http://127.0.0.1:2002/current_status')
print("r: ", r)
data = r.json()
print("data: ", data)


# r2 = requests.get("https://jsonplaceholder.typicode.com/users/1")
# data2 = r2.json()
# print("data: ", data2)
# print("r: ", r2)