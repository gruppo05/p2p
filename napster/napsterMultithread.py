import socket, sqlite3, string, threading
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
	self.dbReader.execute("DROP TABLE IF EXISTS user")
	self.dbReader.execute("DROP TABLE IF EXISTS file")
	self.dbReader.execute("DROP TABLE IF EXISTS download")
	self.dbReader.execute("CREATE TABLE user (SessionID text, IPP2P text, PP2P text)")
	self.dbReader.execute("CREATE TABLE file (Filemd5 text, Filename text, SessionID text)")
	self.dbReader.execute("CREATE TABLE download (Filemd5 text, Download integer)")
	
	
def sessionIdGenerator():
	return "".join(choice(string.ascii_letters + string.digits) for x in range(16))
	

def setCopy(getCopy):
	copy = int(getCopy[0])
	if copy > 1000:
		copy = 999
	elif copy < 100 and copy > 9:
		copy = "0"+str(copy)
	elif copy < 10:
		copy = "00"+str(copy)
	return copy
	

def setDownload(getDownload):
	download = int(getDownload[0])
	if download > 100000:
		download = 99999
	elif download < 10000 and download > 999:
		download = "0"+str(download)
	elif download < 1000 and download > 99:
		download = "00"+str(download)
	elif download < 100 and download > 9:
		download = "000"+str(download)
	elif download < 10:
		download = "0000"+str(download)
	return download
	

