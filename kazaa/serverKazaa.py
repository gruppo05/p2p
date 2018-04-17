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
	self.dbReader.execute("CREATE TABLE File (Filemd5 text, Filename text, IPP2P text)")
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
		self.endUDP1 = "";
		self.endUDP2 = "";
		self.BUFF = 99999
		
		self.super = ""
		# Creo DB
		conn = sqlite3.connect(':memory:', check_same_thread=False)
		self.dbReader = conn.cursor()
		
		# Creo tabella user
		clearAndSetDB(self)
		
		
		#inserisco l'utente root
		self.dbReader.execute("INSERT INTO user (Super, IPP2P, PP2P) values(?, ?, ?) ",(1, "192.168.043.078|fe80:0000:0000:0000:5bf8:4887:b7f4:6974", 3000))
		if self.myIPP2P != var.Settings.root_IP:
			self.dbReader.execute("INSERT INTO user (IPP2P, PP2P) values ('"+var.Settings.root_IP+"', '"+var.Settings.root_PORT+"')")
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
					IPP = connection.recv(5).decode()
					print("Ricevuto " + color.recv + command + color.end + " da " + color.recv + IPP2P + color.end + " - " + color.recv + IPP + color.end)
					self.dbReader.execute("SELECT SessionID FROM user WHERE IPP2P=?", (IPP2P,))
					data = self.dbReader.fetchone() #retrieve the first row
					if data is None:
						print(color.green + "NUOVO UTENTE" + color.end);
						SessionID = sessionIdGenerator()
						self.dbReader.execute("INSERT INTO user (SessionID, IPP2P, PP2P) values (?, ?, ?)",(SessionID, IPP2P, IPP))
					else:
						print(color.fail + "UTENTE GIÀ PRESENTE" + color.end)
						SessionID = str(data[0])
				except:
					SessionID = "0000000000000000"
				finally:
					connection.sendall(("ALGI"+SessionID).encode())
			
		except:
			connection.close()
			return False
	
	
		
if __name__ == "__main__":
    gnutella = Kazaa()
gnutella.server()

















