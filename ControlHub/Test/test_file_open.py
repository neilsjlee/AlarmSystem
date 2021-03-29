import json

#with open("./test.txt", "rb") as opened_file:
#    for b in opened_file:
#        print(b)


with open("./test.txt", 'r', errors='ignore') as opened_file:
    data = opened_file.read()
    print(data)
    data2 = data.split('{')[1]
    print(data2)
    data3 = "{"+data2
    print(data3)
    try:
        data_json = json.loads(data3)
        print(data_json)
        print(data_json["IP"])
    except:
        print("error")
