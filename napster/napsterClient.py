#! /usr/bin/python3

import threading
import socket
import hashlib
import os
import sys
import stat
import time
import random
import ipaddress
import signal

Port=3000
fileAggiunti = {}
indiceLista = 0

def signalHandler(signal, frame):
	print('\nTermino il programma')
	os._exit(0)

class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

def printError(string):
	print(bcolors.FAIL + bcolors.BOLD + "ERRORE -> " + string + bcolors.ENDC)

def printConfirm(string):
	print(bcolors.OKGREEN + bcolors.BOLD + "OK -> " + string + bcolors.ENDC)

def printWarning(string):
	print(bcolors.OKGREEN + bcolors.BOLD + "AVVISO -> " + string + bcolors.ENDC)

def trovaPercorso(fileAggiunti,filemd5):
	i=0
	while i<len(fileAggiunti):
		if fileAggiunti[i].FILEMD5==filemd5:
			return fileAggiunti[i].PERCORSO
		else :
			i=i+1
	print ("File md5 non compatibile...")
	exit()	

class salvaFileAggiunti:

	PERCORSO=''
	FILEMD5=''

	def __init__(self,PERCORSO, FILEMD5):
		
		self.PERCORSO=PERCORSO
		self.FILEMD5=FILEMD5
	
def creazioneSocketIPv4(IPP2P,PortaP2P):
	#apertura socket
	peer_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	peer_socket.connect((IPP2P,int(PortaP2P)))
	return peer_socket

def creazioneSocketIPv6(IPP2P,PortaP2P):
	#apertura socket
	peer_socket = socket.socket(socket.AF_INET6,socket.SOCK_STREAM)
	peer_socket.connect((IPP2P,int(PortaP2P)))
	return peer_socket


def encryptMD5(filename):
	#calcolo hash file
    BLOCKSIZE = 128
    hasher = hashlib.md5()
    with open(filename, 'rb') as f:
        buf = f.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(BLOCKSIZE)
        f.close()
    filemd5 = hasher.hexdigest()
    #print(str(msg))
    #res = makeStringLength(str(msg),100)
    return(filemd5)


#CheckIP
def isValidIP(address):
    try:
        ipaddress.ip_address(address)
        return True
    except ValueError:
        return False


def makeStringLength(stringa,lunghezza):
    for i in range(lunghezza - len(stringa)):
        stringa = stringa + "_"
    return stringa

def getNByteFromSocket(sock,nByte):
    return sock.recv(nByte).decode()

def parseString(sock):
    FILEMD5 = 32
    FILENAME = 100
    IPP2P = 55
    PP2P = 5

    response = getNByteFromSocket(sock,4) #AFIN
    #if(response.startswith('AFIN') == False):
    print("AFIN: " + response)
    #    print("FORMATO RISPOSTA NON CORRETTO")
    #    return [],[],[],[]

    idmd5 = getNByteFromSocket(sock,3)
    numeroIDMD5 = int(idmd5)
    #print(numeroIDMD5)
    print("idmd5: " + idmd5)

    listaMd5 = []
    listaFilename = []
    listaNumeroCopie = []
    listaIP = [] #lista di liste
    listaPorte = [] #lista di liste

    response = getNByteFromSocket(sock,FILEMD5) #primo file md5
    print("filemd5: " + response)
    numeroIDMD5 = numeroIDMD5 - 1

    while True:
        listaMd5.append(response)
        response = getNByteFromSocket(sock,FILENAME)
        print("filename: " + response)
        listaFilename.append(response)
        numeroCopie = getNByteFromSocket(sock,3)
        print("numeroCopie: " + numeroCopie)
        listaNumeroCopie.append(numeroCopie)

        ipListTemp = []
        portListTemp = []

        for i in numeroCopie:
            response = getNByteFromSocket(sock,IPP2P) #controllare se è valido
            print("IPP2P: " + response)
            ipListTemp.append(response)
            response = getNByteFromSocket(sock,PP2P)
            print("pp2p:" + response)
            portListTemp.append(response)

        listaIP.append(ipListTemp)
        listaPorte.append(portListTemp)

        if numeroIDMD5 == 0:
            break

        response = getNByteFromSocket(sock,FILEMD5) #primo file md5
        numeroIDMD5 = numeroIDMD5 - 1

        print("filemd5: " + response)

    return listaMd5, listaFilename, listaIP, listaPorte


