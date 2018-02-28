import socket
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#server_address = (sys.argv[1], 10000)
server_address = ("127.0.0.1", 3000)
print('connecting to %s port %s', server_address)
sock.connect(server_address)

try:
	message = sys.argv[1]
	print('sending "%s"', message)
	sock.sendall(message)
finally:
    sock.close()
