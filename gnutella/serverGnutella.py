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
	return ip
	
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
		IP = "192.168.43.73"
		self.PORT = 3000
		
		UDP_IP = "127.0.0.1"
		UDP_PORT = 49999
		#MODIFICAMI CON IL TUO IP
		self.myIPP2P = "192.168.043.073|0000:0000:0000:0000:0000:0000:0000:0001"
		self.myPort = 3000
		self.myPortAnear = 50001
		
		# Creo DB
		conn = sqlite3.connect(':memory:', check_same_thread=False)
		self.dbReader = conn.cursor()

		# Creo tabella user
		clearAndSetDB(self)
		#inserisco l'utente root
		self.dbReader.execute("INSERT INTO user (IPP2P, PP2P) values ('192.168.043.135|0000:0000:0000:0000:0000:0000:0000:0001', '3000')")
		
		# Socket ipv4/ipv6 port 3000
		self.server_address = (IP, self.PORT)
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind(self.server_address)
		self.sock.listen(5)
		
		# socket upd ipv4 internal Server
		self.sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sockUDP.bind((UDP_IP, UDP_PORT))
		
		# Socket ipv4/ipv6 port 50001
		self.server5k1 = (IP, self.myPortAnear)
		self.sock5k1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock5k1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock5k1.bind(self.server5k1)
		self.sock5k1.listen(5)
	
		
	def attesaVicini(self):
		#dovrebbe durare 300s
		#drop near db
		while True:
			try:
				connection, client_address = self.sock5k1.accept()
				print("RICEVO "+connection.recv(4).decode())
			
				Pktid = connection.recv(16).decode()
				IPP2P = connection.recv(55).decode()
				PP2P = connection.recv(5).decode()
				
				#verifico se l'utente è già salvato nel db oppure lo aggiungo
				self.dbReader.execute("SELECT IPP2P FROM user WHERE IPP2P=?", (IPP2P,))
				
				data = self.dbReader.fetchone() #retrieve the first row
				print("dodododo")
				if data is None:
					print("zibibbo")
					dbReader.execute("INSERT INTO user (IPP2P, PP2P) values (?, ?)",(IPP2P, IPP))
					print(color.green + "Aggiunto nuovo user" + color.end)
				else:
					print(color.fail + "User già presente" + color.end)
			except:
				print("erroreee")
			
	
	
	def internalServer(self):
		print(color.green+"In attesa di comandi interni..."+color.end)
		while True:
			data, addr = self.sockUDP.recvfrom(4)
			command = data.decode()
			print("Ricevuto comando dal client: "+color.recv+command+color.end)
			if command == "NEAR":
				threading.Thread(target = self.attesaVicini, args = '').start()
				myPktid = PktidGenerator()
				TTL = setNumber(2)
				self.dbReader.execute("SELECT IPP2P, PP2P FROM user")
				resultUser = self.dbReader.fetchall()
				msg = "NEAR" + myPktid + self.myIPP2P + str(self.myPortAnear).ljust(5) + TTL
				print(msg)
				for user in resultUser:
					#rnd = random()
					rnd = 0.1
					if(rnd<0.5):
						IPP2P = user[0][0:15]
						IPP2P = splitIp(IPP2P)

						PP2P=int(user[1])
						
						#fix problem ipv4
						#IPP2P = ipaddress.ip_address(IPP2P)
						
						
				
						print(color.green+"Connessione IPv4:"+IPP2P+color.end)
						
						peer_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
						peer_socket.connect((IPP2P,PP2P))
						print(color.green+"Connessione stabilita"+color.end);
		
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
					print("Download")
					print("Quale file vuoi scaricare?")
					self.dbReader.execute("SELECT * FROM File WHERE IPP2P != ?", (IP,))
					resultFile = self.dbReader.fetchall()

					files[0] = ("0","0","0")
					i = 1
					for resultFile in resultFile:
						files[i] = (resultFile[0], resultFile[1], resultFile[2])
						print(i + " - " + resultFile[1])

					code = input("\n ")	

					connection.sendall(("RETR" + files[code][0]).encode)
					
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
				print("SONO NEL SERVER PRINCIPALE")
				#connection.settimeout(60)
				threading.Thread(target = self.startServer, args = (connection,client_address)).start()
			except:
				return False
			
	def startServer(self, connection, client_address):
		while True:
			command = connection.recv(4).decode()
			print("SONO NEL SERVER CHE GESTISCE LE CONNESSIONI ESTERNE (richieste)")
			try:
				if command == "NEAR":
					Pktid = connection.recv(16).decode()
					IPP2P = connection.recv(55).decode()
					PP2P = connection.recv(5).decode()
					TTL = connection.recv(2).decode()
					
					#rispondo 
					msg = "ANEA" + Pktid + self.myIPP2P.ljust(55) + str(self.myPort).ljust(5)
					print("Invio --> " + color.send + msg + color.end)

					peer_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
					peer_socket.connect((IPP2P,PP2P))
					peer_socket.sendall(msg.encode())
					peer_socket.close()
					
					
					'''
					if int(TTL) == 1:
						#return
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
					
					'''
					
		
				
				elif command == "QUER":
					print("QUER")
				elif command == "RETR":
					print("RETR")
					
					#inviare un file che ho
					#leggo il filemd5 dal client o dalla connessione?
					FileMD5 = connection.recv(55).decode()
					
					
					self.dbReader.execute("SELECT Filename FROM File WHERE FileMD5 = ?",(FileMD5,))
					resultFile = self.dbReader.fetchone()
					f = os.open(str(resultFile), os.O_RDONLY)

					filesize = os.fstat(fd)[stat.ST.SIZE]
					nChunck = filesize / 4096

					if (filesize % 4096)!= 0:
						nChunk = nChunk + 1

					nChunk = int(float(nChunk))
					pacchetto = "ARET" + str(nChunk).zfill(6)
					sock.send(pacchetto.encode())
					print ('Trasferimento in corso di ', resultFile, '[BYTES ', filesize, ']')

					i = 0

					while i < nChunk:
						buf = os.read(fd,4096)
						if not buf: break
						lbuf = len(buf)
						lbuf = str(lBuf).zfill(5)
						sock.send(lBuf.encode())
						sock.send(buf)
						i = i + 1

					os.close(fd)
					print('Trasferimento completato.. ')

					#chiusura della connessione
					connection.close()
					#chiusura della socket
					sock.close()
					
			except:
				connection.close()
				return False
		
if __name__ == "__main__":
    gnutella = GnutellaServer()
gnutella.server()











