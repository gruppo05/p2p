import socket
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#server_address = (sys.argv[1], 10000)
<<<<<<< HEAD
server_address = ('192.168.43.135', 3000)
=======
server_address = ('192.168.43.73', 3000)
>>>>>>> 06d0db8ddfed4a61e23a971470acbe129f7f0eef
print("starting up on port", server_address)
sock.connect(server_address)

try:
	message = sys.argv[1]
	sock.sendall(message.encode())
	print("Inviato:", message)
finally:
    sock.close()

