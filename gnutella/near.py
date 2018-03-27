import random
import ipaddress

myIPP2P = "127.000.000.001|0000:0000:0000:0000:0000:0000:0000:0001"
myPort = "3000"
TTL = 2

def setNumber(n):
	if n < 10:
		copy = "0"+str(n)
	return n
	
def PktidGenerator():
	return "".join(choice(string.ascii_letters + string.digits) for x in range(16))
	
def creazioneSocketIPv4(IPP2P,PortaP2P):
	#apertura socket
	peer_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	peer_socket.connect((IPP2P,int(PortaP2P)))
	return peer_socket
	
def creazioneSocketIPv6(IPP2P,PortaP2P):
	#apertura socket
	peer_socket = socket.socket(socket.AF_INET6,socket.SOCK_STREAM)
	peer_socket.connect((IPP2P,int(PortaP2P)))
	return peer_socket



# Client
if command is "1":
	# --> creare socket di ricezione lato server
	
	myPktid = PktidGenerator()
	#Prendo tutti gli utente
	self.dbReader.execute("SELECT IPP2P, PP2P FROM user")
	TTL = setNumber(TTL)
	resultUser = self.dbReader.fetchall()
	msg = "NEAR" + myPktid + myIPP2P.ljust(55) + myPort.ljust(5) + TTL

	for user in resultUser:
		rnd = random.random()
		if(rnd<0.5):
			IPP2P = user[0][0:15]
			#fix problem ipv4
			IPP2P = ipaddress.Ipv4Address(IPP2P)
			connection=creazioneSocketIPv4(IPP2P,user[1])
		else:
			IPP2P = user[0][16:55]
			connection=creazioneSocketIPv6(IPP2P,user[1])
	
		print("Invio --> " + color.send + msg + color.end)
		connection.sendall(msg.encode())
		connection.close()


#Server

#Ricevo le richieste NEAR
command = connection.recv(4).decode()
if command == "NEAR":
	Pktid = connection.recv(16).decode()
	IPP2P = connection.recv(55).decode()
	PP2P = connection.recv(5).decode()
	TTL = connection.recv(2).decode()
	
	#rispondo 
	msg = "ANEA" + myPktid + myIPP2P.ljust(55) + myPort.ljust(5)
	connection.sendall(msg.encode())
	connection.close()
	
	if TTL == "01":
		break
	else:
		TTL = setNumber(int(TTL) - 1)
		msg = "NEAR" + Pktid + IPP2P.ljust(55) + str(user[1]).ljust(5) + TTL
		self.dbReader.execute("SELECT IPP2P, PP2P FROM user WHERE IPP2P!=?", (IPP2P,))
		resultUser = self.dbReader.fetchall()

		for user in resultUser:
			rnd = random.random()
			if(rnd<0.5):
				IPP2P = user[0][0:15]
				#fix problem ipv4
				IPP2P = ipaddress.Ipv4Address(IPP2P)
				connection=creazioneSocketIPv4(IPP2P,user[1])
			else:
				IPP2P = user[0][16:55]
				connection=creazioneSocketIPv6(IPP2P,user[1])

			print("Invio --> " + color.send + msg + color.end)
			connection.sendall(msg.encode())
			connection.close()
	#Inserisco il nuovo utente
	dbReader.execute("INSERT INTO user (IPP2P, PP2P) values (?, ?)",(IPP2P, IPP))


		
		
	