def sceltaMenu(listaMd5, listaFilename, listaIP, listaPorte):
    print("Corrispondenze:")
    for i in range(len(listaMd5)):
        print("[" + str(i) + "] -" + " Md5: " + listaMd5[i] + " Filename: " + listaFilename[i])
        for j in range(len(listaIP)):
            print("[" + str(i) + "][" + str(j) + "]" + " IP: " + listaIP[i][j] + " Porta: " + listaPorte[i][j])
        print("----------")
    name = int(input("Scelta file: "))
    peer = int(input("Scelta peer: "))

    return listaMd5[name], listaFilename[name], listaIP[name][peer], listaPorte[name][peer]


def login(sock,ipv6,ipv4,serverPort):

	msg = "LOGI" + ipv4 + ipv6 + serverPort
	sock.send(msg.encode())
	#controllo risposta del server
	response = sock.recv(20).decode()
	session_ID=response[4:20]
	if((response.startswith('ALGI') == False)or(session_ID == "0000000000000000")):
		print("LOGIN FALLITO. RIPROVA!")
		return False
	else:
		print("Sessione creata: " + session_ID)
		return session_ID


def aggiuntaFile(sock,sessionID,filename):
    #msg = "ADDF" + str(sessionID) + hashlib.md5(filename) + makeStringLength(filename,100)
	filemd5=encryptMD5(filename)
	msg = "ADDF" + str(sessionID) + filemd5 + makeStringLength(str(filename),100)
	sock.send(msg.encode())
	print("Inviato al server comando di aggiuntaFile")
    #aspetto la risposta AADD[4].numeroCopie[3]
	response = sock.recv(7).decode()
	numeroCopie = response[5:7] #AADD
	if(response.startswith('AADD') == False):
		printError("FILE NON AGGIUNTO CORRETTAMENTE")
	elif(len(response) != 7):
		printError("Lunghezza risposta non corretta: " + str(len(response)))
	else:
		print("response: " + response)
		print("numeroCopie: " + numeroCopie)
		fileAggiunti[indiceLista] = salvaFileAggiunti(filename,filemd5)
		indiceLista = indiceLista + 1

def rimuoviFile(peer_socket, SessionID, file):
	fileMD5=encryptMD5(file)
	packet="DELF"+SessionID+fileMD5
	peer_socket.send(packet.encode())
	response = peer_socket.recv(7).decode()
	numeroCopie = response[5:7]
	#print (response)
	if(response.startswith("ADEL") == False):
		printError("FILE NON RIMOSSO CORRETTAMENTE")
	elif(len(response) != 7):
		printError("Lunghezza risposta non corretta: " + str(len(response)))
	else:
		print("response: " + response)
		print("numeroCopie: " + numeroCopie)

def ricerca(sock,sessionID,stringa):
	msg = "FIND" + str(sessionID) + str(stringa)
	sock.send(msg.encode())
	#cotrollo risposta AFIN[4].idmd5[3].altrielementi
	listaMd5, listaFilename, listaIP, listaPorte = parseString(sock)
	md5,nome,ipPeer,portaPeer = sceltaMenu(listaMd5, listaFilename, listaIP, listaPorte)
	print("Avvio download del file "+nome+" dal peer "+ipPeer+":"+portaPeer)
	#downloadP2P(ipPeer,portaPeer,md5)
	if(peerDownload(ipPeer,portaPeer,md5,nome)):
		print ('Il file è stato salvato con successo!')
		infoServer(sock,sessionID,md5)
	else:
		print("File non scaricato correttamente")

def downloadP2P(IPP2P,PortaP2P,Filemd5):
	p2pSocket = creazioneSocketIPv4(IPP2P,PortaP2P)
	pacchetto = "RETR" + Filemd5
	#invio pacchetto al peer
	p2pSocket.send(pacchetto)
	return 	p2pSocket

