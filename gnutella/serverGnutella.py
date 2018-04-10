import socket, sqlite3, string, subprocess, threading, os, random, ipaddress, time, datetime, os, os.path, hashlib, sys, stat
import settings as var
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
	#self.dbReader.execute("DROP TABLE IF EXISTS download")
	self.dbReader.execute("CREATE TABLE User (IPP2P text, PP2P text)")
	self.dbReader.execute("CREATE TABLE Pktid (Pktid text, Timestamp DATETIME)")
	self.dbReader.execute("CREATE TABLE File (Filemd5 text, Filename text, IPP2P text)")
	#self.dbReader.execute("CREATE TABLE download (Filemd5 text, Download integer)")

def progressBar(end_val, bar_length):
	end_val = 10
	bar_length = 20
	i = 0
	while i < 11:
		percent = float(i) / end_val
		hashes = '#' * int(round(percent * bar_length))
		spaces = ' ' * (bar_length - len(hashes))
		sys.stdout.write("\rPercent: [{0}] {1}%".format(hashes + spaces, int(round(percent * 100))))
		sys.stdout.flush()
		time.sleep(0.1)
		i = i+1
	print(color.green+"\nFine download!"+color.end)
    
    
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

class GnutellaServer(object):
	def __init__(self):
		IP = ""
		self.download = ""
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
				self.dbReader.execute("INSERT INTO pktid (Pktid, Timestamp) values (?, ?)",(myPktid,datetime.datetime.now()))
				TTL = setNumber(2)
				self.dbReader.execute("SELECT IPP2P, PP2P FROM user")
				resultUser = self.dbReader.fetchall()
				msg = "NEAR" + myPktid + self.myIPP2P + str(self.PORT).ljust(5) + TTL
				for user in resultUser:
					setConnection(user[0], int(user[1]), msg)
			
			elif command == "1111":
				progressBar(1,1)
				
			elif command == "ADDF":
				
				filename, useless = self.sockUDPServer.recvfrom(20)
				filename = filename.decode()

				PATH=var.Settings.userPath+filename.strip()
				if os.path.isfile(PATH) and os.access(PATH, os.R_OK):
					filemd5 = encryptMD5(PATH)
					msg = "1"
					self.dbReader.execute("INSERT INTO File (filemd5, filename, IPP2P) values (?, ?, ?)", (filemd5, filename, self.myIPP2P))
					print(color.green+"Trovato. Aggiunto file in condivisione"+color.end)
				else:
					msg = "0"
					print(color.fail+"File non presente. Impossibile aggiungerlo in condivisione"+color.end)

					
				self.sockUDPClient.sendto(msg.encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
	
			elif command == "QUER":
				
				myPktid = PktidGenerator()
				self.dbReader.execute("INSERT INTO pktid (Pktid, Timestamp) values (?, ?)", (myPktid, datetime.datetime.now()))
				TTL = setNumber(5)
				self.dbReader.execute("SELECT IPP2P, PP2P FROM user")
				resultUser = self.dbReader.fetchall()
				
				ricerca, useless = self.sockUDPServer.recvfrom(20)
				filename = ricerca.decode()
				
				msg = "QUER" + myPktid + self.myIPP2P + str(self.PORT).ljust(5) + TTL + str(filename)

				
				for user in resultUser:
					setConnection(user[0], int(user[1]), msg)
				
				
			elif command == "RETR":
				
				filename, addr = self.sockUDPServer.recvfrom(20)
				
				filename = filename.decode()
				filename = filename.strip()
				self.dbReader.execute("SELECT * FROM File WHERE Filename LIKE ? AND IPP2P NOT LIKE ?", ("%"+filename+"%","%" + self.myIPP2P+"%"))
				resultFile = self.dbReader.fetchone()
				self.dbReader.execute("SELECT * FROM user WHERE IPP2P LIKE ?", ("%"+resultFile[2]+"%",))
				resultUser = self.dbReader.fetchone()
				
				msg = "RETR" + resultFile[0]
				
				
				
				'''
				self.dbReader.execute("SELECT * FROM File WHERE IPP2P NOT LIKE ?", (self.myIPP2P,))
				resultFile = self.dbReader.fetchall()
				print(len(resultFile))	
				for f in resultFile:
					self.sockUDPClient.sendto((f[0]+"-"+f[1]+"-"+f[2]).encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
				self.sockUDPClient.sendto((self.endUDP2).encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
				print("1")
				code = self.sockUDPServer.recvfrom(100)
				code = code.strip()
				if int(code) == -1:
					print("Download annullato.")
					break
				print("2")	
				self.dbReader.execute("SELECT * FROM File WHERE Filename LIKE ? AND IPP2P NOT LIKE ?", (code, self.myIPP2P))
				data = self.dbReader.fetchone()
				msg = "RETR" + 	data[0]
				
				sef.download = data[1]
				self.dbReader.execute("SELECT IPP2P, PP2P FROM User WHERE IPP2P = ?", (data[2],))
				utente = self.dbReader.fetchone()
				
				#invio il retr all'utente
				setConnection(utente[0], int(utente[1]), msg)	
'''
			elif command == "STMV":
				self.dbReader.execute("SELECT * FROM user")
				vicini = self.dbReader.fetchall()
				for v in vicini:
					self.sockUDPClient.sendto((v[0]+"-"+v[1]).encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
				self.sockUDPClient.sendto((self.endUDP1).encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
				
			elif command == "STMF":
				self.dbReader.execute("SELECT * FROM File")
				files = self.dbReader.fetchall()
				for f in files:
					self.sockUDPClient.sendto((f[0]+"-"+f[1]+"-"+f[2]).encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
				self.sockUDPClient.sendto((self.endUDP2).encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
				
			print("\n")


	def server(self):
		#crea thread interno per far comunicare client e server
		threading.Thread(target = self.internalServer, args = '').start()
		
		print(color.green+"In attesa di connessione esterna..."+color.end)
		
		while True:
			try:
				connection, client_address = self.sock.accept()
				#connection.settimeout(60)
				threading.Thread(target = self.startServer, args = (connection,client_address)).start()
			except:
				return False
			
	def startServer(self, connection, client_address):
		command = connection.recv(4).decode()
		try:
			if command == "NEAR":
				print("Ricevuto "+color.recv+"NEAR"+color.end)
				Pktid = connection.recv(16).decode()
				IPP2P = connection.recv(55).decode()
				PP2P = connection.recv(5).decode()
				TTL = connection.recv(2).decode()
				#se non esiste il pktid, lo inserisco e propago il messaggio altrimenti lo ignoro in quanto l'ho già ricevuto e ritrasmesso
				self.dbReader.execute("SELECT Timestamp FROM pktid WHERE Pktid=?", (Pktid,))
				t = self.dbReader.fetchone()
				
				if t is None:
					self.dbReader.execute("INSERT INTO pktid (Pktid, Timestamp) values (?, ?)",(Pktid,datetime.datetime.now()))
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
				print("Ricevuto "+color.recv+"QUER"+color.end)
				Pktid = connection.recv(16).decode()
				IPP2P = connection.recv(55).decode()
				PP2P = connection.recv(5).decode()
				TTL = connection.recv(2).decode()
				ricerca = connection.recv(20).decode()
				#controllo se ho già ricevuto questa richiesta
				self.dbReader.execute("SELECT Timestamp FROM pktid WHERE Pktid=?", (Pktid,))
				t = self.dbReader.fetchone()
				ricerca = ricerca.strip()
				if t is None:
					self.dbReader.execute("INSERT INTO pktid (Pktid, Timestamp) values (?, ?)", (Pktid, datetime.datetime.now()))
					#prendo i file che ho io cioè quelli che puntano al mio indirizzo ip
					self.dbReader.execute("SELECT * FROM File WHERE IPP2P LIKE ? AND Filename LIKE ?", ( '%' + self.myIPP2P + '%', '%' + ricerca + '%',))
					
					resultFile = self.dbReader.fetchall()
					print(color.green+"Trovati: "+str(len(resultFile))+" file"+color.end)
					i = 0
					lunghezza = int(len(resultFile))
					while i < lunghezza:
						#per ogni file che ho trovato nel db, invio un messaggio al peer
						msg = "AQUE" + Pktid + self.myIPP2P + str(self.PORT).ljust(5) + resultFile[i][0] + resultFile[i][1].ljust(100)
						i = i+1
						setConnection(IPP2P, int(PP2P), msg)
						
				if int(TTL) > 1:
					#se ttl maggiore di 1, decremento il ttl e lo rispedisco a tutti i vicini
					
					TTL = setNumber(int(TTL) - 1)
					self.dbReader.execute("SELECT IPP2P, PP2P FROM User WHERE IPP2P != ?", (IPP2P,))
					resultUser = self.dbReader.fetchall()
					msg = "QUER" + Pktid + IPP2P + PP2P + TTL + ricerca.ljust(20)
					for user in resultUser:
						setConnection(user[0], int(user[1], msg))
					
			elif command == "RETR":
				print("Ricevuto "+color.recv+"RETR"+color.end)
				
				#inviare un file che ho
				FileMD5 = connection.recv(32).decode()
				self.dbReader.execute("SELECT Filename FROM File WHERE FileMD5 = ?",(FileMD5,))
				resultFile = self.dbReader.fetchone()
				filename=resultFile[0].replace(" ","")
				nChunk = 0
				try:
					fd = os.open(filename, os.O_RDONLY)
				except OSError as e:
					print(e)
				
				if fd is not -1:

					filesize = os.path.getsize(filename)
					nChunck = filesize / 4096

					if (filesize % 4096)!= 0:
						nChunk = nChunk + 1

					nChunk = int(float(nChunk))
					msg = "ARET" + str(nChunk).zfill(6)
					print ('Trasferimento in corso di ', resultFile[0], '[BYTES ', filesize, ']')

					i = 0

					while i < nChunk:
						buf = os.read(fd,4096)
						if not buf: break
						lbuf = len(buf)
						lbuf = str(lbuf).zfill(5)
						msg = msg + str(lbuf) + str(buf)
						i = i + 1
					
					os.close(fd)
					print('Trasferimento completato.. ')
					
					#invio del file, leggere l'ip dall'oggetto connection	
					connection.sendall(msg.encode())
					connection.close()

				else: 
					print("Errore nell'apertura del file")
				
			elif command == "ANEA":
				print("Ricevuto "+color.recv+"ANEA"+color.end)
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
					print(color.fail+"ricevuto pacchetto dopo 300s"+color.end)
			
			elif command == "AQUE":
				print("Ricevuto "+color.recv+"AQUE"+color.end)
				
				Pktid = connection.recv(16).decode()
				IPP2P = connection.recv(55).decode()
				PP2P = connection.recv(5).decode()
				Filemd5 = connection.recv(32).decode()
				Filename = connection.recv(100).decode()
				
				self.dbReader.execute("SELECT Timestamp FROM Pktid WHERE Pktid = ?", (Pktid, ))
				t = self.dbReader.fetchone()
				
				if getTime(t[0]) < 300 :
					#controllo se il file esiste già nel db
					self.dbReader.execute("SELECT Filemd5 FROM File WHERE FileMD5 = ?", (Filemd5, ))
					data = self.dbReader.fetchone()
					
					if data is None:
						#se il file non esiste nel db lo inserisco
						self.dbReader.execute("INSERT INTO File (Filemd5, Filename, IPP2P) values (?, ?, ?)", (Filemd5, Filename, IPP2P))
						print(color.green + "Aggiunto alla lista un nuovo file" + color.end)
					else:
						print(color.fail + "File già presente" + color.end)
				else:
					print(color.fail+"Ricevuto pacchetto dopo 300s"+color.end)
				
			elif command == "ARET":
				print("Ricevuto "+color.recv+"ARET"+color.end)
				try:
					
					filename = self.download
					
					fd = os.open(filename, os.O_WRONLY | os.O_CREAT, 777)
						
					nChunk = int(connection.recv(6).decode())
					i=0;
						
					while i < nChunk:
						lun = int(connection.recv(5).decode())
						data = connection.recv(lun).decode()
							#scrittura del file
						os.write(fd,data)
						
					print(color.green + "Scaricato il file" + color.end)
							
				except OSError:
					print("Impossibile aprire il file: controlla di avere i permessi")
					return False
					
		except:
			connection.close()
			return False
				
		
if __name__ == "__main__":
    gnutella = GnutellaServer()
gnutella.server()

