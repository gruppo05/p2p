import socket
import sys

IP = "127.0.0.1"
PORT = 3000

# crea socket TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (IP, PORT)
print("Server attivo su %s porta %s" % server_address)
sock.bind(server_address)

# In ascolto per connessione
sock.listen(1)

while True:
    print("In attesa di connessione...")
    connection, client_address = sock.accept()
    
    try:
        print("connection from", client_address)
		
        while True:
            data = connection.recv(16)
            print('received "%s"' % data)
            if data:
                print("sending data back to the client")
                connection.sendall(data)
            else:
                print("no more data from", client_address)
                break
            
    finally:
    	connection.close()
