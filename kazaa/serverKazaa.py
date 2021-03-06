import socket, sqlite3, string, subprocess, threading, os, random, ipaddress, time, datetime, hashlib, sys, stat
import setting as var
from threading import Timer
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
	self.dbReader.execute("CREATE TABLE File (Filemd5 text, Filename text, SessionID text)")
	self.dbReader.execute("CREATE TABLE download (Filemd5 text, Filename text)")
	self.dbReader.execute("CREATE TABLE TrackedFile (IPP2P text, PP2P text, Filemd5 text, Filename text)")
    
def PktidGenerator():
	return "".join(choice(string.ascii_letters + string.digits) for x in range(16))

def setNumber(n):
	if n < 10:
		n = "0"+str(n)
	return n

def setCopy(copy):
	if copy > 1000:
		copy = 999
	elif copy < 100 and copy > 9:
		copy = "0"+str(copy)
	elif copy < 10:
		copy = "00"+str(copy)
	return copy
	
def setIp(n):
	if n < 10:
		n = "00"+str(n)
	elif n < 100:
		n = "0"+str(n)
	return n
	
def setIPv6(n):
	if n < 10:
		n = "000"+str(n)
	elif n < 100:
		n = "00"+str(n)
	elif n < 1000:
		n = "0"+str(n)
	return n


def progBar(i):
	i = i+1
	bar_length = 60
	hashes = '#' * i * 3
	spaces = ' ' * (bar_length - len(hashes))
	sys.stdout.write("\r[{0}] {1}s".format(hashes + spaces, int(i)))			

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
			print(color.green+"Connessione IPv4:"+ip+" PORT:"+str(port)+color.end)
			peer_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			peer_socket.connect((ip,port))		
		else:
			ip = ip[16:55]
			print(color.green+"Connetto con IPv6:"+ip+" PORT:"+str(port)+color.end);
			peer_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
			peer_socket.connect((ip, port))
		
		print("Invio --> "+color.send+msg+color.end)
		peer_socket.send(msg.encode())
		peer_socket.close()
	except:
		print("Nessun vicino trovato!")

def setNotCloseConnection(ip, port, msg):
	try:
		rnd = random()
		if(rnd<0.5):
			ip = splitIp(ip[0:15])						
			print(color.green+"Connessione IPv4:"+ip+ " PORT:"+str(port)+color.end)
			peer_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			peer_socket.connect((ip,port))

		else:
			ip = ip[16:55]
			print(color.green+"Connetto con IPv6:"+ip+" PORT:"+str(port)+color.end);
			peer_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
			peer_socket.connect((ip, port))

		print("Invio --> "+color.send+msg+color.end)
		peer_socket.sendall(msg.encode())
	except:
		print(color.fail+"Errore connessione 'not close'"+color.end)
	return peer_socket
	
def sendToSuper(self, messaggio):
	self.dbReader.execute("SELECT IPP2P, PP2P FROM user WHERE Super = ?",(2,))
	mySuper = self.dbReader.fetchone()
	setConnection(mySuper[0], 3000, messaggio)

def sessionIdGenerator():
	return "".join(choice(string.ascii_letters + string.digits) for x in range(16))
	

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


