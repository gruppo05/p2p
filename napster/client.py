import socket
import sys

if sys.argv[1] == '4':
	print(sys.argv[1])
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_address = ('127.0.0.1', 3000)
	sock.connect(server_address)
else:
	print(sys.argv[1])
	sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
	server_address = ('0000:0000:0000:0000:0000:0000:0000:0001', 3000)
	sock.connect(server_address)
	
while True:
	message = sys.argv[2]
	sock.sendall(message.encode())
	print("Inviato:", message)
