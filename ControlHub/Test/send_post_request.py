import requests

r = requests.post('http://127.0.0.1:2002/alert', json={"data1": "value1"})
# r = requests.post('http://192.168.1.195:2002/alert', json={"data1": "value1"})
# r = requests.post('http://99.105.193.244:2002/alert', json={"data1": "value1"})

print(r)