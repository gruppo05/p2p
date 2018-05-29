import socket, sqlite3, string, subprocess, threading, os, random, ipaddress, time, datetime, hashlib, sys, stat
import setting as var
from threading import Timer
from random import *

class color:
	HEADER = '\033[95m'
	recv = '\033[36m'
	green = '\033[32m'
	send = '\033[33m'
	fail = '\033[1m'+'\033[31m'
	end = '\033[0m'

def clearAndSetDB(self):
	self.dbReader.execute("DROP TABLE IF EXISTS User")
	self.dbReader.execute("DROP TABLE IF EXISTS File")
	self.dbReader.execute("DROP TABLE IF EXISTS Parts")
	
	self.dbReader.execute("CREATE TABLE User (IPP2P text, PP2P text, SessionID text)")
	self.dbReader.execute("CREATE TABLE File (Filemd5 text, Filename text, SessionID text, Lenfile text, Lenpart text)")
	self.dbReader.execute("CREATE TABLE Parts (IPP2P text, PP2P text, Filemd5 text, IdParts text)")
	
def closeServer(self):
	time.sleep(0.1)
	self.sockUDPServer.close()
	self.sockUDPClient.close()
	os._exit(0)
    
def sessionIdGenerator():
	return "".join(choice(string.ascii_letters + string.digits) for x in range(16))
	
