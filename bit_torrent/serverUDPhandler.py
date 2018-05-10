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
	self.dbReader.execute("DROP TABLE IF EXISTS File")
	self.dbReader.execute("DROP TABLE IF EXISTS TrackedFile")

	self.dbReader.execute("CREATE TABLE File (Filemd5 text, Filename text, SessionID text)")
	self.dbReader.execute("CREATE TABLE TrackedFile (IPP2P text, PP2P text, Filemd5 text, Filename text)")
    
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

def timer(self):
	print("Timer partito")
	
class serverUDPhandler(object):
	def __init__(self):
		self.ServerIP = ""
		self.ServerPORT = 3000
		
		self.PORT = var.Settings.PORT
		self.myIPP2P = var.Settings.myIPP2P
		self.mySessionID = ""
		
		self.UDP_IP = "127.0.0.1"
		UDP_PORT_SERVER = 49999
		self.UDP_PORT_CLIENT = 50000
	
		self.timeDebug = var.Settings.timeDebug
		self.BUFF = 1024
		
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
		#gestione cronometro
		#threading.Thread(target = self.timer, args = '').start()
		
	def server(self):
		#crea thread interno per far comunicare client e server
		threading.Thread(target = self.serverUDP, args = '').start()
		
		print(color.green+"In attesa di connessione esterna..."+color.end)
		while True:
			try:
				connection, client_address = self.sock.accept()
				threading.Thread(target = self.download, args = (connection,client_address)).start()
			except:
				return False
	
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
		
			elif command == "LOGI":
				msg = "LOGI"+str(self.myIPP2P).ljust(55)+str(self.PORT).ljust(5)
				try:
					peer_socket = setConnection(self.ServerIP, int(self.ServerPORT), msg)					
					command = peer_socket.recv(4).decode()
					if command == "ALGI":
						#setto il mio sessionID
						self.mySessionID = peer_socket.recv(16).decode()
						print("Ricevuto <-- "+color.send+command+str(self.mySessionID)+color.end)
						
						print(color.recv+"Login effettuato!")
						self.sockUDPClient.sendto(("LOG1").encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
					else:
						print(color.fail+"Login fallito!")
						self.sockUDPClient.sendto(("LOG0").encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
					peer_socket.close()
				except:
						print(color.fail+"Errore salvataggio SessionID"+color.end)
						self.sockUDPClient.sendto(("LOG0").encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
			
			
			
			
			
			
			
			
			
			# parte bertasi #
			
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
					
					
					''' da modificare per p2p '''
					
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

	def download(self, connection, client_address):
		command = connection.recv(4).decode()
		if command == "RETR":
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
					print("Il file non esiste!")
					
if __name__ == "__main__":
    serverUDP = serverUDPhandler()
serverUDP.server()