class Napster(object):
	def __init__(self):
		IP = ''
		PORT = 3000
		
		# Creo DB
		conn = sqlite3.connect(':memory:', check_same_thread=False)
		self.dbReader = conn.cursor()
		# Creo tabella user
		clearAndSetDB(self)		
		# Socket ipv4/ipv6
		self.server_address = (IP, PORT)
		self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind(self.server_address)
		
	def listener(self):
		self.sock.listen(5)
		print("In attesa di connessione...")
		while True:
			try:
				connection, client_address = self.sock.accept()
				#connection.settimeout(60)
				threading.Thread(target = self.startClient, args = (connection,client_address)).start()
			except:
				return False
			
	def startClient(self, connection, client_address):
		while True:
			try:
				command = connection.recv(4).decode()
				if command == "LOGI":
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
						print("Invio il SessionID --> "+ color.send + SessionID + color.end)
						
				elif command == "LOGO":
					SessionID = connection.recv(16).decode()
					print("Ricevuto " + color.recv + command + color.end + " da " + color.recv + SessionID + color.end)
					#conto i file associati all'utente
					self.dbReader.execute("SELECT COUNT(Filemd5) from file where SessionID=?",(SessionID,))
					delete = self.dbReader.fetchone()
					delete = setCopy(delete)
					self.dbReader.execute("DELETE FROM file WHERE SessionID=?", (SessionID,))
					self.dbReader.execute("DELETE FROM user WHERE SessionID=?", (SessionID,))
					#magari controllo se è andato a buon fine?
					print("Invio --> "+ color.send + "ALGO" + delete + color.end)
					connection.sendall(("ALGO"+delete).encode())
					connection.close()
					return False
				
				elif command == "DELF":
					SessionID = connection.recv(16).decode()
					Filemd5 = connection.recv(32).decode()
					print("Ricevuto "+ color.recv + command + color.end + " da " + color.recv + SessionID + color.end)
					self.dbReader.execute("SELECT count(*) FROM file WHERE Filemd5=?", (Filemd5,))
					copy = self.dbReader.fetchone()
					if copy[0] is 0:
						print(color.fail+ "NESSUN FILE TROVATO" + color.end);
						copy = "999"
					else:
						self.dbReader.execute("DELETE FROM file WHERE Filemd5=? AND SessionID=?", (Filemd5,SessionID,))
					print("Inviato numero di copie --> " + color.send + "ADEL" + copy + color.end)
					connection.sendall(("ADEL"+str(copy)).encode())

				elif command == "FIND":
					SessionID = connection.recv(16).decode()
					Ricerca = connection.recv(20).decode()
					print("Ricevuto "+ color.recv + command + color.end + " da " + color.recv + SessionID + color.end)
					
					#Conto quanti file con filemd5 diverso ci sono con filename simile a ricerca
					self.dbReader.execute("SELECT count(*) FROM (SELECT DISTINCT Filemd5 FROM file WHERE Filename LIKE ?)", ('%' + Ricerca + '%',))
					idmd5 = self.dbReader.fetchone()

					#Prendo tutti i filemd5 singolarmente
					self.dbReader.execute("SELECT DISTINCT Filemd5 FROM file WHERE Filename LIKE ?", ('%' + Ricerca + '%',))
					resultFilemd5 = self.dbReader.fetchall()
					#Per ogni file ciclo per cercare chi ha questi file
					idmd5 = setCopy(idmd5)

					msg = "AFIN" + idmd5
					for md5 in resultFilemd5:
						self.dbReader.execute("SELECT Filename FROM file WHERE filemd5 = ?",(md5[0],))
						resultFilename = self.dbReader.fetchone()
						self.dbReader.execute("SELECT count(*) FROM file WHERE Filemd5=?", (md5[0],))
						print("md5 i-esimo= ", md5[0])
						copy = self.dbReader.fetchone()
						copy = setCopy(copy)
						self.dbReader.execute("SELECT IPP2P, PP2P FROM user JOIN file WHERE user.SessionID = file.SessionID AND filemd5 = ?", (md5[0],))
						resultIP = self.dbReader.fetchall()
						msg = msg + md5[0] + resultFilename[0] + copy
						for ip in resultIP:
							msg = msg + ip[0] + ip[1]
					
					print("Invio --> " + color.send + msg + color.end)
					connection.sendall(msg.encode())

				elif command == "ADDF":
					SessionID = connection.recv(16).decode()
					print("Ricevuto "+ color.recv + command + color.end + " da " + color.recv + SessionID + color.end)
					Filemd5 = connection.recv(32).decode()
					Filename = connection.recv(100).decode()
					
					self.dbReader.execute("SELECT SessionID from file where Filemd5=? and SessionID=?",(Filemd5,SessionID,))
					data = self.dbReader.fetchone()
					
					if data is None:
						self.dbReader.execute("INSERT INTO file (Filemd5, Filename, SessionID) values (?, ?, ?)",(Filemd5, Filename, SessionID))
					self.dbReader.execute("UPDATE file SET Filename=?",(Filename,))
					self.dbReader.execute("SELECT COUNT(Filemd5) from file where Filemd5=?",(Filemd5,))
					copy = self.dbReader.fetchone()
					copy = setCopy(copy)
					
					print("Invio --> " + color.send + "AADD" + copy + color.end)
					connection.sendall(("AADD"+copy).encode())
				
				elif command == "DREG":
					SessionID = connection.recv(16).decode()
					print("Ricevuto "+ color.recv + command + color.end + " da " + color.recv + SessionID + color.end)
					Filemd5 = connection.recv(32).decode()
					self.dbReader.execute("SELECT Download FROM download WHERE Filemd5 = ?",(Filemd5,))
					download = self.dbReader.fetchone()

					if download is None:
						download[0] = 1
						self.dbReader.execute("INSERT INTO download (Filemd5, Download) values (?, ?)", (Filemd5, 1))
					else:
						download[0] = download[0] + 1
						self.dbReader.execute("UPDATE download SET Download = ? WHERE Filemd5 = ?",(download[0], Filemd5,))

					download = setDownload(download)
					print("Invio --> " + color.send + "ADRE" + download + color.end)
					connection.sendall(("ADRE"+download).encode())
		
				# *************** DA TOGLIERE *********************

				elif command == "STAU":
					#Stampo user
					self.dbReader.execute("SELECT * FROM user")
					for row in self.dbReader:
						print(row)

				elif command == "STAF":
					#Stampo file
					self.dbReader.execute("SELECT * FROM file")
					for row in self.dbReader:
						print(row)

				elif command == "STAD":
					#Stampo download
					self.dbReader.execute("SELECT * FROM download")
					for row in self.dbReader:
						print(row)
	
				# *************************************************
			except:
				connection.close()
				return False
			
if __name__ == "__main__":
    napster = Napster()
napster.listener()
