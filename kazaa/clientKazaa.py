import socket, sqlite3, string, subprocess, os, time, sys
from random import *
import setting as var

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

def stopServer(self):
	##os.system("kill $(ps aux | grep '.py' | awk '{print $2}')") #questo killa anche gedit se il file si chiama .py
	time.sleep(0.1)
	self.sockUDPServer.sendto(("STOP").encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
	self.sockUDPServer.close()
	self.sockUDPClient.close()
	os._exit(0)

def printMenu(self):
	os.system('cls' if os.name == 'nt' else 'clear')
	print(color.recv+" _  __ "+ color.green+"        "+ color.send+"       "+ color.fail+"        "+ color.recv+"        "+ color.fail+"  ____  _____   ____  "+ color.end)
	print(color.recv+"| |/ / "+ color.green+"  __ _  "+ color.send+" ____  "+ color.fail+"  __ _  "+ color.recv+"  __ _  "+ color.fail+" |  _ \ \__  \ |  _ \ "+ color.end)
	print(color.recv+"| ' /  "+ color.green+" / _` | "+ color.send+"|_  /  "+ color.fail+" / _` | "+ color.recv+" / _` | "+ color.fail+" | |_) | __) | | |_) |"+ color.end)
	print(color.recv+"| | \  "+ color.green+"| (_| | "+ color.send+" / /_  "+ color.fail+"| (_| | "+ color.recv+"| (_| | "+ color.fail+" |  __/ / __/  |  __/ "+ color.end)
	print(color.recv+"|_|\_\ "+ color.green+" \__,_/ "+ color.send+"/____\ "+ color.fail+" \__,_| "+ color.recv+" \__,_| "+ color.fail+" |_|   |_____| |_|    "+ color.end)
	print("\n")
	print("« 1 » AGGIUNTA FILE")
	print("« 2 » RIMOZIONE FILE")
	print("« 3 » RICERCA FILE")
	print("« 4 » DOWNLOAD FILE")
	print("« 5 » LOGOUT")
	print("« 6 » STAMPA FILE IN CONDIVISIONE")
	print("« 7 » STAMPA PEER VICINI")
	if self.super == "1":
		print("« 8 » RICERCA SUPERNODI")
	print(color.fail+"« 0 » CHIUDI IL CLIENT"+color.end)

def progBar(i):
	i = i+1
	bar_length = 60
	hashes = '#' * i * 3
	spaces = ' ' * (bar_length - len(hashes))
	sys.stdout.write("\r[{0}] {1}s".format(hashes + spaces, int(i)))
	
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
	
	
class kazaaClient(object):
	def __init__(self):
		self.UDP_IP = "127.0.0.1"
		self.UDP_PORT_SERVER = 49999
		UDP_PORT_CLIENT = 50000
		self.endUDP1 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
		self.endUDP2 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
		self.endUDP3 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
		self.super = 0
		
		# Socket UPD ipv4 client in attesa
		self.sockUDPClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sockUDPClient.bind((self.UDP_IP, UDP_PORT_CLIENT))
		
		# Socket UDP ipv4 server in uscita
		self.sockUDPServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.timeDebug = var.Settings.timeDebug
		
	def start(self):
		startServer()
		os.system('cls' if os.name == 'nt' else 'clear')
		
		
		#ricerca super nodi
		time.sleep(0.1)
		
		while True:
			cmd = input(color.green+"Sei super?"+color.end+"\n1 - SI\n0 - NO\nScelta:	");
			if cmd == "0" or cmd == "1":
				self.sockUDPServer.sendto(("IFSU").encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
				self.sockUDPServer.sendto(cmd.encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
				self.super = cmd
				break;
			else:
				print(color.fail+"Scelta non valida"+color.end)
		
		print(color.green+"Inserisci nodo conosciuto"+color.end)
		self.sockUDPServer.sendto(("SETV").encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
		gruppo = setIp(int(input("Inserisci gruppo:	")))
		numPc = setIp(int(input("Inserisci numero pc:	")))
		port = setPort(int(input("Inserisci porta:	")))
		self.sockUDPServer.sendto((gruppo).encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
		self.sockUDPServer.sendto((numPc).encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
		self.sockUDPServer.sendto((str(port)).encode(), (self.UDP_IP, self.UDP_PORT_SERVER))

		
		
		print("RICERCA SUPERNODI"+color.green)
		self.sockUDPServer.sendto(("SUPE").encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
		i = 0
		while i < 20:
			progBar(i)
			time.sleep(self.timeDebug)
			i = i+1

		self.sockUDPServer.sendto(("SETS").encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
		#socketUDP che verifica che sia supernodo
		data, addr = self.sockUDPClient.recvfrom(4)
		command = data.decode()
		if command == "SET1":
			print("\n"+color.recv+"SUPERNODO settato"+color.end)
		else:
			print("\n"+color.fail+"SUPERNODO non trovato"+color.end)
			return False
		
		print(color.recv+"Effettuo LOGIN"+color.end)
		self.sockUDPServer.sendto(("LOGI").encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
		result, addr = self.sockUDPClient.recvfrom(4)
		result = result.decode()
		if result == "LOG1":
			print("\n"+color.recv+"LOGIN effettuato con successo"+color.end)
			time.sleep(2)
		else:
			print("\n"+color.fail+"LOGIN fallito!"+color.end)
			stopServer(self)
		
		while True:
			printMenu(self)
			try:
				cmd = input("\nDigita cosa vuoi fare: ")
			except:
				continue						
			if cmd is "1":
				print(color.recv+"AGGIUNTA FILE"+color.end)
				self.sockUDPServer.sendto(("ADDF").encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
				filename = input("Inserisci il nome del file da aggiungere: ")
				self.sockUDPServer.sendto((filename.ljust(100)).encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
				
				command, useless = self.sockUDPClient.recvfrom(1)
				com = command.decode()
				if com is "1":
					print(color.green+"File aggiunto con successo"+color.end)
				else:
					print(color.fail+"Impossibile aggiungere il file"+color.end)
				time.sleep(1)
				
			elif cmd is "2":
				print(color.recv+"DELF"+color.end)
				self.sockUDPServer.sendto(("DELF").encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
				filename = input("Inserisci il nome del file da cancellare: ")
				self.sockUDPServer.sendto((filename.ljust(100)).encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
				
				command, useless = self.sockUDPClient.recvfrom(1)
				com = command.decode()
				if com is "1":
					print(color.green+"File rimosso con successo"+color.end)
				else:
					print(color.fail+"Impossibile rimuovere il file"+color.end)
				time.sleep(1)
				
			elif cmd is "3":
				print(color.recv+"FIND"+color.end)
				self.sockUDPServer.sendto(("FIND").encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
				ricerca = input("Inserisci il nome del file da cercare: ")
				ricerca = ricerca.ljust(20)
				print(ricerca)
				self.sockUDPServer.sendto(ricerca.encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
				print("Ricerca File: ")
				i = 0
				print(color.green)
				while i < 25:
					progBar(i)
					time.sleep(self.timeDebug)
					i = i+1
				print(color.end)
				
				#leggere da server
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
							else:
								print(color.fail+"Errore download file!"+color.end)
							break
						else:
							print("Scelta non valida")
							break
					else:
						print(color.recv+str(count)+" - "+cmd+color.end)
						count = count+1
					
			
			elif cmd is "4":
				print(color.recv+"DOWNLOAD"+color.end)
				
				ricerca = input("Inserisci il nome del file da scaricare: ")
				ricerca = ricerca.ljust(20)
				
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
							else:
								print(color.fail+"Errore download file!"+color.end)
							break
						else:
							print("Scelta non valida")
							break
					else:
						print(color.recv+str(count)+" - "+cmd+color.end)
						count = count+1
						

			elif cmd is "5":
				print(color.recv+"LOGOUT"+color.end)
				self.sockUDPServer.sendto(("LOGO").encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
				command, useless = self.sockUDPClient.recvfrom(3)
				nCopy = command.decode()
				print("Cancellato "+color.recv+nCopy+color.end)
				stopServer(self)
				
			elif cmd is "6":
				print(color.recv+"STAMPA FILE IN CONDIVISIONE"+color.end)
				self.sockUDPServer.sendto(("STMF").encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
				while True:
					buff, addr = self.sockUDPClient.recvfrom(159)
					cmd = buff.decode()
					if cmd == self.endUDP1:
						print(color.recv+"Lista file terminata"+color.end)
						cmd = input("Premi invio per continuare:")
						break;
					else:
						print(color.recv+cmd+color.end)
			
			elif cmd is "7":
				print(color.recv+"STAMPA PEER IN CONDIVISIONE"+color.end)
				self.sockUDPServer.sendto(("STMP").encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
				while True:
					buff, addr = self.sockUDPClient.recvfrom(80)
					cmd = buff.decode()
					if cmd == self.endUDP2:
						print(color.recv+"Lista peer terminata"+color.end)
						cmd = input("Premi invio per continuare:")
						break;
					else:
						print(color.recv+cmd+color.end)
						
			elif cmd is "8" and self.super == "1":
				print("RICERCA SUPERNODI"+color.green)
				self.sockUDPServer.sendto(("SUPE").encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
				i = 0
				while i < 20:
					progBar(i)
					time.sleep(self.timeDebug)
					i = i+1
			
			elif cmd is "0":
				print(color.recv+"LOGOUT"+color.end)
				self.sockUDPServer.sendto(("LOGO").encode(), (self.UDP_IP, self.UDP_PORT_SERVER))
				stopServer(self)
				
if __name__ == "__main__":
    kazaa = kazaaClient()
kazaa.start()



















