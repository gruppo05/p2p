import socket, sqlite3, string, subprocess, os, time, sys
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
	os.system("gnome-terminal -e 'sh -c \"python3 serverKazaa.py\"'")

def stopServer():
	##os.system("kill $(ps aux | grep '.py' | awk '{print $2}')") #questo killa anche gedit se il file si chiama .py
	os._exit(0)

def printMenu():
	os.system('cls' if os.name == 'nt' else 'clear')
	print(color.recv+" _  __ "+ color.green+"        "+ color.send+"       "+ color.fail+"        "+ color.recv+"        "+ color.fail+"  ____  _____   ____  "+ color.end)
	print(color.recv+"| |/ / "+ color.green+"  __ _  "+ color.send+" ____  "+ color.fail+"  __ _  "+ color.recv+"  __ _  "+ color.fail+" |  _ \ \__  \ |  _ \ "+ color.end)
	print(color.recv+"| ' /  "+ color.green+" / _` | "+ color.send+"|_  /  "+ color.fail+" / _` | "+ color.recv+" / _` | "+ color.fail+" | |_) | __) | | |_) |"+ color.end)
	print(color.recv+"| | \  "+ color.green+"| (_| | "+ color.send+" / /_  "+ color.fail+"| (_| | "+ color.recv+"| (_| | "+ color.fail+" |  __/ / __/  |  __/ "+ color.end)
	print(color.recv+"|_|\_\ "+ color.green+" \__,_/ "+ color.send+"/____\ "+ color.fail+" \__,_| "+ color.recv+" \__,_| "+ color.fail+" |_|   |_____| |_|    "+ color.end)
	print("\n")
	print("« 1 » LOGIN")
	print("« 2 » AGGIUNTA FILE")
	print("« 3 » RIMOZIONE FILE")
	print("« 4 » RICERCA FILE")
	print("« 5 » DOWNLOAD FILE")
	print("« 6 » LOGOUT")
	print(color.fail+"« 7 » CHIUDI IL CLIENT"+color.end)

def progBar(i):
	bar_length = 60
	hashes = '#' * i * 3
	spaces = ' ' * (bar_length - len(hashes))
	sys.stdout.write("\r[{0}] {1}s".format(hashes + spaces, int(i)))
	
class kazaaClient(object):
	def __init__(self):
		self.UDP_IP = "127.0.0.1"
		self.UDP_PORT_SERVER = 49999
		UDP_PORT_CLIENT = 50000
		self.endUDP1 = "";
		
		# Socket UPD ipv4 client in attesa
		self.sockUDPClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sockUDPClient.bind((self.UDP_IP, UDP_PORT_CLIENT))
		
		# Socket UDP ipv4 server in uscita
		self.sockUDPServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	
	def start(self):
		startServer()
		os.system('cls' if os.name == 'nt' else 'clear')
		
		#ricerca super nodi
		time.sleep(0.1)
		print("RICERCA SUPERNODI"+color.green)
		self.sockUDPServer.sendto(("SUPE").encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
		i = 0
		while i < 20:
			progBar(i)
			time.sleep(0.1)
			i = i+1
		self.sockUDPServer.sendto(("SETS").encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
		#socketUDP che verifica che sia supernodo
		data, addr = self.sockUDPClient.recvfrom(4)
		command = data.decode()
		if command == "SET1":
			print("\n"+color.recv+"SUPERNODO settato"+color.end)
			time.sleep(2)
		else:
			print("\n"+color.fail+"SUPERNODO non trovato"+color.end)
			return False
		
		while True:
			printMenu()
			try:
				cmd = input("\nDigita cosa vuoi fare: ")
			except:
				continue
			
			if cmd is "1":
				print(color.recv+"LOGI"+color.end)
			elif cmd is "2":
				print(color.recv+"ADDF"+color.end)
			elif cmd is "3":
				print(color.recv+"DELF"+color.end)
			elif cmd is "4":
				print(color.recv+"FIND"+color.end)
			elif cmd is "5":
				print(color.recv+"RETR"+color.end)
			elif cmd is "6":
				print(color.recv+"LOGO"+color.end)
			elif cmd is "7":
				print(color.recv+"LOGO"+color.end)
				self.sockUDPServer.close()
				self.sockUDPClient.close()
				stopServer()
			
	
if __name__ == "__main__":
    kazaa = kazaaClient()
kazaa.start()



