#Funzione che apre la socket con il peer da dove scaricare
def peerDownload(IPdownload,PortDownload, md5,filename):
	#filename = input('Inserisci il nome del file.estensione per salvare: ')
	#path = input('In che cartella salvare? ')
	#path = ''
	# Se non è già presente aggiungo alla fine della stringa il separatore (/ o \\ a seconda del OS)
	#if path[-1] != os.sep: path += os.sep
	#fd = os.open(path+filename, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 777)
	fd = os.open(filename, os.O_WRONLY | os.O_CREAT, 777)

	# QUI VA INSERITO IP E PORTA DEL PEER DA CUI VOGLIO SCARICARE IL FILE
	socketP2P = downloadP2P(IPdownload,PortDownload,md5) #

	rispostaPeer = socketP2P.recv(10).decode()
	if not rispostaPeer:
		printError ('ERRORE RICEZIONE PACCHETTO DOWNLOAD DAL PEER')
		return False

	comandoPeer = rispostaPeer[0:4]
	if comandoPeer != "ARET":
		printError ('ERRORE RISPOSTA DOWNLOAD PEER')
		return False

	# Determino il numero di chunk
	nChunk=int(rispostaPeer[4:10])

	# Ricevo il file
	i = 0
	while i < nChunk:
		lenChunk = socketP2P.recv(5).decode()
		while len(lenChunk) < 5:
			lenChunk = lenChunk + socketP2P.recv(1).decode()
		lenChunk = int(lenChunk)
		data = socketP2P.recv(lenChunk)
		while len(data) < lenChunk:
			data = data + socketP2P.recv(1)
		os.write(fd, data)
		i = i + 1


	os.close(fd)
	socketP2P.close()  #chiudo la socket con il peer da cui ho effettuato il download
	return True

def infoServer(sock,sessionID,fileMD5):
	msg = "DREG" + str(sessionID) + str(fileMD5)
	sock.send(msg.encode())
    #controllo risposta
	response = sock.recv(9).decode()
	numdown = response[5:7] #AADD
	if(response.startswith('DREG') == False):
		print("NOTIFICA AL SERVER NON AVVENUTA CORRETTAMENTE")
	if(len(response) != 7):
		printError("Lunghezza risposta non corretta: " + str(len(response)))
	else:
		print("Notifica al server eseguita correttamente")
		sock.close()

def logout(sock,sessionID):
	msg = "LOGO" + str(sessionID)
	sock.send(msg.encode())

	#cotrollo risposta ALGO[4].filedeleted[3]
	response = sock.recv(7).decode()
	numdeleted = response[5:7] #AADD
	if(response.startswith('ALGO') == False):
		print("LOGOUT NON ESEGUITO CORRETTAMENTE")
	if(len(response) != 7):
		printError("Lunghezza risposta non corretta: " + str(len(response)))
	else:
		print("Logout eseguito correttamente")
		sock.close()

