import socket, sqlite3, string, subprocess, threading, os, random, ipaddress, time


import settings as var

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

def setConnection(ip, port, msg):
	try:
		rnd = random()
		rnd = 0.1
		if(rnd<0.5):
			ip = splitIp(ip[0:15])						
			print(color.green+"Connessione IPv4:"+ip+color.end)
			peer_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			peer_socket.connect((ip,port))
		
		else:
			ip = ip[16:55]
			print(color.green+"Connetto con IPv6:"+ip+" PORT:"+str(port)+color.end);
			peer_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
			peer_socket.connect((ip, port))
		
		print("Invio --> "+color.send+msg+color.end)
		peer_socket.sendall(msg.encode())
		peer_socket.close()
	except:
		print("Nessun vicino trovato!")


class GnutellaServer(object):
	def __init__(self):
		IP = ""
		self.PORT = var.Settings.PORT
		self.myIPP2P = var.Settings.myIPP2P
		self.UDP_IP = "127.0.0.1"
		UDP_PORT_SERVER = 49999
		self.UDP_PORT_CLIENT = 50000
		self.endUDP1 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx";
		self.endUDP2 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx";
		
		# Creo DB
		conn = sqlite3.connect(':memory:', check_same_thread=False)
		self.dbReader = conn.cursor()
		
		# Creo tabella user
		clearAndSetDB(self)
		
		#inserisco l'utente root
		if self.myIPP2P != var.Settings.root_IP:
			self.dbReader.execute("INSERT INTO user (IPP2P, PP2P) values ('"+var.Settings.root_IP+"', '"+var.Settings.root_PORT+"')")
		else:
			print("Loggato come root")
		
		# Socket ipv4/ipv6 port 3000
		self.server_address = (IP, self.PORT)
		self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind(self.server_address)
		self.sock.listen(5)
		
		# socket upd ipv4 internal Server
		self.sockUDPServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sockUDPServer.bind((self.UDP_IP, UDP_PORT_SERVER))
		
		# socket upd ipv4 client in uscita
		self.sockUDPClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	
	def internalServer(self):
		print(color.green+"In attesa di comandi interni..."+color.end)
		while True:
			data, addr = self.sockUDPServer.recvfrom(4)
			command = data.decode()
			print("\n\nRicevuto comando dal client: "+color.recv+command+color.end)
			if command == "NEAR":
				myPktid = PktidGenerator()
				TTL = setNumber(2)
				self.dbReader.execute("SELECT IPP2P, PP2P FROM user")
				resultUser = self.dbReader.fetchall()
				msg = "NEAR" + myPktid + self.myIPP2P + str(self.PORT).ljust(5) + TTL
				for user in resultUser:
					setConnection(user[0], int(user[1]), msg)
					
			elif command == "QUER":
				print("\n\nRicevuto comando dal client: "+color.recv+command+color.end)
				threading.Thread(target = self.attesaRicerca, args = (data,addr)).start()
				ricerca = self.sockUDPServer.recvfrom(20)
				
				
			elif command == "RETR":
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
						self.sock.sendto(lunghezza).encode(), (self.UDP_IP, selfUDP_PORT))
						
					files[i] = (result[0], result[1], result[2])
					print(i + " - " + result[1])
					self.sock.sendto((result[1]).encode(), (self.UDP_IP, self.UDP_PORT))

				code = self.sockUDPServer.recvfrom(2)
				
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
					
			elif command == "RETR":
				print("\n\nRicevuto comando dal client: "+color.recv+command+color.end)
			
			
			
			elif command == "STMF":
				self.dbReader.execute("SELECT * FROM File")
				files = self.dbReader.fetchall()
				for f in files:
					self.sockUDPClient.sendto((f[0]+"-"+f[1]+"-"+f[2]).encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
				self.sockUDPClient.sendto((self.endUDP2).encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
				
			elif command == "STMV":
				if False: #questo è da rimuovere
					self.dbReader.execute("SELECT * FROM user")
					vicini = self.dbReader.fetchall()
					for v in vicini:
						self.sockUDPClient.sendto((v[0]+"-"+v[1]).encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
				self.sockUDPClient.sendto((self.endUDP1).encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
				
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
		command = connection.recv(4).decode()
		try:
			if command == "NEAR":
				Pktid = connection.recv(16).decode()
				IPP2P = connection.recv(55).decode()
				PP2P = connection.recv(5).decode()
				TTL = connection.recv(2).decode()
				
				self.dbReader.execute("SELECT IPP2P FROM user WHERE IPP2P=?", (IPP2P,))
				data = self.dbReader.fetchone()
				if data is None:
					self.dbReader.execute("INSERT INTO user (IPP2P, PP2P) values (?, ?)",(IPP2P, PP2P))
					print(color.green + "Aggiunto nuovo user" + color.end)
				else:
					print(color.fail + "User già presente" + color.end)
				
				msg = "ANEA" + Pktid + self.myIPP2P.ljust(55) + str(self.PORT).ljust(5)
				setConnection(IPP2P, int(PP2P), msg)
				
				
				
				
				
				TTL = setNumber(int(TTL) - 1)
				if int(TTL) > 0:
					msg = "NEAR" + Pktid + IPP2P.ljust(55) + str(PP2P).ljust(5) + str(TTL)
					self.dbReader.execute("SELECT IPP2P, PP2P FROM user WHERE IPP2P!=? and IPP2P!=?", (IPP2P,self.myIPP2P,))
					resultUser = self.dbReader.fetchall()
					
					for user in resultUser:
						setConnection(user[0], int(user[1]), msg)
				
				
				
				
				
				
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
				print("Ricevuto ANEA")
				'''********************************************************************************
				#verifica che la differnza del time stamp del packet id sia minore di 300
				********************************************************************************'''
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

