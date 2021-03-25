import socket
import time

HOST = '192.168.1.90'
PORT = 3000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect((HOST, PORT))

client_socket.sendall('hello. testing'.encode('utf-8'))

client_socket.close()
# while(True):
#    print("wait")
    # time.sleep(1000)
