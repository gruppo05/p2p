import socket
import sqlite3
import random
import string
from random import *

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
		IP = "127.0.0.1"
		PORT = 3000
		
		# Creo DB
		conn = sqlite3.connect(':memory:')
		print("Creato db", conn)
		self.dbReader = conn.cursor()
		
		# Creo tabella user
		self.dbReader.execute("DROP TABLE IF EXISTS user")
		self.dbReader.execute("CREATE TABLE user (SessionID text, IPP2P text, PP2P text)")
		self.dbReader.execute("CREATE TABLE file (Filemd5 text, filename text, SessionID text)")
		print("Tabelle user, file create...")
		
		# Creo socket
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server_address = (IP, PORT)
		self.sock.bind(self.server_address)
		print("Server attivo su porta", self.server_address)
		self.sock.listen(1)
		
	def start(self):
		while True:
			print("In attesa di connessione...")
			connection, client_address = self.sock.accept()
			
			try:
				print("Connessione da", client_address)
				command = connection.recv(4).decode()
				print("Ricevuto", command)
				if command == "LOGI":
					IPP2P = connection.recv(55).decode()
					IPP = connection.recv(5).decode()
					print("IPP2P = ",IPP2P," IPP = ",IPP)					
					#Cerco IP utente
					self.dbReader.execute("SELECT SessionID FROM user WHERE IPP2P=?", (IPP2P,))
					data = self.dbReader.fetchone() #retrieve the first row
					if data is None:
						print("*************** NON TROVATO ***************")
						SessionID = sessionIdGenerator()
						#Inserimento
						self.dbReader.execute("INSERT INTO user (SessionID, IPP2P, PP2P) values (?, ?, ?)",(SessionID, IPP2P, IPP))
					else:
						print("*************** TROVATO ***************")
						SessionID = data[0]
					print("SessionID:", SessionID)
					connection.sendall(SessionID.encode())
					print("...Inviato il SessionID")
					#Da implementare processio di invio del SessionID...
				elif command == "DELF":
					print("Delete file")
				elif command == "FIND":
					print("Find file name")
				elif command == "ADDF":
					print("Add file")
					SessionID = connection.recv(16).decode()
					Filemd5 = connection.recv(32).decode()
					Filename = connection.recv(100).decode()
					
					self.dbReader.execute("SELECT SessionID from file where Filemd5=?",(Filemd5,))
					data = self.dbReader.fetchone()
					if data is None:
						self.dbReader.execute("INSERT INTO file (Filemd5, Filename, SessionID) values (?, ?, ?)",(Filemd5, Filename, SessionID))
					else:
						self.dbReader.execute("UPDATE file SET Filename=?",(Filename,))
					self.dbReader.execute("SELECT COUNT(Filemd5) from file where Filemd5=?",(Filemd5,))
					copy = self.dbReader.fetchone()
					copy = setCopy(copy)
					connection.sendall(("AADD"+copy).encode())
					
				elif command == "LOGO":
					print("Log out")
				elif command == "DREG":
					print("Download")
					
				# *************** DA TOGLIERE *********************
				elif command == "STAM":
					#Stampo
					self.dbReader.execute("SELECT * FROM user")
					for row in self.dbReader:
						print(row)
				# *************************************************
				# *************** DA TOGLIERE *********************
				elif command == "DEKK":
					#Stampo
					self.dbReader.execute("SELECT * FROM file")
					for row in self.dbReader:
						print(row)
				# *************************************************
			except:
				print("Errore lato server")
			finally:
				connection.close()
				
if __name__ == "__main__":
    napster = Napster()
napster.start()
