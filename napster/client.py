import socket, sys, time

if sys.argv[1] is '4':
	print(sys.argv[1])
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_address = ('127.000.000.001', 3000)
		sock.connect(server_address)
		print("ook")
	except:
		print("Non riesco a stabilire la connessione")
else:
	print(sys.argv[1])
	sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
	server_address = ('0000:0000:0000:0000:0000:0000:0000:0001', 3000)
	sock.connect(server_address)
	
while True:
	message = sys.argv[2]
	sock.sendall(message.encode())
	print("Inviato:", message)
	time.sleep(3)
	
