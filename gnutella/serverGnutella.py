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
		IP = ''
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
		self.sock.listen(5)
		
	def start(self):
		while True:
			print("nuovo terminale")
			print("ciao")
			
			command = connection.recv(4).decode()
			
			if command == "RETR"
				
				FileMD5 = connection.recv(55).decode()
				self.dbReader.execute("SELECT Filename FROM File WHERE FileMD5 = ?",(FileMD5,))
				resultFile = self.dbReader.fetchone()
				f = os.open(str(resultFile), os.O_RDONLY)
				
				filesize = os.fstat(fd)[stat.ST.SIZE]
				nChunck = filesize / 4096
				
				if (filesize % 4096)!= 0:
					nChunk = nChunk + 1
				
				nChunk = int(float(nChunk))
				pacchetto = "ARET" + str(nChunk).zfill(6)
				sock.send(pacchetto.encode())
				print ('Trasferimento in corso di ', resultFile, '[BYTES ', filesize, ']')
				
				i = 0
				
				while i < nChunk:
					buf = os.read(fd,4096)
					if not buf: break
					lbuf = len(buf)
					lbuf = str(lBuf).zfill(5)
					sock.send(lBuf.encode())
					sock.send(buf)
					i = i + 1
					
				os.close(fd)
				print('Trasferimento completato.. ')
				
				#chiusura della connessione
				connection.close()
				#chiusura della socket
				sock.close()

		
if __name__ == "__main__":
    gnutella = Gnutella()
gnutella.start()
