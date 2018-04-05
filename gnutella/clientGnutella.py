import socket, sqlite3, string, subprocess, os, time
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

def startServer():
	os.system("gnome-terminal -e 'sh -c \"python3 serverGnutella.py\"'")

def printMenu():
	print(color.recv+"  ____  "+ color.green+"        "+ color.send+"        "+ color.fail+" _    "+ color.recv+"       "+ color.green+" _  "+ color.send+" _  "+ color.green+"        "+ color.fail+"  ____  _____   ____  "+ color.end)
	print(color.recv+" / ___| "+ color.green+" _ __   "+ color.send+" _   _  "+ color.fail+"| |_  "+ color.recv+"  ___  "+ color.green+"| | "+ color.send+"| | "+ color.green+"  __ _  "+ color.fail+" |  _ \ \__  \ |  _ \ "+ color.end)
	print(color.recv+"| |  _  "+ color.green+"| '_ \  "+ color.send+"| | | | "+ color.fail+"| __/ "+ color.recv+" / _ \ "+ color.green+"| | "+ color.send+"| | "+ color.green+" / _` | "+ color.fail+" | |_) | __) | | |_) |"+ color.end)
	print(color.recv+"| |_| | "+ color.green+"| | | | "+ color.send+"| |_| | "+ color.fail+"| |_  "+ color.recv+"|  __/ "+ color.green+"| | "+ color.send+"| | "+ color.green+"| (_| | "+ color.fail+" |  __/ / __/  |  __/ "+ color.end)
	print(color.recv+" \____| "+ color.green+"|_| |_| "+ color.send+" \__,_| "+ color.fail+" \__\ "+ color.recv+" \___| "+ color.green+"|_| "+ color.send+"|_| "+ color.green+" \__,_| "+ color.fail+" |_|   |_____| |_|    "+ color.end)
	print("\n")
	print("« 1 » RICERCA VICINI")
	print("« 2 » RICERCA FILE")
	print("« 3 » SCARICA FILE")
	print("« 4 » STAMPA TUTTI I VICINI")
	print("« 5 » STAMPA TUTTI I FILE TROVATI")
	print(color.fail+"« 6 » CHIUDI IL CLIENT"+color.end)


class GnutellaClient(object):
	def __init__(self):
		self.UDP_IP = "127.0.0.1"
		self.UDP_PORT = 49999
		
		# Socket UDP ipv4 interna
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		
	def start(self):
		os.system('cls' if os.name == 'nt' else 'clear')
		startServer()
		while True:
			time.sleep(0.5)
			printMenu()
			
			try:
				cmd = input("\nDigita cosa vuoi fare:\n")
			except:
				continue
			if cmd is "1":
				print("INIZIO RICERCA VICINI")
				self.sock.sendto(("NEAR").encode(), (self.UDP_IP, self.UDP_PORT))
			elif cmd is "2":
				print("INIZIO RICERCA FILE")
				self.sock.sendto(("QUER").encode(), (self.UDP_IP, self.UDP_PORT))
				#Inserisci nome da cercare
				self.so
			elif cmd is "3":
				print("INIZIO DOWNLOAD")
				print("Quale file vuoi scaricare?")
				self.sock.sendto(("RETR").encode(), (self.UDP_IP, self.UDP_PORT))
				
				lunghezza = self.sockUDP.recvfrom(2)
				
				i = 0
				
				while i < int(lunghezza):
					filename[i] = self.sockUDP.recvfrom(100)
					print(i + " : " + filename[i])
				
				code = input("\n ")	
				
				if len(code) == 1:
					code = "0"+code
				else:
					code = str(code)
				
				#la connessione avviene sul client o sul server??
				self.sock.sendto((code).encode(), (self.UDP_IP, self.UDP_PORT))
			
			elif cmd is "4":
				print("STAMPA TUTTI I VICINI")
				self.sock.sendto(("STMV").encode(), (self.UDP_IP, self.UDP_PORT))
			elif cmd is "5":
				print("STAMPA TUTTI I FILE TROVATI")
				self.sock.sendto(("STMF").encode(), (self.UDP_IP, self.UDP_PORT))
			elif cmd is "6":
				#stopServer()
				os._exit(0)
			print("\n")
			
if __name__ == "__main__":
    gnutella = GnutellaClient()
gnutella.start()






