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
	self.dbReader.execute("DROP TABLE IF EXISTS File")
	self.dbReader.execute("DROP TABLE IF EXISTS Parts")
	
	self.dbReader.execute("CREATE TABLE User (IPP2P text, PP2P text, SessionID text)")
	self.dbReader.execute("CREATE TABLE File (Filemd5 text, Filename text, SessionID text, Lenfile text, Lenpart text)")
	self.dbReader.execute("CREATE TABLE Parts (IPP2P text, PP2P text, Filemd5 text, IdParts text, Downloaded text)")
	#0 --> Parte non ancora scaricata
	#1 --> Parte scaricata con successo
	
	# ************** DA TOGLIERE ************* #	
	self.dbReader.execute("INSERT INTO File (Filemd5, filename,sessionId , lenfile, lenpart) values (?,?,?,?,?)", ("aaaabbbbccccddddeeeeffffgggghhhh", "PROVAAAAA", "okokokokokokokokokok", "500", "100"))
	self.dbReader.execute("INSERT INTO Parts (IPP2P, PP2P, Filemd5, IdParts, Downloaded) values (?,?, ?, ?, ?)", ("172.016.005.002|fc00:0000:0000:0000:0000:0000:0005:0002","50000", "aaaabbbbccccddddeeeeffffgggghhhh", "00000001", "0"))
	self.dbReader.execute("INSERT INTO Parts (IPP2P, PP2P, Filemd5, IdParts, Downloaded) values (?,?, ?, ?, ?)", ("172.016.005.002|fc00:0000:0000:0000:0000:0000:0005:0002","50000", "aaaabbbbccccddddeeeeffffgggghhhh", "00000002", "0"))
	self.dbReader.execute("INSERT INTO Parts (IPP2P, PP2P, Filemd5, IdParts, Downloaded) values (?,?, ?, ?, ?)", ("172.016.005.002|fc00:0000:0000:0000:0000:0000:0005:0002","50000", "aaaabbbbccccddddeeeeffffgggghhhh", "00000003", "0"))
	self.dbReader.execute("INSERT INTO Parts (IPP2P, PP2P, Filemd5, IdParts, Downloaded) values (?,?, ?, ?, ?)", ("172.016.005.003|fc00:0000:0000:0000:0000:0000:0005:0003","50000", "aaaabbbbccccddddeeeeffffgggghhhh", "00000001", "0"))
	self.dbReader.execute("INSERT INTO Parts (IPP2P, PP2P, Filemd5, IdParts, Downloaded) values (?,?, ?, ?, ?)", ("172.016.005.003|fc00:0000:0000:0000:0000:0000:0005:0003","50000", "aaaabbbbccccddddeeeeffffgggghhhh", "00000002", "0"))
	self.dbReader.execute("INSERT INTO Parts (IPP2P, PP2P, Filemd5, IdParts, Downloaded) values (?,?, ?, ?, ?)", ("172.016.005.004|fc00:0000:0000:0000:0000:0000:0005:0004","50000", "aaaabbbbccccddddeeeeffffgggghhhh", "00000001", "0"))
	self.dbReader.execute("INSERT INTO Parts (IPP2P, PP2P, Filemd5, IdParts, Downloaded) values (?,?, ?, ?, ?)", ("172.016.005.005|fc00:0000:0000:0000:0000:0000:0005:0005","50000", "aaaabbbbccccddddeeeeffffgggghhhh", "00000001", "0"))

	# **************************************** #		
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

def splitIp(ip):
	splitted = ip.split(".")
	ip = str(int(splitted[0]))+"."+str(int(splitted[1]))+"."+str(int(splitted[2]))+"."+str(int(splitted[3]))
	return ip

	
def encryptMD5(self, filename):
	#calcolo hash file
	BLOCKSIZE = 128
	hasher = hashlib.md5()
	with open(filename, 'rb') as f:
		buf = f.read(BLOCKSIZE)
		while len(buf) > 0:
			hasher.update(buf)
			buf = f.read(BLOCKSIZE)
		f.close()
	hasher.update(self.myIPP2P.encode())
	filemd5 = hasher.hexdigest()
	return(filemd5)
	