class peerServer(threading.Thread):
	host = 'localhost'
	port = 50001
	maxconn = 5
	clients = {}

	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		# Creo la socket passiva in ascolto
		for res in socket.getaddrinfo(self.host, self.port, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
			af, socktype, proto, canonname, sa = res
			try:
				s = socket.socket(af, socktype, proto)
				s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			except socket.error:
				s = None
				continue
			try:
				s.bind(sa)
				s.listen(self.maxconn)
				# Mi collego alla prima disponibile (solitamente IPv6 se disponibile)
				break
			except socket.error:
				s.close()
				s = None
				continue

		if s is None:
			print ('Non sono riuscito ad aprire la socket')
			sys.exit(1)

		print ('Server in ascolto sulla porta', self.port)

		while 1:
			try:
				# Attendo una connessione
				(conn, addr) = s.accept()
				# Costruisco un identificatore per la connessione
				cid = str(addr[0]) + ':' + str(addr[1])
				print('Connesso a ' + cid)
				# Avvio un thread per gestire la connessione
				peerServer.clients[cid]=peerUpload(cid, conn, peerServer)
				peerServer.clients[cid].start()
			except KeyboardInterrupt:
				printError('KeyboardInterrupt received. Closing the server.')
				break
			except:
				break

class peerUpload(threading.Thread):
	id=''
	socket=''
	server=None

	def __init__(self, id, socket, server):
		threading.Thread.__init__(self)
		self.id=id
		self.socket = socket
		self.server = server

	def run(self):
		socketP2P=self.socket

		identificativo = socketP2P.recv(4)
		if not identificativo:
			print ('ERRORE RICEZIONE PACCHETTO RETR')
			sys.exit(1)


		if identificativo !="RETR":
			print ('ERRORE RICEZIONE IDENTIFICATIVO RETR')

		filemd5 = socketP2P.recv(16)
		filename = trovaPercorso(fileAggiunti,filemd5)

		#filename = '/Users/abertagnon/Downloads/immagine.jpg'
		fd = os.open(filename, os.O_RDONLY)
		filesize = os.fstat(fd)[stat.ST_SIZE]

		# Calcolo i chunk
		nChunk = filesize/4096
		# Verifico se il file si divide esattamente nei chunk
		if (filesize % 4096) !=0:
			nChunk = nChunk + 1

		nChunk = int(float(nChunk))
		pacchetto = "ARET" + str(nChunk).zfill(6)
		socketP2P.send(pacchetto.encode())

		print ('Trasferimento in corso di ', filename, '[BYTES ', filesize, ']')

		i = 0
		while i < nChunk:
			buf = os.read(fd,4096)
			if not buf: break
			lBuf = len(buf)
			lBuf = str(lBuf).zfill(5)
			socketP2P.send(lBuf.encode())
			socketP2P.send(buf)
			i = i + 1

		os.close(fd)
		printConfirm ('Trasferimento completato...')
		#time.sleep(10)
		self.close(False)

	def close(self, nodestroy):
		print ('Disconnessione da ' + self.id)
		self.socket.close()
		# Elimino il client dalla lista di client connessi in peerServer
		if not nodestroy:
			del self.server.clients[self.id]

if __name__ == "__main__":
	loggato = False

	signal.signal(signal.SIGINT, signalHandler)
	# Avvio processo server in ascolto per scambio file p2p
	s = peerServer()
	s.start()
	
	ipv4 = "172.16.6.y"
	ipv6 = "FC00::6:y"
	
	while 1:
		# Aspetto un secondo prima di stampare a video il menù di scelta
		time.sleep(1)
		print(bcolors.WARNING + bcolors.BOLD 	+ "      ____           ____ _ _            _	" + bcolors.ENDC)
		print(bcolors.FAIL +  bcolors.BOLD 		+ " _ __|___ \ _ __    / ___| (_) ___ _ __ | |_ " + bcolors.ENDC)
		print(bcolors.OKBLUE + bcolors.BOLD 	+ "| '_ \ __) | '_ \  | |   | | |/ _ \ '_ \| __|" + bcolors.ENDC)
		print(bcolors.OKGREEN + bcolors.BOLD 	+ "| |_) / __/| |_) | | |___| | |  __/ | | | |_ " + bcolors.ENDC)
		print(bcolors.WARNING + bcolors.BOLD 	+ "| .__/_____| .__/   \____|_|_|\___|_| |_|\__|" + bcolors.ENDC)
		print(bcolors.FAIL + bcolors.BOLD 		+ "|_|        |_|   							\n" + bcolors.ENDC)
		print("< 1 >  LOGIN")
		print("< 2 >  AGGIUNTA FILE")
		print("< 3 >  RIMOZIONE FILE")
		print("< 4 >  RICERCA")
		print("< 5 >  LOGOUT")
		print("< 6 >  DOWNLOAD")
		code=input("\nInserire uno dei precedenti codici per svolgere un'azione: ")

		if(code=="1"):
			rnd = random.random()
			if(rnd<0.5):
				while 1:
					IPP2P=input("Inserire l'indirizzo IPv4 della directory: ")
					if(isValidIP(IPP2P)):
						peer_socket=creazioneSocketIPv4(IPP2P,Port)
						break
			else:
				while 1:
					IPP2P=input("Inserire l'indirizzo IPv6 della directory: ")
					if(isValidIP(IPP2P)):
						peer_socket=creazioneSocketIPv6(IPP2P,Port)
						break
			print("Procedura per il login")
			sessionID=login(peer_socket,ipv4,ipv6,peerServer.port)
			if(sessionID==False):
				loggato=False
			else:
				loggato=True

		elif(code=="2" and loggato):
			print("Procedura per l'aggiunta di un file")
			filename=input("Inserire il nome del file che si intende aggiungere: ")
			aggiuntaFile(peer_socket,sessionID,filename)

		elif(code=="3" and loggato):
			print("Procedura per la rimozione di un file")
			filename=input("Inserire il nome del file che si intende rimuovere: ")
			rimuoviFile(peer_socket,sessionID,filename)

		elif(code=="4" and loggato):
			print("Procedura per la ricerca di un file")
			filename=input("Inserire il nome del file che si intende cercare: ")
			ricerca(peer_socket,sessionID,filename)	#vedere questa funzione per organizzare la selezione

		elif(code=="5" and loggato):
			print("Procedura per il logout")
			logout(peer_socket,sessionID)
			break

		#elif(code=="6" and loggato):
		#	print("Procedura di download di un file")
		#	IPdownload=input("Inserire l'IP del peer da dove fare il download: ")
		#	#checkIP?
		#	success=peerDownload(IPdownload,PortDownload)
		#	PortDownload=input("Inserire la porta del peer da dove fare il download: ")
		#	if(success):
		#		infoServer(peer_socket,sessionID,fileMD5)
		#	else:
		#		printError("Download non eseguito correttamente")
		else:
			printError("Prima di procedere devi effttuare il LOGIN\n\n")
