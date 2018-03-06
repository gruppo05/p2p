import socket
import sqlite3
import random
import string
from random import *

def sessionIdGenerator():
	return "".join(choice(string.ascii_letters + string.digits) for x in range(16))

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
		self.dbReader.execute('''CREATE TABLE user (SessionID text, IPP2P text, PP2P text)''')
		print("Tabella user creata...")

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
					result = self.dbReader.execute("SELECT SessionID FROM user WHERE IPP2P=?", (IPP2P,))
					if result.fetchone() is None:
						print("*************** NON TROVATO ***************")
						SessionID = sessionIdGenerator()
						#Inserimento
						self.dbReader.execute("INSERT INTO user (SessionID, IPP2P, PP2P) values (?, ?, ?)",(SessionID, IPP2P, IPP))
					else:
						print("*************** TROVATO ***************")
						self.dbReader.execute("SELECT SessionID FROM user WHERE IPP2P=?", (IPP2P,))
						data = self.dbReader.fetchone() #retrieve the first row
						SessionID = data[0]
					print("SessionID:", SessionID)
					connection.sendall(("ALGI", SessionID).encode())
					print("Inviato il session ID")
					#Da implementare processio di invio del SessionID...
				elif command == "DELF":
					print("Delete file")
				elif command == "FIND":
					print("Find file name")
				elif command == "ADDF":
					print("Add file")
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
			except:
				print("Errore lato server")
			finally:
				connection.close()
				
if __name__ == "__main__":
    napster = Napster()
napster.start()
