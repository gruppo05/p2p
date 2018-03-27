import socket, sqlite3, string, subprocess, os
from random import *

def clearAndSetDB(self):
	self.dbReader.execute("DROP TABLE IF EXISTS user")
	self.dbReader.execute("DROP TABLE IF EXISTS file")
	self.dbReader.execute("DROP TABLE IF EXISTS download")
	self.dbReader.execute("CREATE TABLE user (SessionID text, IPP2P text, PP2P text)")
	self.dbReader.execute("CREATE TABLE file (Filemd5 text, Filename text, SessionID text)")
	self.dbReader.execute("CREATE TABLE download (Filemd5 text, Download integer)")

class Gnutella(object):
	def __init__(self):
		'''IP = ''
		PORT = 3000
		# Creo DB
		conn = sqlite3.connect(':memory:')
		self.dbReader = conn.cursor()
		# Creo tabella user
		clearAndSetDB(self)
		# Socket ipv4/ipv6
		self.server_address = (IP, PORT)
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind(self.server_address)
		self.sock.listen(5)'''
		
	def start(self):
		
		os.system("gnome-terminal -e 'sh -c \"python3 serverGnutella.py\"'")
		
		#os.system("gnome-terminal -x python test.py")
		''' connection, client_address = self.sock.accept()
		
		while True:
			print("In attesa di connessione...")
			
			try:
				if command == "1":
					print("primo")
				elif command == "2":
					print("secondo")
				elif command == "3":
					print("Download")
					print("Quale file vuoi scaricare?")
					self.dbReader.execute("SELECT * FROM File WHERE IPP2P != ?", (IP,))
					resultFile = self.dbReader.fetchall()
					
					files[0] = ("0","0","0")
					int i = 1
					for resultFile in resultFile:
						files[i] = (resultFile[0], resultFile[1], resultFile[2])
						print(i + " - " + resultFile[1])
						
					code = input("\n ")	
					
					connection.sendall(("RETR" + files[code][0]).encode())
					
			except:
				print("Errore lato server")
			finally:
				print("\n\n")
		'''	

if __name__ == "__main__":
    gnutella = Gnutella()
gnutella.start()
