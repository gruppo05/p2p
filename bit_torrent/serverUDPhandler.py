import socket, sqlite3, string, subprocess, threading, os, random, ipaddress, time, datetime, hashlib, sys, stat
import setting as var
from threading import Timer
from random import *

class color:
	HEADER = '\033[95m'
	recv = '\033[36m'
	green = '\033[32m'
	send = '\033[33m'
	fail = '\033[1m'+'\033[31m'
	end = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'
	greenB = '\033[1m'+'\033[32m'

def clearAndSetDB(self):
	self.dbReader.execute("DROP TABLE IF EXISTS User")
	self.dbReader.execute("DROP TABLE IF EXISTS File")
	self.dbReader.execute("DROP TABLE IF EXISTS Parts")
	
	self.dbReader.execute("CREATE TABLE User (IPP2P text, PP2P text, SessionID text)")
	self.dbReader.execute("CREATE TABLE File (Filemd5 text, Filename text, SessionID text, Lenfile text, Lenpart text)")
	self.dbReader.execute("CREATE TABLE Parts (IPP2P text, PP2P text, Filemd5 text, IdParts text)")
	#0 --> Parte non ancora scaricata
	#1 --> Parte scaricata con successo		

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
	
def setConnection(ip, port, msg):
	try:
		rnd = random()
		#rnd=0.1
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
	return filemd5IP
		
		
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
		
		#thread lock
		self.lock = threading.Lock()
		self.nThread  = 0
		
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
		threading.Thread(target = self.timerChunk, args = '').start()
		print(color.green+"In attesa di connessione esterna..."+color.end)
		while True:
			try:
				connection, client_address = self.sock.accept()
				threading.Thread(target = self.upload, args = (connection,client_address)).start()
			except:
				return False
					
	def gettingParts(self, sessionID, filemd5):
		self.dbReader.execute("DELETE FROM Parts WHERE Filemd5=?",(filemd5,))
		msg = "FCHU" + sessionID.ljust(16) + filemd5.ljust(32)
		peer_socket = setConnection(self.ServerIP, int(self.ServerPORT), msg)
		self.dbReader.execute("SELECT Lenfile, Lenpart FROM File WHERE Filemd5 LIKE ?", ("%"+filemd5+"%",))
		resultFile = self.dbReader.fetchone()	
		nParts = int(int(resultFile[0])/int(resultFile[1]))
		if (int(resultFile[0])%int(resultFile[1]))!=0:
			nParts = nParts + 1
		lenBytes = int(nParts/8)
		if (nParts % 8)!=0:
			lenBytes = lenBytes + 1
		data, addr = peer_socket.recvfrom(4)
		command = data.decode()
		if command == "AFCH":
			
			hitpeer, useless = peer_socket.recvfrom(3)
			hitpeer = int(hitpeer.decode())
			if hitpeer > 0 :
				i = 0
				while i < hitpeer:
					ipp2p = peer_socket.recv(55).decode()
					pp2p = peer_socket.recv(5).decode()
					partList = int.from_bytes(peer_socket.recv(lenBytes), 'big')
					partList = bin(partList)[2:]
					j=0
					while j < len(partList)-1:
						if partList[j] == "1":
							self.dbReader.execute("INSERT INTO Parts (IPP2P, PP2P, Filemd5, IdParts) values (?, ?, ?, ?)", (ipp2p, pp2p, filemd5, j))
						j=j+1
					i = i + 1
		peer_socket.close()
		
	def timerChunk(self):
		sec = 0
		print("Thread creato per la FCHU")
		while True:
			time.sleep(var.setting.timeDebug)
			sec = sec + 0.1
			if int(sec) == 2:
				try:
					self.lock.acquire(True)
					#self.dbReader.execute("INSERT INTO File (Filemd5, Filename) values (?, ?)", ("prova", "prova.txt"))
					self.dbReader.execute("SELECT DISTINCT Filemd5 FROM File")
					filemd5 = self.dbReader.fetchall()
				except:
					print("Problemi sulla timerChunk")
				finally:
					self.lock.release()
				if len(filemd5) > 0:
					print("Invio FCHU")
					for files in filemd5:
						self.gettingParts(self.mySessionID, files[0])
				else:
					print("Non bisogna fare la fchu")
				sec = 0
				
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
				#threading.Thread(target = timerChunk, args = '').start()
			
			elif command == "ADDR":
				filename = self.sockUDPServer.recvfrom(100)[0].decode()
				path = var.setting.userPath+filename.strip()
				filemd5 = encryptMD5(path)
				
				fileSize = os.path.getsize(path)
				numParts = int((fileSize / self.lenPart) + 1)
				
				try:
					fileToDivide = open(path, 'rb')
				except OSError as e:
					print(e)
					self.sockUDPClient.sendto(("0").encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
				
				data = fileToDivide.read()
				sys.stdout.flush()
				fileToDivide.close()
				
				dirName = var.setting.userPath+"/"+filemd5+"/"
				if not os.path.exists(dirName):
					os.makedirs(dirName)
				i = 0
				gap = 0
				while i <= numParts-1:
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
				except:
					print(color.fail+"Errore aggiunta file"+color.end)
					self.sockUDPClient.sendto(("0").encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))

			
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

			elif command == "LOGO":
				msg = "LOGO"+str(self.mySessionID).ljust(16)
				peer_socket = setConnection(self.ServerIP, int(self.ServerPORT), msg)
				command = peer_socket.recv(4).decode()
				if command == "NLOG":
					partDown = peer_socket.recv(10).decode()
					print("Ricevuto <-- "+color.send+command+str(partDown)+color.end)
					print(color.fail + "Impossibile effettuare il logout" + color.end)
					self.sockUDPClient.sendto(("NLOG").encode(),(self.UDP_IP,self.UDP_PORT_CLIENT))
					self.sockUDPClient.sendto((partDown.ljust(10)).encode(),(self.UDP_IP,self.UDP_PORT_CLIENT))
				elif command == "ALOG":
					partOwn = peer_socket.recv(10).decode()
					print("Ricevuto <-- "+color.send+command+str(partOwn)+color.end)
					print(color.green + "Logout consentito" + color.end)
					self.sockUDPClient.sendto(("ALOG").encode(),(self.UDP_IP,self.UDP_PORT_CLIENT))
					self.sockUDPClient.sendto((partOwn.ljust(10)).encode(),(self.UDP_IP,self.UDP_PORT_CLIENT))
				peer_socket.close()
			
			elif command == "FIND":
				ricerca = self.sockUDPServer.recvfrom(20)[0].decode().strip()
				sessionID = self.mySessionID 
				msg = "LOOK" + sessionID.ljust(16) + ricerca.ljust(20)
				print("Invio messaggio -> " + msg + " a " + self.ServerIP + " alla porta " + self.ServerPORT)
				peer_socket = setConnection(self.ServerIP, int(self.ServerPORT), msg)
				command = peer_socket.recv(4).decode()
				nIdMd5 = peer_socket.recv(3).decode().strip()
				if command == "ALOO":
					print("Ricevuto <-- "+color.send+command+""+str(nIdMd5)+color.end)
					i=0
					while i < int(nIdMd5):
						filemd5 = peer_socket.recv(32).decode().strip()
						filename = peer_socket.recv(100).decode().strip()
						lenfile = peer_socket.recv(10).decode().strip()
						lenpart = peer_socket.recv(6).decode().strip()
						self.dbReader.execute("SELECT Filemd5 FROM File WHERE Filemd5 LIKE ?", (filemd5,))
						f = self.dbReader.fetchone()
						if f is None:
							self.dbReader.execute("INSERT INTO File (Filemd5, Filename, Lenfile, Lenpart) values (?, ?, ?, ?)", (filemd5, filename, lenfile, lenpart))
						i = i + 1
				self.sockUDPClient.sendto((str(nIdMd5)).ljust(3).encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
				peer_socket.close()
				print(color.green + "Ricerca completata. Trovati " +str(nIdMd5) + " file." + color.end)
				#dopo aver fatto la ricerca, chiedo dove si trovano le parti
				self.dbReader.execute("SELECT Filemd5 FROM File WHERE Filename LIKE ?", ("%"+ricerca+"%",))
				resultFile = self.dbReader.fetchall()
				if len(resultFile) > 0:	
					for files in resultFile:
						self.gettingParts(self.mySessionID, files[0])
					print(color.green + "Ricerca parti completata." + color.end)
			
			elif command == "FDWN":
				data, noused = self.sockUDPServer.recvfrom(20)
				filename = data.decode()
				filename = filename.strip()
				self.dbReader.execute("SELECT Filemd5, Filename, SessionID FROM File WHERE Filename LIKE ?", ("%"+filename+"%",))
				files = self.dbReader.fetchall()
				for f in files:
					self.sockUDPClient.sendto((str(f[0]).ljust(32)+"-"+str(f[1]).ljust(100)).encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
				self.sockUDPClient.sendto(((self.UDP_END).ljust(133)).encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
			
			elif command == "RETP":
				print("ricevuto RETP")
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
				numPart = int(int(resultFile[1]) / int(resultFile[2]) + 1)
				self.dbReader.execute("SELECT COUNT(Filemd5) FROM Parts WHERE Filemd5=? AND IPP2P=? GROUP BY Filemd5", (Filemd5, self.myIPP2P))
				data = self.dbReader.fetchone()
				if data is None:
					count = 1
				elif data[0] == 0:
					count = 1
				else:
					count = int(data[0]) +1
				
				self.dbReader.execute("SELECT COUNT(IdParts) as Seed, IdParts, IPP2P, PP2P, Filemd5 FROM Parts WHERE IPP2P!=? AND Filemd5=? AND IdParts NOT IN (SELECT IdParts FROM Parts WHERE IPP2P=?) GROUP BY IdParts ORDER BY Seed, IdParts ASC", (self.myIPP2P, Filemd5, self.myIPP2P))
				data = self.dbReader.fetchall()
				for resultParts in data:
					while True:
						if self.nThread < 50:
							idParts = resultParts[1]
							ip = resultParts[2]
							port = resultParts[3]
					
							#se non ho già quella parte la chiedo
							if resultParts is not None:
								if resultParts[0] > 1:
									#se ho più risultati seleziono randomicamente IP 
									rnd = randint(1, int(resultParts[0])) - 1 
									try:
										self.lock.acquire(True)
										self.dbReader.execute("SELECT IPP2P, PP2P FROM Parts WHERE IdParts=? LIMIT 1 OFFSET ?", (resultParts[0], rnd))
									except:
										print("Erroreeee")
									finally:
										self.lock.release()		
									resultParts = self.dbReader.fetchone()
									#aggiorno ip e port con quello casuale
									ip = resultParts[0]
									port = resultParts[1]
							
								#inserisco la parte nel db con Downloaded--> 0, se la ricevo aggiorno il db e metto 1

								msg = "RETP" + str(Filemd5).ljust(32)+str(idParts).ljust(8)
								try:
									threading.Thread(target = self.download, args = (ip, int(port), msg)).start()
									self.nThread += 1
								except:
									print("Errore nell'esecuzione del thread")
								finally:
									break
							else:
								print("Ho già quel file")
							break
					
			elif command == "STOP":
				print(color.fail+"Server fermato"+color.end)
				self.sockUDPServer.close()
				self.sockUDPClient.close()
				os._exit(0) 
			
			elif command == "STMC":
				self.dbReader.execute("SELECT IPP2P, IdParts FROM Parts")
				parts = self.dbReader.fetchall()
				if len(parts) == 0:
					print("Non ci sono parti in condivisione dei file che hai cercato.")
				else:
					print("Parti in condivisione:")
				for part in parts:
					print("IP: " +part[0]+ " PARTE IN CONDIVISIONE: " +part[1])
				self.dbReader.execute("SELECT Filename FROM File")
				files = self.dbReader.fetchall()
				if int(len(files))==0:
					print("Non ci sono file.")
				else:
					print("file in condivisione:")
					for f in files:
						print("filename: " +f[0])
					
	
	def download(self, ip, port, msg):
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
		filemd5 = msg[4:36]
		idParts = msg[36:44].strip()
		command = peer_socket.recv(4).decode()
		
		if command == "AREP":
			print("Ricevuto "+color.recv+"AREP"+color.end)
			try:
				try:
					#dal messaggio inviato estraggo l'identificativo
					dirName = var.setting.userPath+"/"+filemd5+"/"
					if not os.path.exists(dirName):
						os.makedirs(dirName)
					
					fd = open(dirName + "" + idParts, 'wb')
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
						i = i + 1

					time2 = time.time()
					sys.stdout.flush()
					fd.close()
					print("\n")
					totTime = time2 - time1
					print(color.green + "Scaricato <-- parte " + idParts + color.end+" (time: "+str(int(totTime))+"s)")			
				
					peer_socket.close()	
					#libero il thread
				except:
					print("Errore durante la fase di scaricamento")
				finally:
					#libero il thread
					self.nThread -=1
				
				try:
					#accesso in muta esclusione per aggiornamento server
					self.lock.acquire(True)
					self.dbReader.execute("INSERT INTO Parts (IPP2P, PP2P, Filemd5, IdParts) values (?, ?, ?, ?)", (self.myIPP2P,self.PORT,filemd5,idParts))
					#la mando al server				
					msg = "RPAD"+str(self.mySessionID).ljust(16)+filemd5.ljust(32)+idParts.ljust(8)
				
					#aspetto la risposta
					peer_socket = setConnection(self.ServerIP, int(self.ServerPORT), msg)
					command = peer_socket.recv(4).decode()
					if command == "APAD":
						nPart = peer_socket.recv(8).decode()
						print("Ricevuto <-- "+color.send+"APAD"+str(nPart)+color.end)	
				except:
					print(color.fail+"Errore nella comunicazione con il server"+color.end)
				finally:
					self.lock.release()
					
				#Recupero le informazioni del file con un mutex
				try:
					self.lock.acquire(True)
					self.dbReader.execute("SELECT Lenfile, Lenpart, Filename FROM File WHERE Filemd5=?", (filemd5,))
					infoFile = self.dbReader.fetchone()
					numPart = int(int(infoFile[0]) / int(infoFile[1])) + 1
					#Conto quante parti ho
					self.dbReader.execute("SELECT COUNT(Filemd5) FROM Parts WHERE Filemd5=? AND IPP2P=?", (filemd5, self.myIPP2P))
					result = self.dbReader.fetchone()
					#se ho tutte le parti compatto la foto 
					if result[0] == numPart:
						print(color.recv+"\nFile scaricato. Unione delle parti in corso..."+color.end)
						dirName = var.setting.userPath+""+filemd5+"/"
						i = 0
						data = "".encode()
						while i <= numPart-1 :
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
							downloadDir = var.setting.userPath+"/download/"
							if not os.path.exists(downloadDir):
								os.makedirs(downloadDir)
							fileToCompact = open(downloadDir+""+infoFile[2], 'wb')
						except OSError as e:
							print(e)
						
						fileToCompact.write(data)
						sys.stdout.flush()
						fileToCompact.close()
						print(color.greenB+"********************** Fine **********************\n"+color.end)
						self.dbReader.execute("DELETE FROM Parts WHERE IPP2P=? AND Filemd5=?", (self.myIPP2P, filemd5))
						
				except:
					print(color.fail+"Download non riuscito. Scarica le parti mancanti"+color.end)
				finally:
					self.lock.release()					
				
			except OSError:
				print("Errore nella procedure di download parte --> ",idParts )
				#se non funziona tolgo i file tra quelli a disposizione

	
	def upload(self, connection, client_address):
		command = connection.recv(4).decode()
		if command == "RETP":
			try:
				self.lock.acquire(True)
				print("Ricevuto "+color.recv+"RETP"+color.end)
		
				#inviare un file che ho
				filemd5 = connection.recv(32).decode()
				idParts = int(connection.recv(8).decode().strip())
				dirName = var.setting.userPath+""+filemd5+"/"
				try:
					fd = os.open(dirName+""+str(idParts), os.O_RDONLY)
				except OSError as e:
					print(e)
				
				if fd is not -1:
					partsize = int(os.path.getsize(dirName+""+str(idParts)))
					num = int(partsize / self.BUFF)
					if (partsize % self.BUFF)!= 0:
						num = num + 1
					msg = "AREP" + str(num).zfill(6)
		
					print ('Trasferimento iniziato di ', str(idParts), ' [BYTES ', partsize, ']')
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
						i += 1
		
					os.close(fd)
					print(color.green+"Fine UPLOAD parte "+str(idParts)+color.end)					
					connection.close()
				else: 
					print("Parte non trovata!")
			except:
				print(color.fail+"Errore nell'upload parte "+str(idParts)+". Il file potrebbe non essere stato scaricato con successo!"+color.end)
			finally:
				self.lock.release()
									
if __name__ == "__main__":
    serverUDP = serverUDPhandler()
serverUDP.server()


