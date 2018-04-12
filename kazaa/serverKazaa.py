import socket, sqlite3, string, subprocess, threading, os, random, ipaddress, time, datetime, hashlib, sys, stat
import settings as var
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
	
class Kazaa(object):
	def __init__(self):
		IP = ""
		self.PORT = var.Settings.PORT
		self.myIPP2P = var.Settings.myIPP2P
		self.UDP_IP = "127.0.0.1"
		UDP_PORT_SERVER = 49999
		self.UDP_PORT_CLIENT = 50000
		self.endUDP1 = "";
		self.endUDP2 = "";
		self.BUFF = 99999
		
		# Socket ipv4/ipv6 port 3000
		self.server_address = (IP, self.PORT)
		self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind(self.server_address)
		self.sock.listen(5)
		
		# socket upd ipv4 internal Server
		self.sockUDPServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sockUDPServer.bind((self.UDP_IP, UDP_PORT_SERVER))
		
		# socket upd ipv4 client in uscita
		self.sockUDPClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		
	def server(self):
		#crea thread interno per far comunicare client e server
		threading.Thread(target = self.serverUDP, args = '').start()
		
		print(color.green+"In attesa di connessione esterna..."+color.end)
		while True:
			try:
				connection, client_address = self.sock.accept()
				threading.Thread(target = self.serverTCP, args = (connection,client_address)).start()
			except:
				return False
	
	
	def serverUDP(self):
		print(color.green+"In attesa di comandi interni..."+color.end)
		while True:
			data, addr = self.sockUDPServer.recvfrom(4)
			command = data.decode()
			print("\n\nRicevuto comando dal client: "+color.recv+command+color.end)
			if command == "NEAR":
				print("near")
	
	
	def serverTCP(self, connection, client_address):
		command = connection.recv(4).decode()
	
	
		
if __name__ == "__main__":
    gnutella = Kazaa()
gnutella.server()

















