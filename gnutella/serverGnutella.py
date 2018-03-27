import socket, sqlite3, string, subprocess, threading, os
from random import *

def clearAndSetDB(self):
	self.dbReader.execute("DROP TABLE IF EXISTS user")
	self.dbReader.execute("DROP TABLE IF EXISTS file")
	self.dbReader.execute("DROP TABLE IF EXISTS download")
	self.dbReader.execute("CREATE TABLE user (SessionID text, IPP2P text, PP2P text)")
	self.dbReader.execute("CREATE TABLE file (Filemd5 text, Filename text, SessionID text)")
	self.dbReader.execute("CREATE TABLE download (Filemd5 text, Download integer)")

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
		print("IN ASCOLTO PROCESSO UDP SERVER...")
		while True:
			data, addr = self.sockUDP.recvfrom(4)
			print("Ricevuto comando: "+color.recv+data.decode()+color.end)
		
	def server(self):
		#crea thread 
		threading.Thread(target = self.internalServer, args = '').start()
		
		print("IN ASCOLTO PROCESSO SERVER...")
		connection, client_address = self.sock.accept()
		while True:
			print("ciao")
		while True:
			print("In attesa di connessione...")
			
			try:
				if command == "QUER":
					print("QUER")
				elif command == "NEAR":
					print("NEAR")
				elif command == "RETR":
					print("RETR")
					
			except:
				print("Errore lato server")
			finally:
				print("\n\n")
				
		
if __name__ == "__main__":
    gnutella = GnutellaServer()
gnutella.server()











