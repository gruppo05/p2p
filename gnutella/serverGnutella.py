import socket, sqlite3, string, subprocess, threading, os, random, ipaddress, time
from random import *

def clearAndSetDB(self):
	self.dbReader.execute("DROP TABLE IF EXISTS user")
	#self.dbReader.execute("DROP TABLE IF EXISTS file")
	#self.dbReader.execute("DROP TABLE IF EXISTS download")
	self.dbReader.execute("CREATE TABLE user (IPP2P text, PP2P text)")
	#self.dbReader.execute("CREATE TABLE file (Filemd5 text, Filename text, SessionID text)")
	#self.dbReader.execute("CREATE TABLE download (Filemd5 text, Download integer)")

def PktidGenerator():
	return "".join(choice(string.ascii_letters + string.digits) for x in range(16))

def creazioneSocketIPv6(IPP2P,PortaP2P):
	#apertura socket
	peer_socket = socket.socket(socket.AF_INET6,socket.SOCK_STREAM)
	peer_socket.connect((IPP2P,int(PortaP2P)))
	return peer_socket
	
def setNumber(n):
	if n < 10:
		n = "0"+str(n)
	return n

def splitIp(ip):
	splitted = ip.split(".")
	ip = str(int(splitted[0]))+"."+str(int(splitted[1]))+"."+str(int(splitted[2]))+"."+str(int(splitted[3]))
	
class color:
	HEADER = '\033[95m'
	recv = '\033[36m'
	green = '\033[32m'
	send = '\033[33m'
	fail = '\033[31m'
	end = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

class GnutellaServer(object):
	def __init__(self):
		IP = "192.168.178.26"
		PORT = 3000
		UDP_IP = "192.168.178.26"
		UDP_PORT = 49999
		#MODIFICAMI CON IL TUO IP
		self.myIPP2P = "192.168.178.026|0000:0000:0000:0000:0000:0000:0000:0001"
		self.myPort = 3000
		
		# Creo DB
		conn = sqlite3.connect(':memory:', check_same_thread=False)
		self.dbReader = conn.cursor()

		# Creo tabella user
		clearAndSetDB(self)
		#inserisco l'utente root
		self.dbReader.execute("INSERT INTO user (IPP2P, PP2P) values ('127.000.000.001|0000:0000:0000:0000:0000:0000:0000:0001', '3000')")
		# Socket ipv4/ipv6
		self.server_address = (IP, PORT)
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind(self.server_address)
		self.sock.listen(5)
		
		# socket upd ipv4 internal Server
		self.sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sockUDP.bind((UDP_IP, UDP_PORT))
		
		
	def internalServer(self):
		print(color.green+"In attesa di comandi interni..."+color.end)
		#splitIp("192.168.001.002")
		while True:
			data, addr = self.sockUDP.recvfrom(4)
			command = data.decode()
			print("Ricevuto comando dal client: "+color.recv+command+color.end)
			if command == "NEAR":
				myPktid = PktidGenerator()
				TTL = setNumber(2)
				self.dbReader.execute("SELECT IPP2P, PP2P FROM user")
				resultUser = self.dbReader.fetchall()
				msg = "NEAR" + myPktid + self.myIPP2P + str(self.myPort).ljust(5) + TTL
				print(msg)
				for user in resultUser:
					#rnd = random()
					rnd = 0.1
					if(rnd<0.5):
						IPP2P = user[0][0:15]
						
						#fix problem ipv4
						#IPP2P = ipaddress.ip_address(IPP2P)
						PP2P=int(user[1])
						print("Connetto con IPv4:", IPP2P)
						peer_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
						peer_socket.connect((IPP2P,PP2P))
						
					else:
						IPP2P = user[0][16:55]
						print("Connetto con IPv6:", IPP2P)
						break
						#da testare
						connection=creazioneSocketIPv6(IPP2P,user[1])
	
					print("Invio --> " + color.send + msg + color.end)
					peer_socket.sendall(msg.encode())
					peer_socket.close()
					
				if command == "QUER":
					print("Ricevuto comando dal client: "+color.recv+command+color.end)
				if command == "RETR":
					print("Ricevuto comando dal client: "+color.recv+command+color.end)
			print("\n")
		
	def server(self):
		#crea thread interno per far comunicare client e server
		threading.Thread(target = self.internalServer, args = '').start()
		
		print(color.green+"In attesa di connessione esterna..."+color.end)
		
		while True:
			try:
				connection, client_address = self.sock.accept()
				#connection.settimeout(60)
				threading.Thread(target = self.startServer, args = (connection,client_address)).start()
			except:
				return False
			
	def startServer(self, connection, client_address):
		while True:
			command = connection.recv(4).decode()
			try:
				if command == "NEAR":
					Pktid = connection.recv(16).decode()
					IPP2P = connection.recv(55).decode()
					PP2P = connection.recv(5).decode()
					TTL = connection.recv(2).decode()
					
					#rispondo 
					msg = "ANEA" + Pktid + self.myIPP2P.ljust(55) + str(self.myPort).ljust(5)
					print("Invio --> " + color.send + msg + color.end)
					connection.sendall(msg.encode())
					connection.close()
					
					if int(TTL) == 1:
						break
					else:
						TTL = setNumber(int(TTL) - 1)
						
					msg = "NEAR" + Pktid + IPP2P.ljust(55) + str(PP2P).ljust(5) + str(TTL)
					self.dbReader.execute("SELECT IPP2P, PP2P FROM user WHERE IPP2P!=?", (IPP2P,))
					resultUser = self.dbReader.fetchall()
					
					for user in resultUser:
						#rnd = random()
						#rnd = 0.1
						if(rnd<0.5):
							IPP2P = user[0][0:15]
							print(IPP2P)
							#fix problem ipv4
							#IPP2P = ipaddress.ip_address(IPP2P)
							PP2P=int(user[1])
							print("Connetto con IPv4:", IPP2P)
							peer_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
							peer_socket.connect((IPP2P,PP2P))
						
						else:
							IPP2P = user[0][16:55]
							print("Connetto con IPv6:", IPP2P)
							break
							#da testare
							connection=creazioneSocketIPv6(IPP2P,user[1])
	
						print("Invio --> " + color.send + msg + color.end)
						peer_socket.sendall(msg.encode())
						peer_socket.close()
					
					
				elif command == "ANEA":
					print("sono dentro ANEA")
					Pktid = connection.recv(16).decode()
					IPP2P = connection.recv(55).decode()
					PP2P = connection.recv(5).decode()

					#verifico se l'utente è già salvato nel db oppure lo aggiungo
					dbReader.execute("SELECT IPP2P FROM user WHERE IPP2P=?", (IPP2P,))
					data = dbReader.fetchone() #retrieve the first row
					if data is None:
						dbReader.execute("INSERT INTO user (IPP2P, PP2P) values (?, ?)",(IPP2P, IPP))
						print(color.green + "Aggiunto nuovo user" + color.end);
					else:
						print(color.fail + "User già presente" + color.end);
		
				
				elif command == "QUER":
					print("QUER")
				elif command == "RETR":
					print("RETR")
			except:
				connection.close()
				return False
		
if __name__ == "__main__":
    gnutella = GnutellaServer()
gnutella.server()











