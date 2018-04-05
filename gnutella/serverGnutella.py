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

		IP = "192.168.43.131"
		self.PORT = 4000

		UDP_IP = "127.0.0.1"
		UDP_PORT = 49999
		
		#MODIFICAMI CON IL TUO IP
		self.myIPP2P = "192.168.043.131|0000:0000:0000:0000:0000:0000:0000:0001"
		self.myPort = 4000		

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

	'''def attesaDownload(self):
		
		while True:
			connection, client_address = self.sock5k1.accept()
			print ("Ricevo " + connection.rev(4).decode())
		def attesaVicini(self):
		#dovrebbe durare 300s
		#drop near db
		while True:
			try:
				connection, client_address = self.sock5k1.accept()
				cmd=connection.recv(4).decode()
				print("RICEVO "+cmd)
				
				if cmd == "NEAR":
					Pktid = connection.recv(16).decode()
					IPP2P = connection.recv(55).decode()
					IPP2P_IPv4 = IPP2P[0:15]
					IPP2P_IPv6 = IPP2P[16:55]
					IPP2P_IPv4 = splitIp(IPP2P_IPv4)
					print(IPP2P)
					PP2P = connection.recv(5).decode()
					PP2P=int(PP2P)
					print(PP2P)
					TTL = connection.recv(2).decode()
				
					self.dbReader.execute("SELECT IPP2P FROM user WHERE IPP2P=?", (IPP2P,))
				
					data = self.dbReader.fetchone() #retrieve the first row
					if data is None:
						self.dbReader.execute("INSERT INTO user (IPP2P, PP2P) values (?, ?)",(IPP2P, PP2P))
						print(color.green + "Aggiunto nuovo user" + color.end)
					else:
						print(color.fail + "User già presente" + color.end)
				
					#rispondo 
					msg = "ANEA" + Pktid + self.myIPP2P.ljust(55) + str(self.myPort).ljust(5)
					print("Invio --> " + color.send + msg + color.end)
				
					peer_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
					peer_socket.connect((IPP2P_IPv4,PP2P))
					peer_socket.sendall(msg.encode())
					peer_socket.close()
				
					TTL = setNumber(int(TTL) - 1)
					if int(TTL) > 0:

						msg = "NEAR" + Pktid + IPP2P.ljust(55) + str(PP2P).ljust(5) + str(TTL)
						print("STAMPO IL MIE")
						print(msg)
						self.dbReader.execute("SELECT IPP2P, PP2P FROM user WHERE IPP2P!=? and IPP2P!=?", (IPP2P,self.myIPP2P,))
						resultUser = self.dbReader.fetchall()
					
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
			
				if cmd == "ANEA":
					Pktid = connection.recv(16).decode()
					IPP2P = connection.recv(55).decode()
					PP2P = connection.recv(5).decode()
				
					#verifico se l'utente è già salvato nel db oppure lo aggiungo
					self.dbReader.execute("SELECT IPP2P FROM user WHERE IPP2P=?", (IPP2P,))
				
					data = self.dbReader.fetchone() #retrieve the first row
					if data is None:
						self.dbReader.execute("INSERT INTO user (IPP2P, PP2P) values (?, ?)",(IPP2P, PP2P))
						print(color.green + "Aggiunto nuovo user" + color.end)
					else:
						print(color.fail + "User già presente" + color.end)
			except:
				print("erroreee")
				'''
	def internalServer(self):
		print(color.green+"In attesa di comandi interni..."+color.end)
		while True:
			data, addr = self.sockUDP.recvfrom(4)
			command = data.decode()
			print("Ricevuto comando dal client: "+color.recv+command+color.end)
			if command == "NEAR":
				#threading.Thread(target = self.attesaVicini, args = '').start()
				myPktid = PktidGenerator()
				TTL = setNumber(2)
				self.dbReader.execute("SELECT IPP2P, PP2P FROM user")
				resultUser = self.dbReader.fetchall()
				msg = "NEAR" + myPktid + self.myIPP2P + str(self.myPort).ljust(5) + TTL
				print(color.recv+"  "+msg+color.end)
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
					print(IPP2P)
					print(PP2P)
					peer_socket.sendall(msg.encode())
					#peer_socket.close()
					
				if command == "QUER":
					print("Ricevuto comando dal client: "+color.recv+command+color.end)
					threading.Thread(target = self.attesaRicerca, args = (data,addr)).start()
					ricerca = self.sockUDP.recvfrom(20)
					
					
				if command == "RETR":
					'''print("Ricevuto comando dal client: "+color.recv+command+color.end)
					self.dbReader.execute("SELECT * FROM File WHERE IPP2P != ?", (IP,))
					resultFile = self.dbReader.fetchall()

					i = 0
					if len(resultFile) == 1:
						lunghezza = "0" + str(len(resultFile))
					else:
						lunghezza = str(len(resultFile))
					
					for result in resultFile:
						
						if i == 0:
							self.sock.sendto(lunghezza).encode(), (selfUDP_IP, selfUDP_PORT))
							
						files[i] = (result[0], result[1], result[2])
						print(i + " - " + result[1])
						self.sock.sendto((result[1]).encode(), (self.UDP_IP, self.UDP_PORT))
	
					code = self.sockUDP.recvfrom(2)
					
					if code == -1:
						print("Download annullato.")
						break
					if len(resultFile[code][0]) == 0:
						print("Codice sbagliato.")
						break
					
					threading.Thread(target = self.attesaDownload, args = (data,addr)).start()
					
					msg = "RETR" + 	resultFile[code][0]
					
					self.dbReader.execute("SELECT IPP2P, PP2P FROM User WHERE IPP2P = ?", (IPP2P,))
					utente = self.dbReader.fetchone()
					#rnd = random()
					rnd = 0.1
					if rnd < 0.5
						IPP2P = utente[0][0:15]
						IPP2P = splitIp(IPP2P)
						PP2P = int(utente[1])
						
						print("connetto con ipv4 " + IPP2P + " PORT ->" +PP2P )
						
						peer_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
						peer_socket.connect((IPP2P,PP2P))
						
					else:
						IPP2P = utente[0][16:55]
						print("Connetto con ipv6 " + IPP2P)
						#da finire
						
						
					print("Invio --> "+ color.send + msg + color.end)	
					peer_socket.sendall((msg).encode)
					peer_socket.close()'''
					
			if command == "RETR":
				print("Ricevuto comando dal client: "+color.recv+command+color.end)
			print("\n")
			if command == "STMF":
				#stampo i file 
				self.dbReader.execute("SELECT * FROM File")

				files = self.dbReader.fetchall()

				for f in files:
					print("Filemd5: " + f[0] + " Filename: " + f[1] + " IPP2P: " + f[3])

			if command == "STMV":
				#stampo i vicini
				print("ciao")
				self.dbReader.execute("SELECT * FROM user")

				vicini = self.dbReader.fetchall()

				for v in vicini:
					print("IPP2P: " + v[0] + " PORT: " + v[1])


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
		command = connection.recv(4).decode()
		try:
			if command == "NEAR":
				Pktid = connection.recv(16).decode()
				IPP2P = connection.recv(55).decode()
				IPP2P_IPv4 = IPP2P[0:15]
				IPP2P_IPv6 = IPP2P[16:55]
				IPP2P_IPv4 = splitIp(IPP2P_IPv4)
				print(IPP2P_IPv4)
				PP2P = connection.recv(5).decode()
				PP2P=int(PP2P)
				print(PP2P)
				TTL = connection.recv(2).decode()
				
				self.dbReader.execute("SELECT IPP2P FROM user WHERE IPP2P=?", (IPP2P,))
				
				data = self.dbReader.fetchone() #retrieve the first row
				if data is None:
					self.dbReader.execute("INSERT INTO user (IPP2P, PP2P) values (?, ?)",(IPP2P, PP2P))
					print(color.green + "Aggiunto nuovo user" + color.end)
				else:
					print(color.fail + "User già presente" + color.end)
				
				#rispondo 
				msg = "ANEA" + Pktid + self.myIPP2P.ljust(55) + str(self.myPort).ljust(5)
				print("Invio --> " + color.send + msg + color.end)
				
				peer_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
				peer_socket.connect((IPP2P_IPv4,PP2P))
				peer_socket.sendall(msg.encode())
				peer_socket.close()
				
				TTL = setNumber(int(TTL) - 1)
				if int(TTL) > 0:

					msg = "NEAR" + Pktid + IPP2P.ljust(55) + str(PP2P).ljust(5) + str(TTL)
					self.dbReader.execute("SELECT IPP2P, PP2P FROM user WHERE IPP2P!=? and IPP2P!=?", (IPP2P,self.myIPP2P,))
					resultUser = self.dbReader.fetchall()
					
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
				
			elif command == "ANEA":
				#verifica che la differnza del time stamp del packet id sia minore di 300
				Pktid = connection.recv(16).decode()
				IPP2P = connection.recv(55).decode()
				PP2P = connection.recv(5).decode()
			
				#verifico se l'utente è già salvato nel db oppure lo aggiungo
				self.dbReader.execute("SELECT IPP2P FROM user WHERE IPP2P=?", (IPP2P,))
			
				data = self.dbReader.fetchone() #retrieve the first row
				if data is None:
					self.dbReader.execute("INSERT INTO user (IPP2P, PP2P) values (?, ?)",(IPP2P, PP2P))
					print(color.green + "Aggiunto nuovo user" + color.end)
				else:
					print(color.fail + "User già presente" + color.end)	
			
					
		except:
			connection.close()
			return False
				
		
if __name__ == "__main__":
    gnutella = GnutellaServer()
gnutella.server()