class Kazaa(object):
	def __init__(self):
		IP = ""
		self.PORT = var.Settings.PORT
		self.myIPP2P = var.Settings.myIPP2P
		self.UDP_IP = "127.0.0.1"
		UDP_PORT_SERVER = 49999
		self.UDP_PORT_CLIENT = 50000
		self.endUDP1 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
		self.endUDP2 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
		self.endUDP3 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
		self.timeDebug = var.Settings.timeDebug
		self.BUFF = 1024
		self.super = ""
		# Creo DB
		conn = sqlite3.connect(':memory:', check_same_thread=False)
		self.dbReader = conn.cursor()
		
		# Creo tabella user
		clearAndSetDB(self)
		
		# Mi inserisco nel DB
		self.dbReader.execute("INSERT INTO user (Super, IPP2P, PP2P) values(?, ?, ?) ",(0, self.myIPP2P, self.PORT))
		
		self.super = 0

		
		# Socket ipv4/ipv6 port 3000
		self.server_address = (IP, int(self.PORT))
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
			
			if command == "IFSU":
				sup = str(self.sockUDPServer.recvfrom(1)[0].decode())
				if sup == "1":
					print("Loggato come root")
					self.dbReader.execute("UPDATE user set Super=? where IPP2P=?",(1, self.myIPP2P))
					self.super = 1
				
			elif command == "SETV":
				gruppo = str(self.sockUDPServer.recvfrom(3)[0].decode())
				numPc = str(self.sockUDPServer.recvfrom(3)[0].decode())
				port = str(self.sockUDPServer.recvfrom(5)[0].decode())
				ip = "172.016."+gruppo+"."+numPc
				ipv6 = "fc00:0000:0000:0000:0000:0000:"+setIPv6(int(gruppo))+":"+setIPv6(int(numPc))
				ip = ip+"|"+ipv6
				if ip != self.myIPP2P:
					self.dbReader.execute("INSERT INTO user (Super, IPP2P, PP2P) values(?, ?, ?) ",(0, ip, port))
				print(color.green + "NODO " + ip +" aggiunto con successo"+ color.end)	
				
			elif command == "SUPE":
				myPktid = PktidGenerator()
				self.dbReader.execute("INSERT INTO pktid (Pktid, Timestamp) values (?, ?)",(myPktid,datetime.datetime.now()))
				TTL = setNumber(4)
				self.dbReader.execute("SELECT IPP2P, PP2P FROM user")
				resultUser = self.dbReader.fetchall()
				msg = "SUPE" + myPktid + self.myIPP2P + str(self.PORT).ljust(5) + TTL
				
				for user in resultUser:
					setConnection(user[0], int(user[1]), msg)
			
			elif command == "SETS":
				try:
					if self.super == 1:
						print("SETTO SUPERNODO -------------------------------------------------------> IP"+self.myIPP2P)
						self.dbReader.execute("UPDATE user SET Super=? where IPP2P=?",(2,self.myIPP2P))
						print(color.green + "SUPERNODO con IP:"+self.myIPP2P+" selezionato con successo"+ color.end)
					else:
						self.dbReader.execute("SELECT count(*) FROM user WHERE Super=?", (1,))
						data = self.dbReader.fetchone()
						print("Supernodi trovati:", data[0])
						rnd = randint(1, int(data[0])) - 1
						self.dbReader.execute("SELECT IPP2P FROM user where Super=? LIMIT 1 OFFSET ?", (1,rnd))

						data = self.dbReader.fetchone()
						print(data[0])
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
				self.dbReader.execute("SELECT SessionID FROM user where IPP2P=? AND Super = ?", (self.myIPP2P,0))
				sessionID = self.dbReader.fetchone()
				print(str(PATH))
				if os.path.isfile(PATH) and os.access(PATH, os.R_OK):
					filemd5 = encryptMD5(PATH)
					
					self.dbReader.execute("SELECT filename FROM File WHERE filemd5=?",(filemd5,))
					data = self.dbReader.fetchone()
					if data is None:
						self.dbReader.execute("INSERT INTO File (filemd5, filename, SessionID) values (?, ?, ?)", (filemd5, filename, sessionID[0]))
						print(color.green+"Trovato. Aggiunto file in condivisione"+color.end)
					else:
						self.dbReader.execute("UPDATE File SET filename=? WHERE filemd5=?",(filename,filemd5))
					
					msg = "ADFF" + sessionID[0] + filemd5 + filename
					sendToSuper(self, msg)
					msg = "1"
				else:
					msg = "0"
					print(color.fail+"File non presente. Impossibile aggiungerlo in condivisione"+color.end)
					
				self.sockUDPClient.sendto(msg.encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
			
			
			elif command == "DELF":
				filename, useless = self.sockUDPServer.recvfrom(100)
				filename = filename.decode()
				msg = ""
				
				try:
					PATH = var.Settings.userPath+filename.strip()
					filemd5 = encryptMD5(PATH)
					
					self.dbReader.execute("SELECT filename FROM File WHERE filemd5=?",(filemd5,))
					data = self.dbReader.fetchone()
				
					if data is None:
						msg = "0"
						print(color.fail+"File non presente. Impossibile rimuovere il file"+color.end)
					else:
						self.dbReader.execute("DELETE FROM File WHERE filemd5=?",(filemd5,))
						print(color.green+"Rimosso file dalla condivisione"+color.end)
					
						self.dbReader.execute("SELECT SessionID FROM user where IPP2P=? AND Super=?", (self.myIPP2P,0))
						sessionID = self.dbReader.fetchone()
					
						msg = "DEFF" + sessionID[0] + filemd5
						sendToSuper(self, msg)
						msg = "1"
				except:
					msg = "0"
					print(color.fail+"File non presente nella cartella. Errore"+color.end)
				
				self.sockUDPClient.sendto(msg.encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
			
			elif command == "FDWN":
				data, noused = self.sockUDPServer.recvfrom(20)
				filename = data.decode()
				filename = filename.strip()
				self.dbReader.execute("SELECT IPP2P, PP2P, Filemd5, Filename FROM TrackedFile WHERE Filename LIKE ?", ("%"+filename+"%",))
				files = self.dbReader.fetchall()
				for f in files:
					self.sockUDPClient.sendto((str(f[0].ljust(55))+"-"+str(f[1]).ljust(5)+"-"+str(f[2].ljust(32))+"-"+str(f[3].ljust(100))).encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
				self.sockUDPClient.sendto((self.endUDP3).encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
			
			elif command == "STMF":
				self.dbReader.execute("SELECT Filename, SessionID, Filemd5 FROM File")
				files = self.dbReader.fetchall()
				for f in files:
					self.sockUDPClient.sendto((f[0]+"-"+f[1]+"-"+f[2]).encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
				self.sockUDPClient.sendto((self.endUDP1).encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
			
			elif command == "STMP":
				self.dbReader.execute("SELECT * FROM User")
				files = self.dbReader.fetchall()
				for f in files:
					if(f[3] is None):
						self.sockUDPClient.sendto((f[0]+"-"+f[1]+"-"+f[2]+"-|--------------|").encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
					else:
						self.sockUDPClient.sendto((f[0]+"-"+f[1]+"-"+f[2]+"-"+f[3]).encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
				self.sockUDPClient.sendto((self.endUDP2).encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
			
			
			elif command == "FIND":
				self.dbReader.execute("DELETE FROM TrackedFile")
				self.dbReader.execute("SELECT SessionID FROM User WHERE IPP2P LIKE ? AND Super=?", (self.myIPP2P,0))
				sessionID = self.dbReader.fetchone()
				sessionID = sessionID[0]
				ricerca, useless = self.sockUDPServer.recvfrom(20)
				ricerca = ricerca.decode()
				msg = "FIND" + str(sessionID) + str(ricerca).ljust(20)
				self.dbReader.execute("SELECT IPP2P, PP2P FROM User WHERE Super = 2")
				superUser = self.dbReader.fetchone()
				print("Invio messaggio -> " + msg + " a " + superUser[0] + " Porta " +superUser[1])
				
				peer_socket = setNotCloseConnection(mySuper[0], 3000, msg)
				command = peer_socket.recv(4).decode()
				
				if command == "AFIN":
					self.dbReader.execute("DELETE FROM TrackedFile")
					print("Ricevuto " + color.recv + command + color.end)
					nIdMd5 = int(peer_socket.recv(3).decode())
					i=0
					while nIdMd5 > 0:
						filemd5 = peer_socket.recv(32).decode()
						filename = peer_socket.recv(100).decode()
						nCopie = int(peer_socket.recv(3).decode())
						while nCopie > 0:
							ipp2p = peer_socket.recv(55).decode()
							pp2p = peer_socket.recv(5).decode()
							i = i+1
							print("inserito: " + str(filename.strip()))
							self.dbReader.execute("INSERT INTO TrackedFile (Filename, Filemd5, Ipp2p, Pp2p) values (?,?,?,?)", (filename.strip(), filemd5, ipp2p, pp2p))
							nCopie = nCopie - 1
						nIdMd5 = nIdMd5 -1
					print("Trovati " + str(i)+" file" )
					self.dbReader.execute("SELECT * FROM TrackedFile")
					files = self.dbReader.fetchall()
					for f in files:
						print(f[0] + " - " + f[1] + " - " + f[2] + " - " + f[3])
				peer_socket.close()
			
			elif command == "LOGI":
				msg = "LOGI"+str(self.myIPP2P).ljust(55)+str(self.PORT).ljust(5)
				self.dbReader.execute("SELECT IPP2P, PP2P FROM user WHERE Super = ?",(2,))
				mySuper = self.dbReader.fetchone()
				peer_socket = setNotCloseConnection(mySuper[0], 3000, msg)
				command = peer_socket.recv(4).decode()
				if command == "ALGI":
					print("Ricevuto ALGI")
					try:
						SessionID = peer_socket.recv(16).decode()						
						#Aggiorno SessionID non sono un super, altrimenti mi aggiungo come user normale
						if self.super == 0:
							self.dbReader.execute("UPDATE user SET SessionID=? WHERE IPP2P=?",(SessionID,self.myIPP2P))
						else:
							self.dbReader.execute("INSERT INTO user (Super, IPP2P, PP2P, SessionID) values (?, ?, ?, ?)",(0, self.myIPP2P, self.PORT, SessionID))
						print(color.green + "SessionID salvato con successo"+ color.end)
						self.sockUDPClient.sendto(("LOG1").encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
					except:
						print(color.fail+"Errore salvataggio SessionID"+color.end)
						self.sockUDPClient.sendto(("LOG0").encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
				else:
					print(color.fail+"Login fallito!")
					self.sockUDPClient.sendto(("LOG0").encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
				peer_socket.close()


			elif command == "LOGO":
				#ottengo il mio sessionID dal db
				self.dbReader.execute("SELECT SessionID FROM User Where IPP2P = ? AND Super = ?",(self.myIPP2P,0))
				data = self.dbReader.fetchone()
				SessionID = data[0]
				#seleziono tutti gli utenti
				msg = "LOGO" + SessionID
				peer_socket = setNotCloseConnection(mySuper[0], 3000, msg)
				command = peer_socket.recv(4).decode()
				if command == "ALGO":
					nDeleted = peer_socket.recv(3).decode()
					print("Ricevuto " + color.recv + command + color.end + "\n#Copie " + color.recv + nDeleted + color.end)
					self.sockUDPClient.sendto((nDeleted.ljust(3)).encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
				
				peer_socket.close()
			
			
			elif command == "RETR":
				print("ricevuto RETR")
				filename, useless = self.sockUDPServer.recvfrom(20)
				filename = filename.decode()
				filename = filename.strip()
				cmd, addr = self.sockUDPServer.recvfrom(3)
				cmd = cmd.decode()
				
				#fix per offset
				cmd = int(cmd)-1
				
				#Recupero il file
				self.dbReader.execute("SELECT * FROM TrackedFile WHERE Filename LIKE ? LIMIT 1 OFFSET ?", ("%"+filename+"%",cmd ))
				resultFile = self.dbReader.fetchone()
				print("MD5 --> "+str(resultFile[2])+"  FILENAME --> "+str(resultFile[3]))
				if resultFile is not None:
					self.dbReader.execute("DELETE FROM Download")
					self.dbReader.execute("INSERT INTO Download values (?,?)", (resultFile[2], resultFile[3]))					
					msg = "RETR" + resultFile[2]
					
					#setConnection(resultFile[0], int(resultFile[1]), msg)
					peer_socket = setNotCloseConnection(resultFile[0], int(resultFile[1]), msg)
					command = peer_socket.recv(4).decode()
					
					if command == "ARET":
						print("Ricevuto "+color.recv+"ARET"+color.end)
						try:
							self.dbReader.execute("SELECT * FROM Download")
							files = self.dbReader.fetchone()
							filename = files[1]

							fd = open(var.Settings.userPath + "" + filename, 'wb')					
							numChunk = peer_socket.recv(6).decode()
							numChunk = int(numChunk)

							i = 0
							print("Inizio download...")
							bar_length = 60
							time1 = time.time()
							while i < numChunk:
								lun = peer_socket.recv(5).decode()
								while len(lun) < 5:
									lun = lun + peer_socket.recv(1).decode()
								lun = int(lun)
								data = peer_socket.recv(lun)
								while len(data) < lun:
									data += peer_socket.recv(1)
								fd.write(data)
								percent = float(i) / numChunk
								hashes = '#' * int(round(percent * bar_length))
								spaces = ' ' * (bar_length - len(hashes))
								sys.stdout.write("\rPercent: [{0}] {1}%".format(hashes + spaces, int(round(percent * 100))))
								i = i + 1
							
							percent = float(i) / numChunk
							hashes = '#' * int(round(percent * bar_length))
							spaces = ' ' * (bar_length - len(hashes))
							sys.stdout.write("\rPercent: [{0}] {1}%".format(hashes + spaces, int(round(percent * 100))))
							time2 = time.time()
							sys.stdout.flush()
							fd.close()
							print("\n")
							totTime = time2 - time1
							print(color.green + "Scaricato il file" + color.end+" in "+str(int(totTime))+"s")
							
						except OSError:
							print("Impossibile aprire il file: controlla di avere i permessi")
							self.sockUDPClient.sendto(("ARE0").encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
							return False
						print(color.fail+"Finito baby"+color.end)
						self.sockUDPClient.sendto(("ARE1").encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
					
					peer_socket.close()
				else:
					print("Errore nella procedura di download")			

			
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
						msg = "ASUP" + Pktid + self.myIPP2P.ljust(55) + str(self.PORT).ljust(5)
						print("dio stronzo")
						setConnection(IPP2P, int(PP2P), msg)
	
					TTL = setNumber(int(TTL) - 1)
		
					if int(TTL) > 0:
						msg = "SUPE" + Pktid + IPP2P.ljust(55) + str(PP2P).ljust(5) + str(TTL)
						self.dbReader.execute("SELECT IPP2P, PP2P FROM user WHERE IPP2P!=? and IPP2P!=?", (IPP2P,self.myIPP2P))
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
				t = self.dbReader.fetchone() #retrieve the first ro
				if getTime(t[0]) < 300:
					#verifico se l'utente super è già salvato nel db oppure lo aggiungo
					self.dbReader.execute("SELECT IPP2P FROM user WHERE IPP2P=?", (IPP2P,))
					data = self.dbReader.fetchone() 
					if data is None:
						self.dbReader.execute("INSERT INTO user (Super, IPP2P, PP2P) values (?, ?, ?)",(1, IPP2P, PP2P))
						print(color.green + "Aggiunto nuovo supernodo" + color.end)
					else:
						#verifico se ho salvato l'utente come user normale. In questo caso lo aggiorno come root
						self.dbReader.execute("UPDATE user SET Super=? where IPP2P=?",(1,data[0],))
						print(color.fail + "Aggiornato user "+str(data[0])+" in supernodo" + color.end)	
				else:
					print(color.fail+"ricevuto pacchetto dopo 20s"+color.end)
		
			# se sono un supernodo
			elif command == "LOGI":
				try:
					IPP2P = connection.recv(55).decode()
					PP2P = connection.recv(5).decode()
					print("Ricevuto " + color.recv + command + color.end + " da " + color.recv + IPP2P + color.end + " - " + color.recv + PP2P + color.end)
					self.dbReader.execute("SELECT SessionID FROM user WHERE IPP2P=?", (IPP2P,))
					data = self.dbReader.fetchone() #retrieve the first row
					if data is None:
						print(color.green + "Nuovo utente aggiunto" + color.end);
						SessionID = sessionIdGenerator()
						self.dbReader.execute("INSERT INTO user (Super, IPP2P, PP2P, SessionID) values (?, ?, ?, ?)",(0, IPP2P, PP2P, SessionID))
					else:
						print(color.fail + "Utente già presente" + color.end)
						if data[0] is None:
							#ho l'utente ma non ha ancora un SessionID quindi ne creo un e lo aggiungo
							SessionID = sessionIdGenerator()
							self.dbReader.execute("UPDATE user SET SessionID=? where IPP2P=?",(SessionID,IPP2P))
						else:
							SessionID = data[0]
				except:
					SessionID = "0000000000000000"
					Print("Errore nella procedura di login lato server")
				finally:
					msg = "ALGI"+SessionID

					#setConnection(IPP2P, int(PP2P), msg)
					connection.sendall(msg.encode())
					#connection.close()
				
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
					print(color.green+"Aggiornato filename"+color.end)
		
			elif command == "DEFF":
				SessionID = connection.recv(16).decode()
				Filemd5 = connection.recv(32).decode()
				print("Ricevuto "+ color.recv + command + color.end + " da " + color.recv + SessionID + color.end)
			
				#verifico che l'utente abbia il file
				self.dbReader.execute("SELECT * FROM file WHERE Filemd5=? AND SessionID=?", (Filemd5,SessionID,))
				data = self.dbReader.fetchone()
			
				if data is None:
					print(color.fail+ "Nessun file trovato" + color.end);
				else:
					self.dbReader.execute("DELETE FROM file WHERE Filemd5=? AND SessionID=?", (Filemd5,SessionID,))					
				
			elif command == "FIND":
				sessionID = connection.recv(16).decode()
				ricerca = connection.recv(20).decode()
				#seleziono tutti gli altri peer e ritrasmetto il messaggio
				self.dbReader.execute("SELECT IPP2P, PP2P FROM User WHERE Super LIKE ?", (1,))
				superUser = self.dbReader.fetchall()
				myPktid = PktidGenerator()
				self.dbReader.execute("INSERT INTO pktid (Pktid, Timestamp) values (?, ?)", (myPktid, datetime.datetime.now()))
				ttl = setNumber(4)
				#messaggio da ritrasmettere
				msg = "QUER" + str(myPktid) + str(self.myIPP2P) + str(self.PORT).ljust(5) + str(ttl) + str(ricerca)
				#controllo tra i miei file quali mettere in tracked file
				ricerca = ricerca.strip()
				self.dbReader.execute("SELECT DISTINCT f.Filemd5, u.IPP2P, u.PP2P, f.Filename FROM user as u JOIN file as f WHERE u.sessionId = f.sessionID AND Filename LIKE ?",("%"+ricerca+"%",) )
				resultFile = self.dbReader.fetchall()
				for f in resultFile:
					print("inserisco il file:" + f[0]+ "-" +f[1] + "-" + f[2]+ "-" + f[3])
					self.dbReader.execute("SELECT * FROM TrackedFile WHERE Filemd5=?", (f[0],))
					data = self.dbReader.fetchone()
					if data is None:
						self.dbReader.execute("INSERT INTO TrackedFile (Filemd5, IPP2P, PP2P, Filename) values (?,?,?,?)", (f[0], f[1], f[2],f[3]))
				#threading.Thread(target = self.serverTCP, args = (connection,client_address)).start()
				#invio la quer a tutti gli altri, leggo la porta dal db
				for s in superUser:
					setConnection(s[0],3000, msg)
				
				n = 0
				#wait 10 s
				print(color.green)
				while n < 20:
					progBar(n)
					time.sleep(self.timeDebug)
					n = n+1
				print(color.end)
					
				try:
					#sendAfin(self, sessionID,ricerca,connection)
					self.dbReader.execute("SELECT DISTINCT Filemd5, Filename FROM TrackedFile WHERE filename LIKE ?", ("%"+ricerca+"%", ))
					resultFile = self.dbReader.fetchall()
					#print("Num file trovati: " + str(len(resultFile)))
					msg = "AFIN" + setIp(len(resultFile))
					for f in resultFile:
						self.dbReader.execute("SELECT IPP2P, PP2P FROM TrackedFile WHERE Filemd5 LIKE ?", ("%" + f[0] + "%",))
						resultIP = self.dbReader.fetchall()
						msg = msg + str(f[0]).ljust(32) + str(f[1]).ljust(100) + str(setIp(len(resultIP)))
						for i in resultIP:
							msg = msg + str(i[0]).ljust(55)+ str(i[1]).ljust(5)
					self.dbReader.execute("SELECT IPP2P, PP2P FROM User WHERE SessionID LIKE ?", (sessionID,))
					ip = self.dbReader.fetchone()
					connection.sendall(msg.encode())
					connection.close()
					
					#self.dbReader.execute("DELETE FROM TrackedFile WHERE filename LIKE ?", ("%"+ricerca+"%",))
				except:
					print("ERRORE SEND NUDES")
				
			elif command == "LOGO":
				SessionID = connection.recv(16).decode()
				print("Ricevuto " + color.recv + command + color.end + " da " + color.recv + SessionID + color.end)
				#conto i file associati all'utente
				self.dbReader.execute("SELECT COUNT(Filemd5) from File where SessionID=?",(SessionID,))
				delete = self.dbReader.fetchone()
				nDeleted = int(delete[0])
				self.dbReader.execute("SELECT IPP2P, PP2P from User where SessionID=?",(SessionID,))
				data = self.dbReader.fetchone()
				IPP2P = data[0]
				PP2P = data[1]
				nDeleted = setCopy(nDeleted)
			
				#preparo il msg
				msg  = "ALGO"+str(nDeleted)
				self.dbReader.execute("DELETE FROM File WHERE SessionID=?", (SessionID,))
				self.dbReader.execute("DELETE FROM User WHERE SessionID=?", (SessionID,))
				#setConnection(IPP2P, int(PP2P), msg)
				connection.sendall(msg.encode())

			elif command == "QUER":
				pktId = connection.recv(16).decode()
				ipp2p = connection.recv(55).decode()
				pp2p = connection.recv(5).decode()
				ttl = connection.recv(2).decode()
				ricerca = connection.recv(20).decode()
				print("Ricevuto " + color.recv + command + color.end + " da " + ipp2p)
				self.dbReader.execute("SELECT * FROM Pktid WHERE Pktid LIKE ?", (pktId,))
				resultPkt = self.dbReader.fetchone()
				#elaboro la richiesta se non ho il pktid
				if resultPkt is None:
					self.dbReader.execute("INSERT INTO Pktid (Pktid, timestamp) values (?, ?)", (pktId, datetime.datetime.now()))
					self.dbReader.execute("SELECT * FROM File WHERE Filename LIKE ?", ("%"+ricerca.strip()+"%",))
					resultFile = self.dbReader.fetchall()
					msg = "AQUE" + pktId
					#invio le aque a chi mi ha fatto la richiesta
					for f in resultFile:
						self.dbReader.execute("SELECT IPP2P, PP2P FROM user where SessionID=? AND Super=?", (f[2],0))
						data = self.dbReader.fetchone()
						personalizeMsg = msg + data[0].ljust(55) + data[1].ljust(5) + f[0].ljust(32) + f[1].ljust(100)
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
				print("Ricevuto " + color.recv + command + color.end)
				pktid = connection.recv(16).decode()
				ipp2p = connection.recv(55).decode()
				pp2p = connection.recv(5).decode()
				filemd5 = connection.recv(32).decode()
				filename = connection.recv(100).decode()
			
				self.dbReader.execute("SELECT Timestamp FROM pktid WHERE Pktid=?", (pktid,))
				t = self.dbReader.fetchone() #retrieve the first row
				if getTime(t[0]) < 20:
					#se il pacchetto esiste faccio quello che devo fare
					self.dbReader.execute("INSERT INTO TrackedFile (IPP2P, PP2P, Filemd5, Filename) values (?, ?, ?, ?)", (ipp2p, pp2p, filemd5, filename))
					print("Inserito " + filename + " con md5 " + filemd5)
		
			elif command == "RETR":
				print("Ricevuto "+color.recv+"RETR"+color.end)
			
				#inviare un file che ho
				FileMD5 = connection.recv(32).decode()
				print("FileMD5", FileMD5)
				self.dbReader.execute("SELECT Filename FROM File WHERE FileMD5 = ?",(FileMD5,))
				resultFile = self.dbReader.fetchone()
				filename=resultFile[0].replace(" ","")
			
				try:
					fd = os.open(var.Settings.userPath+""+filename, os.O_RDONLY)
				except OSError as e:
					print(e)
				if fd is not -1:
					filesize = int(os.path.getsize(var.Settings.userPath+""+filename))
					num = int(filesize) / self.BUFF
					if (filesize % self.BUFF)!= 0:
						num = num + 1
				
					num = int(num)
					msg = "ARET" + str(num).zfill(6)
					
					print ('Trasferimento iniziato di ', resultFile[0], ' [BYTES ', filesize, ']')
					#funzione progressBar
					connection.send(msg.encode())
					i = 0
					while i < num:
						buf = os.read(fd,self.BUFF)
						
						if not buf: break
						lbuf = len(buf)
						lbuf = str(lbuf).zfill(5)
						connection.send(lbuf.encode())
						connection.send(buf)
						i = i + 1
					
					os.close(fd)
					print(color.green+"\nFine UPLOAD"+color.end)					
					connection.close()
				else: 
					print("Il file non esiste!")
			
				
		except:
			connection.close()
			return False

if __name__ == "__main__":
    gnutella = Kazaa()
gnutella.server()
