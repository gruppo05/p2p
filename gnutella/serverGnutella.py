import socket, sqlite3, string, subprocess, threading, os
from random import *

def clearAndSetDB(self):
	self.dbReader.execute("DROP TABLE IF EXISTS user")
	self.dbReader.execute("DROP TABLE IF EXISTS file")
	self.dbReader.execute("DROP TABLE IF EXISTS download")
	self.dbReader.execute("CREATE TABLE user (SessionID text, IPP2P text, PP2P text)")
	self.dbReader.execute("CREATE TABLE file (Filemd5 text, Filename text, SessionID text)")
	self.dbReader.execute("CREATE TABLE download (Filemd5 text, Download integer)")

def splitIp(ip):
	splitted = ip.split(".")
	ip = str(int(splitted[0]))+"."+str(int(splitted[1]))+"."+str(int(splitted[2]))+"."+str(int(splitted[3]))
	
class color:
	HEADER = '\033[95m'
	recv = '\033[36m'
	green = '\033[32m'
	send = '\033[33m'
	fail = '\033[31m'
	end = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

class GnutellaServer(object):
	def __init__(self):
		IP = ''
		PORT = 3000
		UDP_IP = "127.0.0.1"
		UDP_PORT = 49999
		# Creo DB
		conn = sqlite3.connect(':memory:')
		self.dbReader = conn.cursor()
		# Creo tabella user
		clearAndSetDB(self)
		# Socket ipv4/ipv6
		self.server_address = (IP, PORT)
		self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind(self.server_address)
		self.sock.listen(5)
		
		# socket upd ipv4 internal Server
		self.sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sockUDP.bind((UDP_IP, UDP_PORT))
		
		
	def internalServer(self):
		print(color.green+"In attesa di comandi interni..."+color.end)
		#splitIp("192.168.001.002")
		while True:
			data, addr = self.sockUDP.recvfrom(4)
			print("Ricevuto comando: "+color.recv+data.decode()+color.end)
			print("\n")
		
	def server(self):
		#crea thread interno per far comunicare client e server
		threading.Thread(target = self.internalServer, args = '').start()
		print(color.green+"In attesa di connessione esterna..."+color.end)
		connection, client_address = self.sock.accept()

		while True:
			try:
				if command == "QUER":
					print("QUER")
				elif command == "NEAR":
					print("NEAR")
				elif command == "RETR":
					print("RETR")
					
					#inviare un file che ho
					#leggo il filemd5 dal client o dalla connessione?
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
					
			except:
				print("Errore lato server")
			finally:
				print("\n\n")
				
		
if __name__ == "__main__":
    gnutella = GnutellaServer()
gnutella.server()











