import socket, sqlite3, string, subprocess, threading, os, random, ipaddress, time, datetime, hashlib, sys, stat
import setting as var
from random import *

class color:
	HEADER = '\033[95m'
	recv = '\033[36m'
	green = '\033[32m'
	send = '\033[33m'
	fail = '\033[31m'
	end = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

def clearAndSetDB(self):
	self.dbReader.execute("DROP TABLE IF EXISTS User")
	self.dbReader.execute("DROP TABLE IF EXISTS Pktid")
	self.dbReader.execute("DROP TABLE IF EXISTS File")
	self.dbReader.execute("DROP TABLE IF EXISTS download")
	self.dbReader.execute("DROP TABLE IF EXISTS TrackedFile")
	# 0 -> user
	# 1 -> supernodo
	# 2 -> supernodo scelto	
	self.dbReader.execute("CREATE TABLE User (Super text, IPP2P text, PP2P text, SessionID text)")
	self.dbReader.execute("CREATE TABLE Pktid (Pktid text, Timestamp DATETIME)")
	self.dbReader.execute("CREATE TABLE File (Filemd5 text, Filename text, IPP2P text, SessionID text)")
	self.dbReader.execute("CREATE TABLE download (Filemd5 text, Filename text)")
	self.dbReader.execute("CREATE TABLE TrackedFile (IPP2P text, PP2P text, Filemd5 text, Filename text)")
    
def PktidGenerator():
	return "".join(choice(string.ascii_letters + string.digits) for x in range(16))

def setNumber(n):
	if n < 10:
		n = "0"+str(n)
	return n

def setIp(n):
	if n < 10:
		n = "00"+str(n)
	elif n < 100:
		n = "0"+str(n)
	return n

def splitIp(ip):
	splitted = ip.split(".")
	ip = str(int(splitted[0]))+"."+str(int(splitted[1]))+"."+str(int(splitted[2]))+"."+str(int(splitted[3]))
	return ip
	
def encryptMD5(filename):
	#calcolo hash file
	BLOCKSIZE = 128
	hasher = hashlib.md5()
	with open(filename, 'rb') as f:
		buf = f.read(BLOCKSIZE)
		while len(buf) > 0:
			hasher.update(buf)
			buf = f.read(BLOCKSIZE)
		f.close()
	filemd5 = hasher.hexdigest()
	return(filemd5)	

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

def sendToSuper(self,messaggio):
	self.dbReader.execute("SELECT IPP2P, PP2P FROM user WHERE Super = ?",(2,))
	mySuper = self.dbReader.fetchone()
	print("Ciao:  ", messaggio)
	setConnection(mySuper[0], int(mySuper[1]), messaggio)

def getTime(t):
	a = str(datetime.datetime.now())

	ht = int(t.split(" ")[1].split(":")[0]) * 60 * 60
	mt = int(t.split(" ")[1].split(":")[1]) * 60
	st = int(t.split(" ")[1].split(":")[2].split(".")[0])
	time1 = ht + mt + st
	
	ha = int(a.split(" ")[1].split(":")[0]) * 60 * 60
	ma = int(a.split(" ")[1].split(":")[1]) * 60
	sa = int(a.split(" ")[1].split(":")[2].split(".")[0])
	time2 = ha + ma + sa
	return time2 - time1

def sendAfin(sessionID):
	self.dbReader.execute("SELECT DISTINC Filemd5, Filename FROM TrackedFile")
	resultFile = self.dbReader.fetchall()
	lunMd5 = len(resultFile)
	msg = "AFIN" + setIp(lunMd5)
	for f in resultFile:
		
		self.dbReader.execute("SELECT IPP2P, PP2P FROM TrackedFile WHERE IPP2P", (resultFile[0],))
		resultIP = self.dbReader.fetchall()
		msg = msg + resultFile[0] + resultFile[1] + setIp(resultIp)
		for i in resultIP:
			msg = resultIP[0] + resultIP[1]
	
	self.dbReader.execute("SELECT IPP2P, PP2P FROM User WHERE SessionID LIKE ?", (sessionID,))
	ip = self.dbReader.fetchone()
	
	setConnection(ip[0], int(ip[1]), msg)

