import socket, sqlite3, string, subprocess, os, time
import setting as var
from random import *

class color:
	recv = '\033[36m'
	green = '\033[32m'
	send = '\033[33m'
	fail = '\033[1m'+'\033[31m'
	end = '\033[0m'

def startUDPhandler():
	os.system("gnome-terminal -e 'sh -c \"python3 serverUDPhandler.py\"'")

def stopServer(self):
	time.sleep(0.1)
	self.sockUDPServer.sendto(("STOP").encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
	self.sockUDPServer.close()
	self.sockUDPClient.close()
	os._exit(0)

def printMenu():
	os.system('cls' if os.name == 'nt' else 'clear')
	print(color.recv+" ______              "+"    "+color.green+" _______                                                  "+color.end)
	print(color.recv+"|  ___ \             "+"    "+color.green+"|__   __|                                                 "+color.end)
	print(color.recv+"| |   | | _  _______ "+"    "+color.green+"   | |    ______  _____   _____   ______  __   _  _______ "+color.end)
	print(color.recv+"| |__/ / | ||__   __|"+"    "+color.green+"   | |   |  __  || __  \ | __  \ |  ____||  \ | ||__   __|"+color.end)
	print(color.recv+"|  __ (  | |   | |   "+"    "+color.green+"   | |   | |  | ||    _/ |    _/ | |__   | \ \| |   | |   "+color.end)
	print(color.recv+"| |  \ \ | |   | |   "+"    "+color.green+"   | |   | |  | || |\ \  | |\ \  |  __|  | |\ | |   | |   "+color.end)
	print(color.recv+"| |___| || |   | |   "+"    "+color.green+"   | |   | |__| || | \ \ | | \ \ | |____ | | \  |   | |   "+color.end)
	print(color.recv+"|______/ |_|   |_|   "+"    "+color.green+"   |_|   |______||_|  \_\|_|  \_\|______||_|  \_|   |_|   "+color.end)
	print("\n")
	print("« 1 » AGGIUNGI FILE IN CONDIVISIONE")
	print("« 2 » RICERCA FILE")
	print("« 3 » SCARICA FILE")
	print("« 4 » STAMPA PARTI RICHIESTE AL SERVER")
	print(color.fail+"« 0 » LOGOUT E CHIUDI"+color.end)
	
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

class clientBitTorrent(object):
	def __init__(self):
		self.UDP_IP = "127.0.0.1"
		self.UDP_PORT_SERVER = 49999
		UDP_PORT_CLIENT = 50000
		self.UDP_END = ""
		# Socket UPD ipv4 client in attesa
		self.sockUDPClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sockUDPClient.bind((self.UDP_IP, UDP_PORT_CLIENT))
		
		# Socket UDP ipv4 server in uscita
		self.sockUDPServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		
	def startClient(self):
		startUDPhandler()
		os.system('cls' if os.name == 'nt' else 'clear')
		#printMenu()
		
		#ricerca super nodi
		time.sleep(0.1)
		
		print(color.green+"Inserisci nodo conosciuto"+color.end)
		self.sockUDPServer.sendto(("SETV").encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
		gruppo = setIp(int(input("Inserisci gruppo:	")))
		numPc = setIp(int(input("Inserisci numero pc:	")))
		port = setPort(int(input("Inserisci porta:	")))
		self.sockUDPServer.sendto((gruppo).encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
		self.sockUDPServer.sendto((numPc).encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
		self.sockUDPServer.sendto((str(port)).encode(), (self.UDP_IP, self.UDP_PORT_SERVER))

		print(color.recv+"LOGIN in corso..."+color.end)
		self.sockUDPServer.sendto(("LOGI").encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
		result, addr = self.sockUDPClient.recvfrom(4)
		result = result.decode()
		if result == "LOG1":
			print(color.recv+"LOGIN effettuato con successo"+color.end)
			time.sleep(2)
		else:
			print("\n"+color.fail+"LOGIN fallito!"+color.end)
			stopServer(self)
			
		while True:
			printMenu()
			try:
				cmd = input("\nDigita cosa vuoi fare: ")
			except:
				continue
			
			if cmd is "1":
				print(color.recv+"AGGIUNGI FILE"+color.end)
				filename = input("Inserisci nome del file da condividere: ")
				try:
					path = var.setting.userPath+""+filename
					f = open(path, 'rb')
					
					self.sockUDPServer.sendto(("ADDR").encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
					filename = filename.ljust(100)
					self.sockUDPServer.sendto((filename).encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
				
					command = self.sockUDPClient.recvfrom(1)[0].decode()
					if command is "1":
						print(color.green+"File aggiunto con successo"+color.end)
					else:
						print(color.fail+"Impossibile aggiungere il file"+color.end)
					time.sleep(1)
				except:
					print(color.fail+"Il file non è presente nella directory di condivisione"+color.end)
					input("Premi invio per continuare")
				
				
			elif cmd is "2":
				print(color.recv+"RICERCA FILE"+color.end)
				self.sockUDPServer.sendto(("FIND").encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
				ricerca = input("Inserisci il nome del file da cercare: ")
				ricerca = ricerca.ljust(20)
				self.sockUDPServer.sendto(ricerca.encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
				cmd, useless = self.sockUDPClient.recvfrom(3)
				cmd = cmd.decode()
				if int(cmd) > 1:
					print("Ricerca completata. Trovati " + str(cmd) + " file.")
				else:
					print("Ricerca completata. Non ci sono file corrispondenti.")
				
				#da aggiungere tutta la fase di download 
			
			elif cmd is "3":
				print("DOWNLOAD")
				ricerca = input("Inserisci numero del file da scaricare: ")
				msg = "FDWN"
				self.sockUDPServer.sendto(msg.encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
				msg = ricerca.ljust(20)
				self.sockUDPServer.sendto(msg.encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
				count = 1;
				print(color.recv+"RISULTATI TROVATI:"+color.end)	
				while True:
					buff, addr = self.sockUDPClient.recvfrom(133)
					cmd = buff.decode()
					if cmd == self.UDP_END.ljust(133):
						print(color.recv+"0 - Annulla\n______________________________\n"+color.end)
						cmd = input("Quale risultato vuoi scaricare? ")
						if cmd == "0":
							break
						elif int(cmd) < count:
							msg = "RETP"
							self.sockUDPServer.sendto((msg).encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
							msg = ricerca.ljust(3)
							self.sockUDPServer.sendto((msg).encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
							msg = cmd.ljust(3)
							self.sockUDPServer.sendto((msg).encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
							print("Download in corso..")
							time.sleep(1)
							break
						elif int(cmd) > count:
							print("Errore nella scelta")
							break
					else:
						print(color.recv+str(count)+" - "+cmd+color.end)
						count = count+1
			elif cmd is "4":
				print(color.recv+"STMC"+color.end)
				self.sockUDPServer.sendto(("STMC").encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
			
			elif cmd is "0":
				print(color.recv + "LOGOUT" + color.end)
				self.sockUDPServer.sendto(("LOGO").encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
				answer = self.sockUDPClient.recvfrom(4)[0].decode()
				parti = self.sockUDPClient.recvfrom(10)[0].decode()
				print("Ricevuto <-- "+color.send+str(answer)+str(parti)+color.end)
				if answer == "NLOG":
					print(color.fail + "IMPOSSIBILE EFFETTUARE IL LOGOUT" + color.end)
					print(color.fail + "Parti ancora in condivisione: " + color.recv + str(parti) + color.end)
				if answer == "ALOG":
					#print(color.green + "LOGOUT" + color.end)
					print(color.green + "Tutte le parti sono già in condivisione da altri."+color.end)
					print(color.recv+"CHIUSURA CLIENT"+color.end)
					stopServer(self)

			
if __name__ == "__main__":
    client = clientBitTorrent()
client.startClient()


