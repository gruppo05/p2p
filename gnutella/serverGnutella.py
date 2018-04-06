import socket, sqlite3, string, subprocess, threading, os, random, ipaddress, time, datetime
import settings as var
from random import *

def clearAndSetDB(self):
	self.dbReader.execute("DROP TABLE IF EXISTS user")
	self.dbReader.execute("DROP TABLE IF EXISTS Pktid")
	#self.dbReader.execute("DROP TABLE IF EXISTS download")
	self.dbReader.execute("CREATE TABLE user (IPP2P text, PP2P text)")
	self.dbReader.execute("CREATE TABLE pktid (Pktid text, Timestamp DATETIME)")
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
	
class GnutellaServer(object):
	def __init__(self):
		IP = ""
		self.PORT = var.Settings.PORT
		self.myIPP2P = var.Settings.myIPP2P
		UDP_IP = "127.0.0.1"
		UDP_PORT = 49999
	
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
		self.sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sockUDP.bind((UDP_IP, UDP_PORT))
	
	def internalServer(self):
		print(color.green+"In attesa di comandi interni..."+color.end)
		while True:
			data, addr = self.sockUDP.recvfrom(4)
			command = data.decode()
			print("\n\nRicevuto comando dal client: "+color.recv+command+color.end)
			if command == "NEAR":
				myPktid = PktidGenerator()
				
				#Inserisco il Pktip nel db
				self.dbReader.execute("INSERT INTO pktid (Pktid, Timestamp) values (?, ?)",(myPktid,datetime.datetime.now()))
				TTL = setNumber(2)
				self.dbReader.execute("SELECT IPP2P, PP2P FROM user")
				resultUser = self.dbReader.fetchall()
				msg = "NEAR" + myPktid + self.myIPP2P + str(self.PORT).ljust(5) + TTL
				for user in resultUser:
					setConnection(user[0], int(user[1]), msg)
					
				if command == "QUER":
					print("\n\nRicevuto comando dal client: "+color.recv+command+color.end)
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
				print("\n\nRicevuto comando dal client: "+color.recv+command+color.end)
			print("\n")
			if command == "STMF":
				#stampo i file 
				self.dbReader.execute("SELECT * FROM File")

				files = self.dbReader.fetchall()

				for f in files:
					print("Filemd5: " + f[0] + " Filename: " + f[1] + " IPP2P: " + f[3])

			if command == "STMV":
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
				PP2P = connection.recv(5).decode()
				TTL = connection.recv(2).decode()
				
				#se non esiste il pktid, lo inserisco e propago il messaggio altrimenti lo ignoro in quanto l'ho già ricevuto e ritrasmesso
				self.dbReader.execute("SELECT Timestamp FROM pktid WHERE Pktid=?", (Pktid,))
				t = self.dbReader.fetchone()
				
				if t is None:
					self.dbReader.execute("INSERT INTO pktid (Pktid, Timestamp) values (?, ?)",(myPktid,datetime.datetime.now()))
					
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
				
				Pktid = connection.recv(16).decode()
				IPP2P = connection.recv(55).decode()
				PP2P = connection.recv(5).decode()
				
				#verifico se c'è il pktid			
				self.dbReader.execute("SELECT Timestamp FROM pktid WHERE Pktid=?", (Pktid,))
				t = self.dbReader.fetchone() #retrieve the first row
				
				if getTime(t[0]) < 300:
					#verifico se l'utente è già salvato nel db oppure lo aggiungo
					self.dbReader.execute("SELECT IPP2P FROM user WHERE IPP2P=?", (IPP2P,))
			
					data = self.dbReader.fetchone() #retrieve the first row
					if data is None:
						self.dbReader.execute("INSERT INTO user (IPP2P, PP2P) values (?, ?)",(IPP2P, PP2P))
						print(color.green + "Aggiunto nuovo user" + color.end)
					else:
						print(color.fail + "User già presente" + color.end)	
				else:
					print("ricevuto pacchetto dopo 300s")
					
		except:
			connection.close()
			return False
				
		
if __name__ == "__main__":
    gnutella = GnutellaServer()
gnutella.server()

