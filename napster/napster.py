import socket, sqlite3, string
from random import *

def clearAndSetDB(self):
	self.dbReader.execute("DROP TABLE IF EXISTS user")
	self.dbReader.execute("DROP TABLE IF EXISTS file")
	self.dbReader.execute("DROP TABLE IF EXISTS download")
	self.dbReader.execute("CREATE TABLE user (SessionID text, IPP2P text, PP2P text)")
	self.dbReader.execute("CREATE TABLE file (Filemd5 text, Filename text, SessionID text)")
	self.dbReader.execute("CREATE TABLE download (Filemd5 text, Download text)")
	print("Tabelle user, file create...")
	
def sessionIdGenerator():
	return "".join(choice(string.ascii_letters + string.digits) for x in range(16))

def setCopy(getCopy):
	copy = int(getCopy[0])
	print(copy)
	if copy > 1000:
		copy = 999
	elif copy < 100 and copy > 9:
		copy = "0"+str(copy)
	elif copy < 10:
		copy = "00"+str(copy)
	return copy

class Napster(object):
	def __init__(self):
		IPv4 = "127.0.0.1"
		IPv6 = "0000:0000:0000:0000:0000:0000:0000:0001"
		PORT = 3000
		
		# Creo DB
		conn = sqlite3.connect(':memory:')
		print("Creato db", conn)
		self.dbReader = conn.cursor()
		
		# Creo tabella user
		clearAndSetDB(self)
		
		# Socket ipv4
		self.server_address = (IPv4, PORT)
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind(self.server_address)
		self.sock.listen(5)
		
		# Socket ipv6
		#self.server_address = (IPv6, PORT)
		#self.sock6 = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		#self.sock6.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		#self.sock6.bind(self.server_address6)
		#self.sock6.listen(5)
		
	def start(self):
		while True:
			print("In attesa di connessione...")
			try:
				connection, client_address = self.sock.accept()
			except:
				connection, client_address = self.sock6.accept()
			
			try:
				print("Connessione da", client_address)
				command = connection.recv(4).decode()
				print("\nRicevuto", command)
				if command == "LOGI":
					try:
						IPP2P = connection.recv(55).decode()
						IPP = connection.recv(5).decode()
						print("IPP2P = ",IPP2P," IPP = ",IPP)					
						#Cerco IP utente
						self.dbReader.execute("SELECT SessionID FROM user WHERE IPP2P=?", (IPP2P,))
						data = self.dbReader.fetchone() #retrieve the first row
						if data is None:
							print("*************** NUOVO UTENTE ***************")
							SessionID = sessionIdGenerator()
							#Inserimento
							self.dbReader.execute("INSERT INTO user (SessionID, IPP2P, PP2P) values (?, ?, ?)",(SessionID, IPP2P, IPP))
						else:
							print("*************** BENTORNATO ***************")
							SessionID = str(data[0])
						print("SessionID:", SessionID)
					except:
						SessionID = "0000000000000000"
					finally:
						connection.sendall(("ALGI"+SessionID).encode())
						print("Invio il SessionID --> "+SessionID)
						
						
				elif command == "DELF":
					print("Delete file")
					SessionID = connection.recv(16).decode()
					Filemd5 = connection.recv(32).decode()
					self.dbReader.execute("SELECT count(*) FROM file WHERE Filemd5=?", (Filemd5,))
					copy = self.dbReader.fetchone()
					if copy[0] is 0:
						print("************** NESSUN FILE TROVATO **************");
						copy = "999"
					else:
						print("Copie trovate ->",copy);
						self.dbReader.execute("DELETE FROM file WHERE Filemd5=? AND SessionID=?", (Filemd5,SessionID,))
					connection.sendall(("ADEL"+str(copy)).encode())
					print("Inviato numero di copie --> ",copy)
					
				#--------------------DA TESTARE-------------------------------------------------#	
				elif command == "FIND":
					print("Find file name")
					SessionID = connection.recv(16).decode()
					Ricerca = connection.recv(20).decode()
					#Conto quanti file con filemd5 diverso ci sono con filename simile a ricerca
					self.dbReader.execute("SELECT count(*) FROM file WHERE Filename LIKE ? GROUP BY Filemd5", ('%' + Ricerca + '%',))
					idmd5 = self.dbReader.fetchone()
					#Prendo tutti i filemd5 singolarmente
					self.dbReader.execute("SELECT DISTINCT Filemd5 FROM file WHERE Filename LIKE ?", ('%' + Ricerca + '%',))
					resultFilemd5 = self.dbReader.fetchall()
					
					#Per ogni file ciclo per cercare chi ha questi file
					#-------------->
					#Fix_bertasi
					idmd5 = setCopy(idmd5)
					#<--------------
					
					msg = "AFIN" + idmd5
					for md5 in resultFilemd5:
						self.dbReader.execute("SELECT Filename FROM file WHERE filemd5 = ?",(md5[0],))
						resultFilename = self.dbReader.fetchone()
						self.dbReader.execute("SELECT count(*) FROM file WHERE Filemd5=?", (Filemd5,))
						copy = self.dbReader.fetchone()
						self.dbReader.execute("SELECT IPP2P, PP2P FROM user JOIN file WHERE user.SessionID = file.SessionID AND filemd5 = ?", (md5[0]))
						resultIP = self.dbReader.fetchall()
						msg = msg + md5[0] + resultFilename + copy
						for ip in resultIP:
							msg = msg + ip
					
					connection.sendall(msg.encode())
				#---------------------------------------------------------------------------------#
					
				elif command == "ADDF":
					print("Add file")
					SessionID = connection.recv(16).decode()
					Filemd5 = connection.recv(32).decode()
					Filename = connection.recv(100).decode()
					print(SessionID)
					print(Filemd5)
					print(Filename)
					self.dbReader.execute("SELECT SessionID from file where Filemd5=? and SessionID=?",(Filemd5,SessionID,))
					data = self.dbReader.fetchone()
					if data is None:
						self.dbReader.execute("INSERT INTO file (Filemd5, Filename, SessionID) values (?, ?, ?)",(Filemd5, Filename, SessionID))
					self.dbReader.execute("UPDATE file SET Filename=?",(Filename,))
					self.dbReader.execute("SELECT COUNT(Filemd5) from file where Filemd5=?",(Filemd5,))
					copy = self.dbReader.fetchone()
					copy = setCopy(copy)
					connection.sendall(("AADD"+copy).encode())
					
					
				elif command == "LOGO":
					print("Log out")
					SessionID = connection.recv(16).decode()
					print(SessionID)
					#conto i file associati all'utente
					self.dbReader.execute("SELECT COUNT(Filemd5) from file where SessionID=?",(SessionID,))
					delete = self.dbReader.fetchone()
					delete = setCopy(delete)
					self.dbReader.execute("DELETE FROM file WHERE SessionID=?", (SessionID,))
					#magari controllo se è andato a buon fine?
					connection.sendall(("ALGO"+delete).encode())
					
				elif command == "DREG":
					print("Download")
					SessionID = connection.recv(16).decode()
					Filemd5 = connection.recv(32).decode()
					idmd5=self.dbReader.fetchone()
					
					#Fix_bertasi
					#-------------->
					idmd5 = setCopy(idmd5)
					#<--------------
					
					msg="ADRE"+idmd5
					connection.sendall(msg.encode())
					
						
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
				
				else: 
					print("Nessuna operazione")
			except:
				print("Errore lato server")
			finally:
				print("\n\n")
				connection.close()
				

if __name__ == "__main__":
    napster = Napster()
napster.start()
