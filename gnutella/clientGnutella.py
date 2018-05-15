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

def stopServer():
	os.system("kill $(ps aux | grep '.py' | awk '{print $2}')") #questo killa anche gedit se il file si chiama .py
	os._exit(0)

def printMenu():
	os.system('cls' if os.name == 'nt' else 'clear')
	print(color.recv+"  ____  "+ color.green+"        "+ color.send+"        "+ color.fail+" _    "+ color.recv+"       "+ color.green+" _  "+ color.send+" _  "+ color.green+"        "+ color.fail+"  ____  _____   ____  "+ color.end)
	print(color.recv+" / ___| "+ color.green+" _ __   "+ color.send+" _   _  "+ color.fail+"| |_  "+ color.recv+"  ___  "+ color.green+"| | "+ color.send+"| | "+ color.green+"  __ _  "+ color.fail+" |  _ \ \__  \ |  _ \ "+ color.end)
	print(color.recv+"| |  _  "+ color.green+"| '_ \  "+ color.send+"| | | | "+ color.fail+"| __/ "+ color.recv+" / _ \ "+ color.green+"| | "+ color.send+"| | "+ color.green+" / _` | "+ color.fail+" | |_) | __) | | |_) |"+ color.end)
	print(color.recv+"| |_| | "+ color.green+"| | | | "+ color.send+"| |_| | "+ color.fail+"| |_  "+ color.recv+"|  __/ "+ color.green+"| | "+ color.send+"| | "+ color.green+"| (_| | "+ color.fail+" |  __/ / __/  |  __/ "+ color.end)
	print(color.recv+" \____| "+ color.green+"|_| |_| "+ color.send+" \__,_| "+ color.fail+" \__\ "+ color.recv+" \___| "+ color.green+"|_| "+ color.send+"|_| "+ color.green+" \__,_| "+ color.fail+" |_|   |_____| |_|    "+ color.end)
	print("\n")
	print("« 1 » RICERCA VICINI")
	print("« 2 » AGGIUNGI FILE")
	print("« 3 » RICERCA FILE")
	print("« 4 » SCARICA FILE")
	print("« 5 » STAMPA TUTTI I VICINI")
	print("« 6 » STAMPA TUTTI I FILE TROVATI")
	print(color.fail+"« 7 » CHIUDI IL CLIENT"+color.end)


class GnutellaClient(object):
	def __init__(self):
		self.UDP_IP = "127.0.0.1"
		self.UDP_PORT_SERVER = 49999
		UDP_PORT_CLIENT = 50000
		self.endUDP1 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx";
		self.endUDP2 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx";
		self.endUDP3 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

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
				cmd = input("\nDigita cosa vuoi fare:\n")
			except:
				continue
			if cmd is "1":
				print("RICERCA VICINI")
				self.sockUDPServer.sendto(("NEAR").encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
				
			elif cmd is "2":
				print("AGGIUNTA FILE")
				self.sockUDPServer.sendto(("ADDF").encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
				filename = input("Inserisci il nome del file da aggiungere: ")
				self.sockUDPServer.sendto((filename.ljust(20)).encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
				#esito operazione
				command, useless = self.sockUDPClient.recvfrom(1)
				com = command.decode()
				if com is "1":
					print(color.green+"File aggiunto con successo"+color.end)
				else:
					print(color.fail+"Impossibile aggiungere il file"+color.end)
				
			elif cmd is "3":
				print("RICERCA FILE")
				self.sockUDPServer.sendto(("QUER").encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
				ricerca = input("Inserire il nome presente nel file da cercare: ")
				self.sockUDPServer.sendto((ricerca.ljust(20)).encode(),(self.UDP_IP, self.UDP_PORT_SERVER))
			
			elif cmd is "4":
				print("DOWNLOAD")
				ricerca = input("Quale file vuoi scaricare?")
				msg = "FDWN"
				self.sockUDPServer.sendto(msg.encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
				msg = ricerca.ljust(20)
				self.sockUDPServer.sendto(msg.encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
				count = 1;
				print(color.recv+"RISULTATI TROVATI:"+color.end)	
				while True:
					buff, addr = self.sockUDPClient.recvfrom(195)
					cmd = buff.decode()
					if cmd == self.endUDP3:
						print(color.recv+"0 - Annulla\n______________________________\n"+color.end)
						cmd = input("Quale risultato vuoi scaricare? ")
						if cmd == "0":
							break
						elif int(cmd) < count:
							msg = "RETR"
							self.sockUDPServer.sendto((msg).encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
							msg = ricerca.ljust(20)
							self.sockUDPServer.sendto((msg).encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
							msg = cmd.ljust(3)
							self.sockUDPServer.sendto((msg).encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
							cmd, addr = self.sockUDPClient.recvfrom(4)
							cmd = cmd.decode()
							
							if cmd == "ARE1":
								print(color.green+"File scaricato!"+color.end)
								break
							else:
								print(color.fail+"Errore download file!"+color.end)
							break
						elif int(cmd) > count:
							print("Errore nella scelta")
							break
					else:
						print(color.recv+str(count)+" - "+cmd+color.end)
						count = count+1
			elif cmd is "5":
				print("STAMPA VICINI TROVATI")
				self.sockUDPServer.sendto(("STMV").encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
				while True:
					buff, addr = self.sockUDPClient.recvfrom(61)
					cmd = buff.decode()
					if cmd == self.endUDP1:
						print(color.recv+"Lista vicini terminata"+color.end)
						cmd = input("Premi invio per continuare:")
						break;
					else:
						print(color.recv+cmd+color.end)

			elif cmd is "6":
				print("STAMPA FILE TROVATI")
				self.sockUDPServer.sendto(("STMF").encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
				while True:
					buff, addr = self.sockUDPClient.recvfrom(159)
					cmd = buff.decode()
					if cmd == self.endUDP2:
						print(color.recv+"Lista file terminata"+color.end)
						cmd = input("Premi invio per continuare:")
						break;
					else:
						print(color.recv+cmd+color.end)
				
			elif cmd is "7":
				stopServer()
			
			time.sleep(1)
			
if __name__ == "__main__":
    gnutella = GnutellaClient()
gnutella.start()






