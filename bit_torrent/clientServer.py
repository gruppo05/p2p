import socket, sqlite3, string, subprocess, os, time 
from random import *

class color:
	recv = '\033[36m'
	green = '\033[32m'
	send = '\033[33m'
	fail = '\033[31m'
	end = '\033[0m'
	BOLD = '\033[1m'

def startServerBitTorrent():
	os.system("gnome-terminal -e 'sh -c \"python3 serverBitTorrent.py\"'")
	
def stopServer(self):
	time.sleep(0.1)
	self.sockUDPServer.sendto(("STOP").encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
	self.sockUDPServer.close()
	self.sockUDPClient.close()
	os._exit(0)

def printMenu():
	os.system('cls' if os.name == 'nt' else 'clear')
	print(color.recv+" ______              "+"    "+color.BOLD+color.fail+" _______                                                   "+ color.end)
	print(color.recv+"|  ___ \  _  _______ "+"    "+color.BOLD+color.fail+"|__   __| ______  _____   _____   ______  __    _  _______ "+ color.end)
	print(color.recv+"| |   | || ||__   __|"+"    "+color.BOLD+color.fail+"   | |   |  __  ||  __ \ |  __ \ |  ____||  \  | ||__   __|"+ color.end)
	print(color.recv+"| |__/ / | |   | |   "+"    "+color.BOLD+color.fail+"   | |   | |  | || |__| || |__| || |__   |   \ | |   | |   "+ color.end)
	print(color.recv+"|  __ (  | |   | |   "+"    "+color.BOLD+color.fail+"   | |   | |  | ||    _/ |    _/ |  __|  | |\ \| |   | |   "+ color.end)
	print(color.recv+"| |  \ \ | |   | |   "+"    "+color.BOLD+color.fail+"   | |   | |  | || |\ \  | |\ \  | |     | | \ | |   | |   "+ color.end)
	print(color.recv+"| |___| || |   | |   "+"    "+color.BOLD+color.fail+"   | |   | |__| || | \ \ | | \ \ | |____ | |  \  |   | |   "+ color.end)
	print(color.recv+"|______/ |_|   |_|   "+"    "+color.BOLD+color.fail+"   |_|   |______||_|  \_\|_|  \_\|______||_|   \_|   |_|   "+ color.end)
	print("\n")
	print(color.fail+"« 0 » CHIUDI IL SERVER"+color.end)
	
def setIp(n):
	if n < 10:
		n = "00"+str(n)
	elif n < 100:
		n = "0"+str(n)
	return n

def setPort(n):
	if n < 10000:
		n = "0"+str(n)
	return n
	
		

class clientServer(object):
	def __init__(self):
		self.UDP_IP = "127.0.0.1"
		self.UDP_PORT_SERVER = 30001
		UDP_PORT_CLIENT = 30002
		
		# Socket UPD ipv4 client in attesa
		self.sockUDPClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sockUDPClient.bind((self.UDP_IP, UDP_PORT_CLIENT))
		
		# Socket UDP ipv4 server in uscita
		self.sockUDPServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		
	def startClient(self):
		startServerBitTorrent()
		os.system('cls' if os.name == 'nt' else 'clear')
		
		while True:
			printMenu();
			try:
				cmd = input("\nDigita cosa vuoi fare: ")
			except:
				continue
			
			if cmd is "0":
				print(color.recv+"CHIUSURA SERVER"+color.end)
				#self.sockUDPServer.sendto(("LOGO").encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
				stopServer(self)
		
			
if __name__ == "__main__":
    client = clientServer()
client.startClient()