class serverBitTorrent(object):
	def __init__(self):
		IP = ""
		self.PORT = 3000
		self.myIPP2P = var.setting.myIPP2P
		self.timeDebug = var.setting.timeDebug
		self.UDP_END = ""
		
		#accesso mutex
		self.lock = threading.Lock()
		
		# Creo DB
		conn = sqlite3.connect(':memory:', check_same_thread=False)
		self.dbReader = conn.cursor()
		# Creo tabella user
		clearAndSetDB(self)
		# Socket ipv4/ipv6 port 3000
		self.server_address = (IP, int(self.PORT))
		self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind(self.server_address)
		self.sock.listen(5)
		# Socket UDP
		self.UDP_IP = "127.0.0.1"
		self.UDP_PORT_CLIENT = 30002
		UDP_PORT_SERVER = 30001
		# socket upd ipv4 internal Server
		self.sockUDPServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sockUDPServer.bind((self.UDP_IP, UDP_PORT_SERVER))
		# socket upd ipv4 client in uscita
		self.sockUDPClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		
	def serverHandler(self):
		#crea thread interno per far comunicare client e server
		threading.Thread(target = self.serverUDP, args = '').start()
		print(color.green+"In attesa di connessione..."+color.end)
		while True:
			try:
				connection, client_address = self.sock.accept()
				threading.Thread(target = self.server, args = (connection,client_address)).start()
			except:
				return False
	
	def server(self, connection, client_address):
		command = connection.recv(4).decode()
		print("\n")
		try:
			if command == "LOGI":
				try:
					IPP2P = connection.recv(55).decode()
					PP2P = connection.recv(5).decode()
					print("Ricevuto " + color.recv + command + color.end + " da " + color.recv + IPP2P + color.end + " - " + color.recv + PP2P + color.end)
					self.dbReader.execute("SELECT SessionID FROM user WHERE IPP2P=?", (IPP2P,))
					data = self.dbReader.fetchone()
					if data is None:
						SessionID = sessionIdGenerator()
						self.dbReader.execute("INSERT INTO user (IPP2P, PP2P, SessionID) values (?, ?, ?)",(IPP2P, PP2P, SessionID))
						print(color.green + "Nuovo utente aggiunto con sessionID -> "+color.recv+SessionID+color.end)
					else:						
						SessionID = data[0]
						print(color.fail+"Utente già presente con sessionID -> "+color.recv+SessionID+color.end)
				except:
					SessionID = "0000000000000000"
					print("Errore nella procedura di login server")
				finally:
					msg = "ALGI"+SessionID
					connection.sendall(msg.encode())
					connection.close()
			
			elif command == "LOGO":
				SessionID = connection.recv(16).decode()
				partiNonScaricate = 0
				partiScaricate = 0
				print("Ricevuto " + color.recv + command + color.end + " da " + color.recv + SessionID + color.end)
				self.dbReader.execute("SELECT IPP2P FROM User WHERE SessionID=?", (SessionID,))
				ip = self.dbReader.fetchone()[0]
				self.dbReader.execute("SELECT IdParts, Filemd5 FROM Parts WHERE IPP2P=?",(ip,))				
				#self.dbReader.execute("SELECT Filemd5, Lenfile, Lenpart FROM File WHERE SessionID=?",(SessionID,))
				resultFile = self.dbReader.fetchall()
				
				if resultFile is None:
					print(color.green+ "Nessun File presente con SessionID "+ SessionID +color.end)
				else:
					for data in resultFile:
						idParts = data[0]						
						filemd5 = data[1]						
						self.dbReader.execute("SELECT COUNT(IdParts) FROM Parts WHERE Filemd5=? AND IdParts=?",(filemd5,idParts))
						resultCount = int(self.dbReader.fetchone()[0])
						###DELETE PART
						if resultCount > 1:
							self.dbReader.execute("DELETE FROM Parts WHERE Filemd5=? AND IdParts=? AND IPP2P=?",(filemd5, idParts, ip))
							partiScaricate += 1
						else:
							partiNonScaricate += 1
				print("Parti MIE Non scaricate --> "+str(partiNonScaricate))
				print("Parti MIE Scaricate --> "+str(partiScaricate))



				if partiNonScaricate > 0:
					msg = "NLOG"+str(partiNonScaricate).ljust(10)
				else:
					try:
						self.dbReader.execute("DELETE FROM user WHERE SessionID=?", (SessionID,))
						msg = "ALOG" + str(partiScaricate).ljust(10)
					except OSError as e: 
						print(e)						
						print(color.fail+"Errore nell'eliminazione dell'utente e dei suoi file"+color.end)
						msg = "NLOG" + str(partiScaricate).ljust(10)
				print(color.send + "Invio --> " + msg + color.end)
				connection.sendall(msg.encode())
				connection.close()					
							
			elif command == "LOOK":
				sessionID = connection.recv(16).decode()
				ricerca = connection.recv(20).decode()
				print("Ricevuto " + color.recv + command + color.end + " da " + color.recv + sessionID + color.end)
				self.dbReader.execute("SELECT SessionID FROM User WHERE SessionID = ?", (sessionID,))
				resultUser = self.dbReader.fetchone()
				if resultUser is None:
					msg = "ALOO000"
					print("Utente non registrato.")
				else:
					ricerca = ricerca.strip()
					self.dbReader.execute("SELECT COUNT(Filemd5) FROM File WHERE Filename LIKE ? AND SessionID <> ?", ("%"+ricerca+"%", sessionID))
					resultCount = self.dbReader.fetchone()
					#i = 0
					msg="ALOO" + str(resultCount[0]).ljust(3)
					if int(resultCount[0]) > 0:
						self.dbReader.execute("SELECT filemd5, filename, Lenfile, Lenpart FROM File WHERE Filename LIKE ? AND SessionID <> ?", ("%"+ricerca+"%", sessionID))
						resultFile = self.dbReader.fetchall()
						for files in resultFile:
							msg = msg + files[0].ljust(32) + files[1].ljust(100) + str(files[2]).ljust(10) + str(files[3]).ljust(6)
				print(color.send + "Invio --> " + msg + color.end)
				connection.sendall(msg.encode())
				connection.close()
				
				
			elif command == "FCHU":
				sessionID = connection.recv(16).decode()
				filemd5 = connection.recv(32).decode()
				self.dbReader.execute("SELECT * FROM User WHERE SessionID LIKE ?", (sessionID,))
				resultUser = self.dbReader.fetchone()
				if resultUser is None:
					msg = "AFCH000"
					print("Utente non registrato")
					connection.sendall(msg.encode())
				else:
					print("Ricevuto " + color.recv + command + color.end + " da " + color.recv + resultUser[0] + color.end)
					self.dbReader.execute("SELECT DISTINCT IPP2P, PP2P FROM Parts WHERE Filemd5=?", (filemd5,))
					resultParts = self.dbReader.fetchall()
					if resultParts is None:
						msg = "AFCH000"
						print("Parti non presenti. File non in condivisione.")
						connection.sendall(msg.encode())
					else:
						msg = "AFCH" + str(len(resultParts)).ljust(3)
						print(color.send + "Invio --> " + msg + color.end)
						connection.sendall(msg.encode())
						for parts in resultParts:
							self.dbReader.execute("SELECT IdParts FROM Parts WHERE IPP2P LIKE ? AND Filemd5 LIKE ?", (parts[0],filemd5))
							resultID = self.dbReader.fetchall()
							partList = 0
							self.dbReader.execute("SELECT Lenfile, Lenpart FROM File WHERE Filemd5 LIKE ?", (filemd5,))
							data = self.dbReader.fetchone()
							nParts = int(int(data[0])/int(data[1]))
							if (int(data[0])%int(data[1]))!=0:
								nParts=nParts+1
							nByte = int(int(nParts)/8)
							if (nParts%8)!=0:
								nByte = nByte + 1
							for ids in resultID:							
								partList = partList + (2**(nByte*8-1 - int(ids[0])))
							#creo il messaggio
							msg = parts[0] + parts[1]
							connection.sendall(msg.encode())
							try:
								ripperoni = (partList).to_bytes(nByte, byteorder='big')
								connection.sendall(ripperoni)
							except:
								print(color.fail+"Errore sulla partlist"+color.end)
							
				connection.close()
				print(color.green+"Invio completato."+color.end)
				
			elif command == "ADDR":
				try:
					sessionID = connection.recv(16).decode()
					lenFile = int(connection.recv(10).decode())
					lenPart = int(connection.recv(6).decode())
					filename = connection.recv(100).decode()
					filemd5 = connection.recv(32).decode()
					
					self.dbReader.execute("SELECT Filemd5 FROM File WHERE Filemd5=?", (filemd5,))
					result = self.dbReader.fetchone()
					if result is None:
						self.dbReader.execute("INSERT INTO file (Filemd5, Filename, SessionID, Lenfile, Lenpart) VALUES (?, ?, ?, ?, ?)",(filemd5, filename, sessionID, lenFile, lenPart))
						print(color.green+"Inserito nuovo file dal peer -> "+color.green+color.recv+sessionID+color.end)
						numPart = int((lenFile / lenPart) + 1)
						self.dbReader.execute("SELECT IPP2P, PP2P FROM user WHERE SessionID=?", (sessionID,))
						data = self.dbReader.fetchone()
						i = 0
						while i <= numPart-1:
							self.dbReader.execute("INSERT INTO parts (IPP2P, PP2P, Filemd5, IdParts) VALUES (?, ?, ?, ?)",(data[0], data[1], filemd5, str(i)))
							i += 1
						msg = "AADR"+str(numPart).ljust(8)
						print("Invio --> "+color.send+msg+color.end)
						connection.sendall(msg.encode())
						connection.close()
					else:
						print(color.fail+"File già presente"+color.end)
						numPart = int((lenFile / lenPart) + 1)
						msg = "AADR"+str(numPart).ljust(8)
						print("Invio --> "+color.send+msg+color.end)
						connection.sendall(msg.encode())
						connection.close()
				except:
					print(color.fail+"Errore invio "+color.recv+"AADR"+color.end)
					connection.close()
					
					
			elif command == "RPAD":
				try:
					#mutex
					self.lock.acquire(True)
					sessionID = connection.recv(16).decode()
					filemd5 = connection.recv(32).decode()
					idParts = connection.recv(8).decode().strip()
					print("\n\nRicevuto: "+color.recv+command+color.end+" da "+color.recv+ sessionID + color.end)
					
					#cerco ip e port
					self.dbReader.execute("SELECT IPP2P, PP2P FROM user WHERE SessionID=?", (sessionID,))
					data = self.dbReader.fetchone()

					#verifico se ho la parte
					self.dbReader.execute("SELECT * FROM parts WHERE IPP2P=? AND Filemd5=? AND idParts=?", (data[0],filemd5,idParts))					
					result = self.dbReader.fetchone()
					if result is None:
						#aggiungo la parte
						self.dbReader.execute("INSERT INTO parts (IPP2P, PP2P, Filemd5, IdParts) VALUES (?, ?, ?, ?)",(data[0], data[1], filemd5, str(int(idParts))))
						print(color.green+"Aggiunta parte "+idParts+ color.green+" da "+sessionID+color.end)
					else:
						print(color.fail+"Parte "+idParts+ color.fail+" da "+sessionID+color.end+"già presente")
					self.dbReader.execute("SELECT COUNT(IdParts) FROM parts WHERE IPP2P=? AND Filemd5=?", (data[0], filemd5))
					numPart = self.dbReader.fetchone()[0]
					msg = "APAD"+str(numPart).ljust(8)
					print("Invio --> "+color.send+msg+color.end)
					connection.sendall(msg.encode())
					connection.close()
				except:
					print(color.fail+"Errore invio "+color.recv+"APAD"+color.end)
					connection.close()
				finally:
					self.lock.release()
		except:
			connection.close()
			return False
			
	def serverUDP(self):
		print(color.green+"In attesa di comandi interni..."+color.end)
		while True:
			data, addr = self.sockUDPServer.recvfrom(4)
			command = data.decode()
			print("\n\nRicevuto comando dal client: "+color.recv+command+color.end)
			
			if command == "STOP":
				print("Ricevuto STOP!")
				closeServer(self)
			elif command == "STMV":
				print("QUI DEVO MANDARE INDIETRO I VICINI")
			elif command == "STMF":
				self.dbReader.execute("SELECT * FROM Parts ORDER BY Filemd5")
				data = self.dbReader.fetchall()
				for f in data:
					self.sockUDPClient.sendto((f[2]+"-"+str(f[1]).ljust(5)+"-"+str(f[0]).ljust(55)+"-"+str(f[3]).ljust(8)).encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
				self.sockUDPClient.sendto(self.UDP_END.ljust(103).encode(), (self.UDP_IP, self.UDP_PORT_CLIENT))
				
if __name__ == "__main__":
    bitTorrent = serverBitTorrent()
bitTorrent.serverHandler()
