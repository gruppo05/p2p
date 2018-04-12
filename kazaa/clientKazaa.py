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
	print("« 1 » RICERCA VICINI")
	print(color.fail+"« 2 » CHIUDI IL CLIENT"+color.end)
	
class GnutellaClient(object):
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
		while True:
			printMenu()
			try:
				cmd = input("\nDigita cosa vuoi fare: ")
			except:
				continue
			
			if cmd is "1":
				print("RICERCA VICINI")
				self.sockUDPServer.sendto(("NEAR").encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
				
			if cmd is "2":
				self.sockUDPServer.close()
				self.sockUDPClient.close()
				stopServer()
			
	
if __name__ == "__main__":
    gnutella = GnutellaClient()
gnutella.start()



















