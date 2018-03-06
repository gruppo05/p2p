import socket
import sqlite3
import random
import string
from random import *

def sessionIdGenerator():
	return "".join(choice(string.ascii_letters + string.digits) for x in range(16))

class Napster(object):
	def start(self):
		#Clear all the db al primo lancio??
		
		IP = "127.0.0.1"
		PORT = 3000
		
		# Creo DB
		conn = sqlite3.connect(':memory:')
		print("Creato db", conn)
		c = conn.cursor()
		
		# Creo tabella user
		c.execute("DROP TABLE IF EXISTS user")
		c.execute('''CREATE TABLE user (SessionID text, IPP2P text, PP2P text)''')
		print("Tabella user creata...")
		
		# Creo socket
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_address = (IP, PORT)
		sock.bind(server_address)
		
		print("Server attivo su porta", server_address)
		sock.listen(1)
		while True:
			print("In attesa di connessione...")
			connection, client_address = sock.accept()
			
			try:
				print("Connessione da", client_address)
				command = connection.recv(4).decode()
				print("Ricevuto", command)
				if command == "LOGI":
					IPP2P = connection.recv(55).decode()
					IPP = connection.recv(5).decode()
					print("IPP2P = ",IPP2P," IPP = ",IPP)
					#Cerco IP utente
					result = c.execute("SELECT SessionID FROM user WHERE IPP2P=?", (IPP2P,))
					if result.fetchone() is None:
						print("*************** NON TROVATO ***************")
						SessionID = sessionIdGenerator()
						#Inserimento
						c.execute("INSERT INTO user (SessionID, IPP2P, PP2P) values (?, ?, ?)",(SessionID, IPP2P, IPP))
					else:
						print("*************** TROVATO ***************")
						c.execute("SELECT SessionID FROM user WHERE IPP2P=?", (IPP2P,))
						data = c.fetchone() #retrieve the first row
						SessionID = data[0]
					print("SessionID:", SessionID)
					connection.sendall(SessionID.encode())
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
					c.execute("SELECT * FROM user")
					for row in c:
						print(row)
				# *************************************************
			except:
				print("Errore lato server")
			finally:
				connection.close()
				
if __name__ == "__main__":
    napster = Napster()
napster.start()










































