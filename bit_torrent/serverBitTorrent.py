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


def clearAndSetDB(self):
	self.dbReader.execute("DROP TABLE IF EXISTS User")
	self.dbReader.execute("DROP TABLE IF EXISTS File")
	self.dbReader.execute("DROP TABLE IF EXISTS Parts")
	
	self.dbReader.execute("CREATE TABLE User (IPP2P text, PP2P text, SessionID text)")
	self.dbReader.execute("CREATE TABLE File (Filemd5 text, Filename text, SessionID text, Lenfile text, Lenpart text)")
	self.dbReader.execute("CREATE TABLE Parts (IPP2P text, PP2P text, Filemd5 text, IdParts text)")

def closeServer(self):
	time.sleep(0.1)
	self.sockUDPServer.close()
	self.sockUDPClient.close()
	os._exit(0)
    
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


class serverBitTorrent(object):
	def __init__(self):
		IP = ""
		self.PORT = 3000
		self.myIPP2P = var.setting.myIPP2P

		self.timeDebug = var.setting.timeDebug
		self.BUFF = 1024
		self.super = ""
		# Creo DB
		conn = sqlite3.connect(':memory:', check_same_thread=False)
		self.dbReader = conn.cursor()
		# Creo tabella user
		clearAndSetDB(self)
		
		# Socket ipv4/ipv6 port 3000
		self.server_address = (IP, int(self.PORT))
		self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind(self.server_address)
		self.sock.listen(5)
		
		
		# Socket UDP
		self.UDP_IP = "127.0.0.1"
		self.UDP_PORT_CLIENT = 30002
		UDP_PORT_SERVER = 30001
		# socket upd ipv4 internal Server
		self.sockUDPServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sockUDPServer.bind((self.UDP_IP, UDP_PORT_SERVER))
		# socket upd ipv4 client in uscita
		self.sockUDPClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		
	def serverHandler(self):
		#crea thread interno per far comunicare client e server
		threading.Thread(target = self.serverUDP, args = '').start()
		
		print(color.green+"In attesa di connessione..."+color.end)
		while True:
			try:
				connection, client_address = self.sock.accept()
				threading.Thread(target = self.server, args = (connection,client_address)).start()
			except:
				return False
	
	def server(self, connection, client_address):
		command = connection.recv(4).decode()
		try:
			if command == "LOGI":
				try:
					IPP2P = connection.recv(55).decode()
					PP2P = connection.recv(5).decode()
					print("Ricevuto " + color.recv + command + color.end + " da " + color.recv + IPP2P + color.end + " - " + color.recv + PP2P + color.end)
					self.dbReader.execute("SELECT SessionID FROM user WHERE IPP2P=?", (IPP2P,))
					data = self.dbReader.fetchone()
					if data is None:
						SessionID = sessionIdGenerator()
						self.dbReader.execute("INSERT INTO user (IPP2P, PP2P, SessionID) values (?, ?, ?)",(IPP2P, PP2P, SessionID))
						print(color.green + "Nuovo utente aggiunto con sessionID -> "+color.recv+SessionID+color.end)
					else:						
						SessionID = data[0]
						print(color.fail+"Utente già presente con sessionID -> "+color.recv+SessionID+color.end)
					
				except:
					SessionID = "0000000000000000"
					print("Errore nella procedura di login server")
				finally:
					msg = "ALGI"+SessionID
					connection.sendall(msg.encode())
					connection.close()
			elif command == "FCHU":
				try:
					sessionID = connection.recv(16).decode()
					filemd5 = connection.recv(32).decode()
					self.dbReader.execute("SELECT * FROM User WHERE SessionID LIKE ?", (sessionID,))
					resultUser = self.dbReader.fetchone()
					if resultUser is None:
						msg = "AFCH000"
						print("Utente non registrato")
					else:
						self.dbReader.execute("SELECT DISTINCT IPP2P, PP2P FROM Parts WHERE Filemd5 LIKE ?", (filemd5,))
						resultParts = self.dbReader.fetchall()
						if resultParts is None:
							msg = "AFCH000"
							print("Parti non presenti. File non in condivisione.")
						else:
							msg = "AFCH" + str(len(resultParts)).ljust()
							for user in resultParts:
								self.dbReader.execute("SELECT IdParts FROM PARTS WHERE IPP2P LIKE ?", (user[0]))
								resultParts = self.dbReader.fetchall()
								partList = 0
								self.dbReader.execute("SELECT Lenfile FROM File WHERE Filemd5 LIKE ?", (filemd5,))
								lenFile = self.dbReader.fetchone()
								for ids in resultParts:
									partList = partList + (2**(lenFile[0] - ids[0])
								#creo il messaggio
								msg = msg + user[0] + user[1] + partList
				except:
					print("Errore nella FCHU")
					msg = "AFCH000"
				finally:
					connection.sendall(msg.encode())
					connection.close()
		except:
			connection.close()
			return False
	
	
	def serverUDP(self):
		print(color.green+"In attesa di comandi interni..."+color.end)
		while True:
			data, addr = self.sockUDPServer.recvfrom(4)
			command = data.decode()
			print("\n\nRicevuto comando dal client: "+color.recv+command+color.end)
			
			if command == "STOP":
				print("Ricevuto STOP!")
				closeServer(self)
			elif command == "STMV":
				print("QUI DEVO MANDARE INDIETRO I VICINI")
				
	

if __name__ == "__main__":
    bitTorrent = serverBitTorrent()
bitTorrent.serverHandler()