class Kazaa(object):
	def __init__(self):
		IP = ""
		self.PORT = var.Settings.PORT
		self.myIPP2P = var.Settings.myIPP2P
		self.UDP_IP = "127.0.0.1"
		UDP_PORT_SERVER = 49999
		self.UDP_PORT_CLIENT = 50000
		self.endUDP1 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx";
		self.BUFF = 99999
		
		self.super = ""
		# Creo DB
		conn = sqlite3.connect(':memory:', check_same_thread=False)
		self.dbReader = conn.cursor()
		
		# Creo tabella user
		clearAndSetDB(self)
		
		#Setto i supernodi noti
		#self.dbReader.execute("INSERT INTO user (Super, IPP2P, PP2P) values(?, ?, ?) ",(1, "192.168.043.012|fe80:0000:0000:0000:8888:4887:b7f4:9999",5000))
	
		if self.myIPP2P != var.Settings.root_IP:
			self.dbReader.execute("INSERT INTO user (Super, IPP2P, PP2P) values(?, ?, ?) ",(0, var.Settings.root_IP,var.Settings.root_PORT))
			self.super = 0
		else:
			print("Loggato come root")
			self.dbReader.execute("INSERT INTO user (Super, IPP2P, PP2P) values(?, ?, ?) ",(1, var.Settings.root_IP,var.Settings.root_PORT))
			self.super = 1
		
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
		
		
	def server(self):
		#crea thread interno per far comunicare client e server
		threading.Thread(target = self.serverUDP, args = '').start()
		
		print(color.green+"In attesa di connessione esterna..."+color.end)
		while True:
			try:
				connection, client_address = self.sock.accept()
				threading.Thread(target = self.serverTCP, args = (connection,client_address)).start()
			except:
				return False
	
	
	def serverUDP(self):
		print(color.green+"In attesa di comandi interni..."+color.end)
		while True:
			data, addr = self.sockUDPServer.recvfrom(4)
			command = data.decode()
			print("\n\nRicevuto comando dal client: "+color.recv+command+color.end)
			
			if command == "SUPE":
				myPktid = PktidGenerator()
				self.dbReader.execute("INSERT INTO pktid (Pktid, Timestamp) values (?, ?)",(myPktid,datetime.datetime.now()))
				TTL = setNumber(4)
				self.dbReader.execute("SELECT IPP2P, PP2P FROM user")
				resultUser = self.dbReader.fetchall()
				msg = "SUPE" + myPktid + self.myIPP2P + str(self.PORT).ljust(5) + TTL
				for user in resultUser:
					setConnection(user[0], int(user[1]), msg)
			
			elif command == "LOGI":
				msg = "LOGI"+str(self.myIPP2P).ljust(55)+str(self.PORT).ljust(5)
				sendToSuper(self, msg)
			
			elif command == "SETS":
				try:
					# scelgo random tra i supernodi
					self.dbReader.execute("SELECT count(*) FROM user WHERE Super=?", (1,))
					data = self.dbReader.fetchone()
					print("Supernodi trovati:", data[0])
					rnd = randint(1, int(data[0])) - 1
					self.dbReader.execute("SELECT IPP2P FROM user LIMIT 1 OFFSET ?", (rnd,))
					data = self.dbReader.fetchone()
					self.dbReader.execute("UPDATE user SET Super=? where IPP2P=?",(2,data[0]))
					print(color.green + "SUPERNODO con IP:"+data[0]+" selezionato con successo"+ color.end)
					self.sockUDPClient.sendto(("SET1").encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
				except: 
					print(color.fail+"Errore SET supernodo"+color.end)
					self.sockUDPClient.sendto(("SET0").encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
					self.sockUDPServer.close()
					self.sockUDPClient.close()
					os._exit(0)
			
			elif command == "ADDF":
				filename, useless = self.sockUDPServer.recvfrom(100)
				filename = filename.decode()
				print("-"+filename+"-")
				
				PATH = var.Settings.userPath+filename.strip()
				
				self.dbReader.execute("SELECT SessionID FROM user where IPP2P=?", (self.myIPP2P,))
				sessionID = self.dbReader.fetchone()
				
				if os.path.isfile(PATH) and os.access(PATH, os.R_OK):
					filemd5 = encryptMD5(PATH)
					msg = "1"
					self.dbReader.execute("INSERT INTO File (filemd5, filename, SessionID) values (?, ?, ?)", (filemd5, filename, sessionID[0]))
					print(color.green+"Trovato. Aggiunto file in condivisione"+color.end)
				else:
					msg = "0"
					print(color.fail+"File non presente. Impossibile aggiungerlo in condivisione"+color.end)

					
				self.sockUDPClient.sendto(msg.encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
				
				msg = "ADFF" + sessionID[0] + filemd5 + filename
				sendToSuper(self, msg)
				print("Invio -> "+color.recv+msg+color.end)
				
			
			
			elif command == "STMF":
				
				self.dbReader.execute("SELECT SessionID FROM User where IPP2P=?", (self.myIPP2P,))
				sessionID = self.dbReader.fetchone()

				self.dbReader.execute("SELECT Filename, SessionID, Filemd5 FROM File WHERE SessionID=?", (sessionID[0],))
				files = self.dbReader.fetchall()
				for f in files:
					self.sockUDPClient.sendto((f[0]+"-"+f[1]+"-"+f[2]).encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
				self.sockUDPClient.sendto((self.endUDP1).encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
			
			
			
			elif command == "FIND":
				self.dbReader.execute("SELECT SessionID FROM User WHERE IPP2P LIKE ?", (self.myIPP2P,))
				sessionID = self.dbReader.fetchone()
				sessionID = sessionID[0]
				ricerca, useless = self.sockUDPServer.recvfrom(20).decode()
				msg = "FIND" + str(sessionID) + str(ricerca)
				self.dbReader.execute("SELECT IPP2P, PP2P FROM User WHERE Super = 2")
				superUser = self.dbReader.fetchone()
				print("Invio messaggio -> " + msg)
					
				setConnection(superUser[0], int(superUser[1]), msg)


			
			elif command == "LOGO":
				#ottengo il mio sessionID dal db
				self.dbReader.execute("SELECT SessionID FROM User Where IPP2P = ?",(self.myIPP2P,))
				data = self.dbReader.fetchone()
				SessionID = data[0]
				#seleziono tutti gli utenti
				msg = "LOGO" + SessionID
				sendToSuper(self, msg)

			elif command == "STOP":
				print(color.fail+"Server fermato"+color.end)
				self.sockUDPServer.close()
				self.sockUDPClient.close()
				os._exit(0)

	def serverTCP(self, connection, client_address):
		command = connection.recv(4).decode()
		try:
			if command == "SUPE":
				print("Ricevuto "+color.recv+"SUPE"+color.end)
				Pktid = connection.recv(16).decode()
				IPP2P = connection.recv(55).decode()
				PP2P = connection.recv(5).decode()
				TTL = connection.recv(2).decode()
				self.dbReader.execute("SELECT Timestamp FROM pktid WHERE Pktid=?", (Pktid,))
				t = self.dbReader.fetchone()
				if t is None:
					self.dbReader.execute("INSERT INTO pktid (Pktid, Timestamp) values (?, ?)",(Pktid,datetime.datetime.now()))
					self.dbReader.execute("SELECT IPP2P FROM user WHERE IPP2P=?", (IPP2P,))
					data = self.dbReader.fetchone()
					if data is None:
						#aggiungo l'utente come user
						self.dbReader.execute("INSERT INTO user (Super, IPP2P, PP2P) values (?, ?, ?)",(0, IPP2P, PP2P))
						print(color.green + "Aggiunto nuovo user" + color.end)
					else:
						print(color.fail + "User già presente" + color.end)
				
					if self.super == 1:
						print("Sono un supernodo e rispondo alla richiesta") 
						msg = "ASUP" + Pktid + self.myIPP2P.ljust(55) + str(self.PORT).ljust(5)
						setConnection(IPP2P, int(PP2P), msg)
		
					TTL = setNumber(int(TTL) - 1)
			
					if int(TTL) > 0:
						msg = "SUPE" + Pktid + IPP2P.ljust(55) + str(PP2P).ljust(5) + str(TTL)
						self.dbReader.execute("SELECT IPP2P, PP2P FROM user WHERE IPP2P!=? and IPP2P!=?", (IPP2P,self.myIPP2P,))
						resultUser = self.dbReader.fetchall()
			
						for user in resultUser:
							setConnection(user[0], int(user[1]), msg)
				
			elif command == "ASUP":
				print("Ricevuto "+color.recv+"ASUP"+color.end)
				Pktid = connection.recv(16).decode()
				IPP2P = connection.recv(55).decode()
				PP2P = connection.recv(5).decode()
				
				#verifico se c'è il pktid			
				self.dbReader.execute("SELECT Timestamp FROM pktid WHERE Pktid=?", (Pktid,))
				t = self.dbReader.fetchone() #retrieve the first row
				if getTime(t[0]) < 20:
					#verifico se l'utente super è già salvato nel db oppure lo aggiungo
					self.dbReader.execute("SELECT IPP2P FROM user WHERE IPP2P=?", (IPP2P,))

					data = self.dbReader.fetchone() 
					if data is None:
						self.dbReader.execute("INSERT INTO user (Super, IPP2P, PP2P) values (?, ?)",(1, IPP2P, PP2P))
						print(color.green + "Aggiunto nuovo supernodo" + color.end)
					else:
						#verifico se ho salvato l'utente come user normale. In questo caso lo aggiorno come root
						self.dbReader.execute("UPDATE user SET Super=? where IPP2P=?",(1,data[0],))
						print(color.fail + "Aggiornato user in supernodo" + color.end)	
				else:
					print(color.fail+"ricevuto pacchetto dopo 20s"+color.end)
			
			# se sono un supernodo
			elif command == "LOGI":
				try:
					IPP2P = connection.recv(55).decode()
					PORT = connection.recv(5).decode()
					print("Ricevuto " + color.recv + command + color.end + " da " + color.recv + IPP2P + color.end + " - " + color.recv + IPP + color.end)
					self.dbReader.execute("SELECT SessionID FROM user WHERE IPP2P=?", (IPP2P,))
					data = self.dbReader.fetchone() #retrieve the first row
					if data is None:
						print(color.green + "NUOVO UTENTE" + color.end);
						SessionID = sessionIdGenerator()
						self.dbReader.execute("INSERT INTO user (Super, IPP2P, PP2P, SessionID) values (?, ?, ?)",(0, IPP2P, PORT, SessionID))
					else:
						print(color.fail + "UTENTE GIÀ PRESENTE" + color.end)
						SessionID = str(data[0])
				except:
					SessionID = "0000000000000000"
				finally:
					connection.sendall(("ALGI"+SessionID).encode())
					
			elif command == "ADFF":
				SessionID = connection.recv(16).decode()
				print("Ricevuto "+ color.recv + command + color.end + " da " + color.recv + SessionID + color.end)
				Filemd5 = connection.recv(32).decode()
				Filename = connection.recv(100).decode()
			
				self.dbReader.execute("SELECT SessionID from File where Filemd5=? and SessionID=?",(Filemd5,SessionID,))
				data = self.dbReader.fetchone()
			
				if data is None:
					self.dbReader.execute("INSERT INTO File (Filemd5, Filename, SessionID) values (?, ?, ?)",(Filemd5, Filename, SessionID))
					print(color.green+"File aggiunto con successo"+color.end)
				else:
					self.dbReader.execute("UPDATE File SET Filename=? where Filemd5=?",(Filename,Filemd5,))
					print(color.fail+"File già presente"+color.end)
					print(color.green+"Aggiornato filename"+color.end)
					
			elif command == "FIND":
				sessionID = connection.recv(16).decode()
				ricerca = connection.recv(20).decode()
				self.dbReader.execute("SELECT IPP2P, PP2P FROM User WHERE Super = 1 AND IPP2P != ", (self.myIPP2P,)) #da controllare
				superUser = self.dbReader.fetchall()
				myPktid = PktidGenerator()
				self.dbReader.execute("INSERT INTO pktid (Pktid, Timestamp) values (?, ?)", (myPktid, datetime.datetime.now()))
				ttl = setNumber(4)
				msg = "QUER" + str(myPktId) + self.myIPP2P + self.myPort + ttl + ricerca
				t = (20.0, sendAfin(sessionID))
				t.start()
				for s in superUser:
					setConnection(superUser[0], int(superUser[1]), msg)
				
			elif command == "ALGI":
				try:
					SessionID = connection.recv(16).decode()
					#Mi inserisco nel db
					self.dbReader.execute("INSERT INTO user (Super, IPP2P, PP2P, SessionID) values (?, ?, ?)",(0, self.myIPP2P, self.PORT, SessionID))
					print(color.green + "Session salvato con successo"+ color.end)
					self.sockUDPClient.sendto(("LOG1").encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
				except:
					print(color.fail+"Errore salvataggio SessionID"+color.end)
					self.sockUDPClient.sendto(("LOG0").encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
					
			elif command == "LOGO":
				SessionID = connection.recv(16).decode()
				print("Ricevuto " + color.recv + command + color.end + " da " + color.recv + SessionID + color.end)
				#conto i file associati all'utente
				self.dbReader.execute("SELECT COUNT(Filemd5) from File where SessionID=?",(SessionID,))
				delete = self.dbReader.fetchone()
				delete = int(delete[0])
				delete = setNumber(delete)
				self.dbReader.execute("DELETE FROM File WHERE SessionID=?", (SessionID,))
				self.dbReader.execute("DELETE FROM User WHERE SessionID=?", (SessionID,))
				print("Invio --> "+ color.send + "ALGO" + delete + color.end)
				connection.sendall(("ALGO"+delete.ljust(3)).encode())
				connection.close()

			elif command == "ALGO":
				nDeleted = connection.recv(3).decode()
				print("Ricevuto " + color.recv + command + color.end + " da " + color.recv + SessionID + color.end)
				#self.sockUDPClient.sendto(("ALGO"+nDeleted.ljust(3)).encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
			
			elif command == "QUER":
				pktId = connection.recv(16).decode()
				ipp2p = connection.recv(55).decode()
				pp2p = connection.recv(5).decode()
				ttl = connection.recv(2).decode()
				ricerca = connection.recv(20).decode()
				
				self.dbReader.execute("SELECT * FROM Pktid WHERE Pktid LIKE ?", (pktId,))
				resultPkt = self.dbReader.fetchall()
				
				#elaboro la richiesta se non ho il pktid
				if resultPkt is None:
					self.dbReader.execute("INSER INTO Pktid (Pktid, timestamp) values (?, ?)", (pktId, datetime.datetime.now()))
					self.dbReader.execute("SELECT * FROM File WHERE Filename LIKE ?", (ricerca,))
					resultFile = self.dbReader.fetchall()
					msg = "AQUE" + pktId
					
					#invio le aque a chi mi ha fatto la richiesta
					for f in resultFile:
						self.dbReader.execute("SELECT PP2P FROM User WHERE IPP2P = ?", (f[2],))
						port = self.dbReader.fetchone()
						personalizeMsg = msg + f[2] + port + f[0] + f[1]
						setConnection(ipp2p, int(pp2p), personalizeMsg)
					
					#controllo il ttl per la ritrasmissione della richiesta
					if int(ttl) > 1:
						ttl = setNumber(int(ttl) - 1)
						self.dbReader.execute("SELECT * User WHERE Super = 1")
						resultSuper = self.dbReader.fetchall()
						#ritrasmetto a tutti i super
						for s in resultSuper:
							setConnection (s[0], int(s[1]), "QUER" + pktId + ipp2p + pp2p + ttl + ricerca)
			
			elif command == "AQUE":
				pktid = connection.recv(16).decode()
				ipp2p = connection.recv(55).decode()
				pp2p = connection.recv(5).decode()
				filemd5 = connection.recv(32).decode()
				filename = connection.recv(100).decode()
				
				self.dbReader.execute("SELECT Timestamp FROM pktid WHERE Pktid=?", (Pktid,))
				t = self.dbReader.fetchone() #retrieve the first row
				if getTime(t[0]) < 20:
					#se il pacchetto esiste faccio quello che devo fare
					self.dbReader.execute("INSERT INTO TrackedFile (IPP2P, PP2P, Filemd5, Filename) values (?, ?, ?, ?)", (ipp2p, pp2p, filemd5, filename))
					
		except:
			connection.close()
			return False
	
	
		
if __name__ == "__main__":
    gnutella = Kazaa()
gnutella.server()