def setConnection(ip, port, msg):
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
	
def timerChunk():
	sec = 0
	while True:
		time.sleep(var.setting.timeDebug)
		sec = sec + var.setting.timeDebug
		if int(sec) == 10:
			sec = 0

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
	hasher.update((var.setting.myIPP2P).encode())
	filemd5IP = hasher.hexdigest()
	return(filemd5)	

class serverUDPhandler(object):
	def __init__(self):
		self.ServerIP = ""
		self.ServerPORT = 3000
		
		self.PORT = var.setting.PORT
		self.myIPP2P = var.setting.myIPP2P
		self.mySessionID = ""
		
		self.UDP_IP = "127.0.0.1"
		UDP_PORT_SERVER = 49999
		self.UDP_PORT_CLIENT = 50000
		self.UDP_END = ""
		self.timeDebug = var.setting.timeDebug
		self.BUFF = 1024
		self.lenPart = 262144
		
		# Creo DB
		conn = sqlite3.connect(':memory:', check_same_thread=False)
		self.dbReader = conn.cursor()
		
		# Creo tabella user
		clearAndSetDB(self)
		
		# Socket ipv4/ipv6 port 3000
		self.server_address = ("", int(self.PORT))
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
				threading.Thread(target = self.recvDownload, args = (connection,client_address)).start()
			except:
				return False
				
	def calcID(self, partList, nParts):
		if partList == 1:
			return nParts, (partList-1)
		else:
			idParts = nParts
			lenParts = 1
			while lenParts < partList:
				idParts = idParts - 1
				lenParts = lenParts * 2
			idParts = idParts + 1
			lenParts = lenParts/2	
			partList = partList - lenParts
			return idParts, partList
		
	def gettingParts(self, sessionID, filemd5):
		msg = "FCHU" + sessionID.ljust(16) + filemd5.ljust(32)
		peer_socket = setConnection(self.ServerIP, int(self.ServerPORT), msg)
		print(filemd5)
		self.dbReader.execute("SELECT Lenfile, Lenpart FROM File WHERE Filemd5 LIKE ?", ("%"+filemd5+"%",))
		resultFile = self.dbReader.fetchone()	
		print(resultFile)
		nParts = int(resultFile[0])/int(resultFile[1])
		print("Deve essere 5: " + str(nParts))
		lenBit = int(nParts/8)
		if (nParts % 8) > 0:
			lenBit = lenBit + 1
		print("Deve essere 1: " + str(lenBit))
		data, addr = self.sockUDPServer.recvfrom(4)
		command = data.decode()
		if command == "AFCH":
			hitpeer = int(peer_socket.recv(3).decode())
			if hitpeer > 0 :
				i = 0
				while i < hitpeer:
					ipp2p = peer_socket.recv(55).decode()
					pp2p = peer_socket.recv(5).decode()
					partList = int.from_bytes(peer_socket.recv(lenBit), 'big')
					while partList > 0:
						idPart, partList = calcID(self, partList, nParts)
						self.dbReader.execute("INSERT INTO Parts (IPP2P, PP2P, Filemd5, IdParts) values (?, ?, ?, ?)", (ipp2p, pp2p, filemd5, idParts))
					'''
					while lenBit > 1:
						#idParts, partList = calcId(partList, nParts)
						self.dbReader.execute("SELECT IdParts FROM Parts WHERE Filemd5 LIKE ? AND IPP2P <> ?", ("%"+filemd5+"%", ))
						self.dbReader.execute("INSERT INTO Parts (IPP2P, PP2P, Filemd5, IdParts) values (?, ?, ?, ?)", (ipp2p, pp2p, filemd5, idParts))
					'''
					i = i + 1
		peer_socket.close()
		
	def serverUDP(self):
		print(color.green+"In attesa di comandi interni..."+color.end)
		while True:
			data, addr = self.sockUDPServer.recvfrom(4)
			command = data.decode()
			print("\n\nRicevuto comando dal client: "+color.recv+command+color.end)
				
			if command == "SETV":
				gruppo = str(self.sockUDPServer.recvfrom(3)[0].decode())
				numPc = str(self.sockUDPServer.recvfrom(3)[0].decode())
				port = str(self.sockUDPServer.recvfrom(5)[0].decode())
				ip = "172.016."+gruppo+"."+numPc
				ipv6 = "fc00:0000:0000:0000:0000:0000:"+setIPv6(int(gruppo))+":"+setIPv6(int(numPc))
				
				#setto il server IP
				self.ServerIP = ip+"|"+ipv6
				self.ServerPORT = port
				print(color.green+"Server settato con successo"+color.end)
				#gestione cronometro
				threading.Thread(target = timerChunk, args = '').start()
			
			elif command == "ADDR":
				filename = self.sockUDPServer.recvfrom(100)[0].decode()
				filename = var.setting.userPath+filename.strip()
				filemd5 = encryptMD5(filename)
				
				fileSize = os.path.getsize(filename)
				numParts = int((fileSize / self.lenPart) + 1)
				
				try:
					fileToDivide = open(filename, 'rb')
				except OSError as e:
					print(e)
					self.sockUDPClient.sendto(("0").encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
				
				data = fileToDivide.read()
				sys.stdout.flush()
				fileToDivide.close()
				
				dirName = var.setting.userPath+"/"+filemd5+"/"
				if not os.path.exists(dirName):
					os.makedirs(dirName)
				i = 1
				gap = 0
				while i <= numParts:
					try:
						#fd = open(dirName+""+str(i), os.O_CREAT)
						fd = open(dirName+""+str(i), 'wb')
					except OSError as e:
						print(e)
						self.sockUDPClient.sendto(("0").encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
					
					endGap = gap+self.lenPart
					if endGap > fileSize:
						endGap = fileSize

					fd.write(data[gap:endGap])
					sys.stdout.flush()
					fd.close()
					
					gap += self.lenPart
					i += 1
				
				msg = "ADDR"+self.mySessionID+str(fileSize).ljust(10)+str(self.lenPart).ljust(6)+filename.ljust(100)+filemd5.ljust(32)
				try:				
					peer_socket = setConnection(self.ServerIP, int(self.ServerPORT), msg)
					#aspetto la risposta
					command = peer_socket.recv(4).decode()
					if command == "AADR":
						nPart = int(peer_socket.recv(8).decode())
						print("Ricevuto <-- "+color.send+"AADR"+str(nPart)+color.end)
						if nPart == numParts:
							self.sockUDPClient.sendto(("1").encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
						else:
							self.sockUDPClient.sendto(("0").encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
							time.sleep(10)
				except:
					print(color.fail+"Errore aggiunta file"+color.end)
					self.sockUDPClient.sendto(("0").encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
					time.sleep(10)

			
			elif command == "LOGI":
				msg = "LOGI"+str(self.myIPP2P).ljust(55)+str(self.PORT).ljust(5)
				try:
					peer_socket = setConnection(self.ServerIP, int(self.ServerPORT), msg)
					command = peer_socket.recv(4).decode()
					if command == "ALGI":
						#setto il mio sessionID
						self.mySessionID = peer_socket.recv(16).decode()
						print("Ricevuto <-- "+color.send+command+str(self.mySessionID)+color.end)
						if self.mySessionID == "0000000000000000":
							print(color.fail+"Errore lato Server! Login fallito!")
							self.sockUDPClient.sendto(("LOG0").encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
						else:
							print(color.recv+"Login effettuato!")
							self.sockUDPClient.sendto(("LOG1").encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
					else:
						print(color.fail+"Login fallito!")
						self.sockUDPClient.sendto(("LOG0").encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
					peer_socket.close()
				except:
					print(color.fail+"Errore salvataggio SessionID"+color.end)
					self.sockUDPClient.sendto(("LOG0").encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
			
			elif command == "FIND":
				ricerca, useless = self.sockUDPServer.recvfrom(20).decode()
				ricerca = ricerca.strip()
				sessionID = self.mySessionID 
				
				msg = "LOOK" + sessionID + ricerca
				print("Invio messaggio -> " + msg + " a " + self.ServerIP + " alla porta " + self.ServerPORT)
				
				peer_socket = setConnection(self.ServerIP, self.ServerPORT, msg)
				command = peer_socket.recv(4).decode()
				print("Ricevuto " + command)
				if command is "ALOO":
					nIdMd5 = int(peer_socket.recv(3).decode())
					i=0
					while i < nIdMd5:
						filemd5 = peer_socket.recv(32).decode()
						filename = peer_socket.recv(100).decode()
						lenfile = peer_socket(10).decode()
						lenpart = peer_socket(6).decoce()
						self.dbReader.execute("INSERT INTO File (Filemd5, Filename, Lenfile, Lenpart) values (?, ?, ?, ?)", (filemd5, filename, lenfile, lenpart))
						i = i + 1
					print("Trovati " + nIdMd5 + " file.")
				self.sockUDPClient.sendto((str(nIdMd5)).ljust(3), (self.UDP_IP, self.UDP_PORT_CLIENT))
				peer_socket.close()
				#posso inserire la richiesta delle parti
			
			elif command == "FDWN":
				data, noused = self.sockUDPServer.recvfrom(20)
				filename = data.decode()
				filename = filename.strip()
				self.dbReader.execute("SELECT Filemd5, Filename, SessionID FROM File WHERE Filename LIKE ?", ("%"+filename+"%",))
				files = self.dbReader.fetchall()
				for f in files:
					self.sockUDPClient.sendto((str(f[0]).ljust(32)+"-"+str(f[1]).ljust(100)+"-"+str(f[2].ljust(16))).encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
				self.sockUDPClient.sendto(((self.UDP_END).ljust(148)).encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
			
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
				self.dbReader.execute("SELECT Filemd5,Lenfile, Lenpart  FROM File WHERE Filename LIKE ? LIMIT 1 OFFSET ?", ("%"+filename+"%",cmd ))
				resultFile = self.dbReader.fetchone()
				Filemd5 = resultFile[0]
				
				numPart = int(resultFile[1])/int(resultFile[2])
				
				self.dbReader.execute("SELECT COUNT(Filemd5) FROM Parts WHERE Filemd5=? AND IPP2P=? AND PP2P=?", (Filemd5, self.myIPP2P, self.PORT))
				data = self.dbReader.fetchone()
				if data is None:
					count = 0
				else:
					count = data[0]
			
				while count < numPart:
					print("COUNT =", count)
					#recupero tutti le parti necessari ...  <--------------- ordineate per minori risultati

					self.dbReader.execute("SELECT COUNT(IdParts) as Seed, IdParts, IPP2P, PP2P, Filemd5  FROM Parts WHERE IPP2P!=? AND Filemd5=? AND IdParts NOT IN (SELECT IdParts FROM Parts WHERE IPP2P=?) GROUP BY IdParts OrDER BY Seed ASC", (self.myIPP2P, Filemd5, self.myIPP2P))
					resultParts = self.dbReader.fetchone()
					
					#se non ho già quella parte la chiedo
					if resultParts is not None:
						#inserisco la parte nel db con Downloaded--> 0, se la ricevo aggiorno il db e metto 1
						self.dbReader.execute("INSERT INTO Parts (IPP2P, PP2P, Filemd5, IdParts, Downloaded) values (?,?, ?, ?, ?)", (self.myIPP2P,self.PORT,Filemd5,resultParts[1], 0))
						msg = "RETP" + str(Filemd5).ljust(32)+str(resultParts[1]).ljust(8)
						print("Invio -->", msg)
						
						randPort = randrange(60000,65000)
						try:
							threading.Thread(target = self.sendDownload, args = (resultParts[2], randPort, msg)).start()
						except:
							print("Errore nell'esecuzione del thread")
					count = count +1
			

			elif command == "STOP":
				print(color.fail+"Server fermato"+color.end)
				self.sockUDPServer.close()
				self.sockUDPClient.close()
				os._exit(0) 
			
			elif command == "FCHU":
	
				print("Debugging FCHU...")
				print("ok")
				self.gettingParts(self.mySessionID,"aaaabbbbccccddddeeeeffffgggghhhh")
				print("Gettingparts completata.")
	
	def sendDownload(self, ip, port, msg):
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
		
		#Blocco in attesa di risposta
		filemd5 = msg[5:36]
		idParts = msg[37:45]
		
		command = peer_socket.recv(4).decode()
		
		if command == "AREP":
			print("Ricevuto "+color.recv+"AREP"+color.end)
			try:
				#dal messaggio inviato estraggo l'identificativo
				fd = open(var.setting.userPath + "" + idParts, 'wb')
				numChunk = peer_socket.recv(6).decode()
				numChunk = int(numChunk)

				i = 0
				print("Inizio download parte --> ",idParts)
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
				print(color.green + "Scaricato la parte " + idParts + color.end+" in "+str(int(totTime))+"s")			
			except OSError:
				print("Errore nella procedure di download parte --> ",idParts )
				#se non funziona tolgo i file tra quelli a disposizione
				self.dbReader.execute("DELETE FROM Parts WHERE IPP2P=? AND IdParts=?", (self.myIPP2P,idParts))
				self.sockUDPClient.sendto(("ARE0").encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))				
				
			self.dbReader.execute("UPDATE Parts SET Downloaded=? where IPP2P=? AND IdParts=?",(1,self.myIPP2P,idParts))
			self.sockUDPClient.sendto(("ARE1").encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
			
			peer_socket.close()

			#Recupero le informazioni del file
			self.dbReader.execute("SELECT Lenfile, Lenpart FROM File WHERE Filemd5 LIKE ?", (filemd5,))
			infoFile = self.dbReader.fetchone()
			numPart = int(infoFile[0])/int(infoFile[1])
			
			#Conto quante parti ho
			self.dbReader.execute("SELECT COUNT(Filemd5) FROM Parts WHERE Filemd5=? AND IPP2P=? AND PP2P=?", (Filemd5, self.myIPP2P, self.PORT))
			data = self.dbReader.fetchone()
			#se ho tutte le parti compatto la foto 
			if data[0] == numPart:
				dirName = var.setting.userPath+"/"+filemd5+"/"
				i = 1
				data = "".encode()
				while j <= numPart:
					try:
						fd = open(dirName+""+str(i), 'rb')
					except OSError as e:
						print(e)
				
					data += fd.read()
					#print(data)
					sys.stdout.flush()
					fd.close()
					i += 1
				try:
					fileToCompact = open(dirName, 'wb')
				except OSError as e:
					print(e)
				fileToCompact.write(data)
				sys.stdout.flush()
				fileToCompact.close()	
	
	def recvDownload(self, connection, client_address):
		command = connection.recv(4).decode()
		if command == "RETP":
			print("Ricevuto "+color.recv+"RETP"+color.end)
		
			#inviare un file che ho
			FileMD5 = connection.recv(32).decode()
			idParts = connection.recv(8).decode()
				
			try:
				fd = os.open(var.setting.userPath+""+idParts, os.O_RDONLY)
			except OSError as e:
				print(e)
			if fd is not -1:
				partsize = int(os.path.getsize(var.setting.userPath+""+idParts))
				num = int(partsize) / self.BUFF
				if (partsize % self.BUFF)!= 0:
					num = num + 1
			
				num = int(num)
				msg = "AREP" + str(num).zfill(6)
				
				print ('Trasferimento iniziato di ', idParts, ' [BYTES ', partsize, ']')
				print(5)
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
				print("Parte non trovata!")
					
if __name__ == "__main__":
    serverUDP = serverUDPhandler()
serverUDP.server()
