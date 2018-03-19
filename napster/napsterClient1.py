#! /usr/bin/python3
# -*- coding: utf-8 -*-

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

#from functools import partial


# Porta di connessione alla directory
ipv4 = '172.016.006.003'
ipv6 = 'fc00::6:3'
port = 3000


#indiceLista = 0
fileAggiunti = []


# gestisco il ctrl c
def signalHandler(signal, frame):
    printWarning('Termino il programma')
    #socketDir.close()
    os._exit(0)


# rimuove gli zeri di padding
def removeZeroIpAddress(address):
    temp = address.split('.')
    validIp = ""
    for i in range(0, len(temp)):
        validIp = validIp + str(int(temp[i])) + "."
    return validIp


# espando indirizzo ipv6
# da fe80::51db:325d:8e6a:c993
# a fe80:0000:0000:0000:51db:325d:8e6a:c993
def expandIpv6Address(address):
    return ipaddress.ip_address(address).exploded


# calcolo ipv4 della macchina locale
'''def getIpv4AddressLocalMachine():
    # try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    response = s.getsockname()[0]
    s.close()
    return response


# except socket.error:
#	printError("Impossibile determinare indirizzo IPV4 della macchina locale")
#	res = input("Inserire indirizzo a mano? 0 NO, 1 YES")
#	if(res == 1):
#		indirizzo = input("Inserire indirizzo IPV4 macchina locale: ")
#		return indirizzo
#	else:
#		return None

# calcolo ipv6 della macchina locale
def getIpv6AddressLocalMachine():
    # try:
    s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    s.connect(("2001:db8::", 1027))
    response = s.getsockname()[0]
    s.close()
    return ipaddress.ip_address(response.split('%')[0]).exploded
'''

# except socket.error:
#	printError("Impossibile determinare indirizzo IPV6 della macchina locale")
#	res = input("Inserire indirizzo a mano? 0 NO, 1 YES")
#	if(res == 1):
#		indirizzo = input("Inserire indirizzo IPV6 macchina locale: ")
#		return indirizzo
#	else:
#		return None



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
    print(bcolors.WARNING + bcolors.BOLD + "AVVISO -> " + string + bcolors.ENDC)


def printResponse(string):
    print(bcolors.OKBLUE + bcolors.BOLD + "RISPOSTA RICEVUTA -> " + string + bcolors.ENDC)


def trovaFile(fileAggiunti, filemd5):
    i = 0
    while i < len(fileAggiunti):
        if fileAggiunti[i].FILEMD5 == filemd5:
            return fileAggiunti[i].PERCORSO
        else:
            i = i + 1
    printWarning("trovaFile: MD5 non trovato tra i file aggiunti")
    return None


class salvaFileAggiunti:
    PERCORSO = ''
    FILEMD5 = ''

    def __init__(self, PERCORSO, FILEMD5):
        self.PERCORSO = PERCORSO
        self.FILEMD5 = FILEMD5


def creazioneSocket(IPP2P, PortaP2P):
    s = None
    for res in socket.getaddrinfo(IPP2P, PortaP2P, socket.AF_UNSPEC, socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        try:
            s = socket.socket(af, socktype, proto)
        except OSError as msg:
            s = None
            continue
        try:
            s.connect(sa)
        except OSError as msg:
            s.close()
            s = None
            continue
        break
    if s is None:
        printError('creazioneSocket: Impossibile aprire la socket')
    return s


# calcolo hash file
#return None se inesistente
def encryptMD5(filename):
    BLOCKSIZE = 128
    hasher = hashlib.md5()
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            buf = f.read(BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(BLOCKSIZE)
            f.close()
        filemd5 = hasher.hexdigest()
        # print(str(msg))
        # res = makeStringLength(str(msg),100)
        return filemd5
    else:
        printError("encryptMD5: file inesistente")
        return None

# controllo se l'ip è valido (ben formato)
def isValidIPv4(address):
    try:
        ipaddress.IPv4Address(address)
        return True
    except ValueError:
        printError("L'IP inserito non è un IPv4 valido")
        return False

def isValidIPv6(address):
    try:
        ipaddress.IPv6Address(address)
        return True
    except ValueError:
        printError("L'IP inserito non è un IPv6 valido")
        return False

# leggo nByte dalla socket sock
def getNByteFromSocket(sock, nByte):
    return sock.recv(nByte).decode()


# analizzo la risposta della directory alla richiesta di ricerca
#inserire timeout wait sulla socket
def parseString(sock):
    FILEMD5 = 32
    FILENAME = 100
    IPP2P = 55
    PP2P = 5

    response = getNByteFromSocket(sock, 4)
    print(response)
    if not response.startswith('AFIN'):
        printError("FORMATO RISPOSTA SERVER NON CORRETTO")
        printWarning("INIZIO RISPOSTA: " + response + " LEN: " + str(len(response)))
        return [], [], [], []

    idmd5 = getNByteFromSocket(sock, 3)
    numeroIDMD5 = int(idmd5)

    if numeroIDMD5 == 0:
        printError("NUMERO FILE MD5 TROVATI = 0")
        printWarning("Risposta server: " + response)
        return [], [], [], []

    print(numeroIDMD5)
    print("find: numero idmd5: " + idmd5)

    listaMd5 = []
    listaFilename = []
    listaNumeroCopie = []
    listaIP = []  # lista di liste
    listaPorte = []  # lista di liste

    response = getNByteFromSocket(sock, FILEMD5)  # primo file md5

    #numeroIDMD5 = numeroIDMD5 - 1

    while True:
        listaMd5.append(response)
        response = getNByteFromSocket(sock, FILENAME)
        print("filename: " + response.strip())
        listaFilename.append(response)
        numeroCopie = getNByteFromSocket(sock, 3)
        print("numeroCopie: " + numeroCopie)
        listaNumeroCopie.append(numeroCopie)

        ipListTemp = []
        portListTemp = []

        for i in range(0, int(numeroCopie)):
            response = getNByteFromSocket(sock, IPP2P)  # controllare se è valido
            print("IPP2P: " + response)
            ipListTemp.append(response)
            response = getNByteFromSocket(sock, PP2P)
            print("pp2p:" + response)
            portListTemp.append(response)
            numeroIDMD5 = numeroIDMD5 - 1

        listaIP.append(ipListTemp)
        listaPorte.append(portListTemp)
        printWarning(str(numeroIDMD5))
        if numeroIDMD5 == 0:
            break

        response = getNByteFromSocket(sock, FILEMD5)  # primo file md5

        print("filemd5: " + response)
    print(listaMd5)
    print(listaFilename)
    print(listaIP)
    print(listaPorte)
    return listaMd5, listaFilename, listaIP, listaPorte


def sceltaMenu(listaMd5, listaFilename, listaIP, listaPorte):
    print("Corrispondenze:")
    print("Lunghezza lista md5: " + str(len(listaMd5)))
    for i in range(len(listaMd5)):
        print("[" + str(i) + "] -" + " Md5: " + listaMd5[i] + " Filename: " + listaFilename[i])
        print("Lista ip len: " + str(len(listaIP[i])))
        for j in range(len(listaIP[i])):
            print("[" + str(i) + "][" + str(j) + "]" + " IP: " + listaIP[i][j] + " Porta: " + listaPorte[i][j])
        print("----------")
    name = int(input("Scelta file: "))
    peer = int(input("Scelta peer: "))

    return listaMd5[name], listaFilename[name], listaIP[name][peer], listaPorte[name][peer]


def connessioneDirectory():
    while 1:
        if(random.random()>0.5 and random.random()<0.9):
            ip_directory = input('Inserire indirizzo IPv4 della directory: ')
            if (isValidIPv4(ip_directory)):
                peer_socket = creazioneSocket(ip_directory, port)
                if peer_socket is None:
                    continue
                else:
                    return peer_socket
        elif(random.random()<0.5):
            ip_directory = input('Inserire indirizzo IPv6 della directory: ')
            if (isValidIPv6(ip_directory)):
                peer_socket = creazioneSocket(ip_directory, port)
                if peer_socket is None:
                    continue
                else:
                    return peer_socket



def login(sock, ipv4Addr, ipv6Addr, serverPort):
    ipv6Addr = expandIpv6Address(ipv6Addr)
    msg = "LOGI" + "128.000.000.111" + "|" + str(ipv6Addr) + str(serverPort).zfill(5)
    sock.send(msg.encode())
    # Controllo risposta del server
    try:
        response = sock.recv(20).decode()
        #printResponse('login: ' + response)
        sessionid = response[4:20]
        if (response.startswith('ALGI') is False) or (sessionid == "0000000000000000"):
            printError("login: Login fallito")
            printError("login: Risposta: " + str(response))
            return None
        elif len(response) != 20:
            printError("login: Lunghezza risposta non corretta: " + str(len(response)))
            return None
        else:
            printConfirm("login: Login eseguito correttamente")
            printResponse("login: Risposta: " + str(response))
            return sessionid
    except socket.timeout:
        printError("login: Nessuna risposta ricevuta dal server")
        return None


def aggiuntaFile(sock, sessionID, filename):
    # msg = "ADDF" + str(sessionID) + hashlib.md5(filename) + makeStringLength(filename,100)
    global fileAggiunti

    filemd5 = encryptMD5(filename)
    if filemd5 is not None:
        msg = "ADDF" + str(sessionID) + filemd5 + str(filename).ljust(100)
        sock.send(msg.encode())
        # print("Inviato al server comando di aggiuntaFile")
        # aspetto la risposta AADD[4].numeroCopie[3]
        try:
            response = sock.recv(7).decode()
            numeroCopie = response[4:7]
            # print(response)
            if not response.startswith('AADD'):
                printError("FILE NON AGGIUNTO CORRETTAMENTE")
                printWarning("Risposta: " + response)
            elif len(response) != 7:
                printError("Lunghezza risposta non corretta: " + str(len(response)))
            else:
                printResponse("response: " + response)
                printResponse("numeroCopie: " + numeroCopie)
            #fileAggiunti[indiceLista] = salvaFileAggiunti(filename, filemd5)
            fileAggiunti.append(salvaFileAggiunti(filename, filemd5))
            #indiceLista = indiceLista + 1
            return filemd5
        except socket.timeout:
            printError("NESSUNA RISPOSTA RICEVUTA DAL SERVER")
            return None
        except socket.error:
            printError("aggiuntafile: socketError")
            return  None
    else:
        printError("aggiuntaFile: il file non esiste, non aggiunto")


#sulla remove adel 999 se fallisce
def rimuoviFile(peer_socket, SessionID, file):
    fileMD5 = encryptMD5(file)
    if fileMD5 is not None:
        packet = "DELF" + SessionID + fileMD5
        peer_socket.send(packet.encode())
        try:
            response = peer_socket.recv(7).decode()
            numeroCopie = response[4:7]
            printResponse(response)
            if not response.startswith("ADEL"):
                printError("FILE NON RIMOSSO CORRETTAMENTE")
                printWarning("Risposta del server: " + response)
            elif len(response) != 7:
                printError("Lunghezza risposta non corretta: " + str(len(response)))
                printWarning("Risposta del server: " + response)
            elif numeroCopie == 999:
                printWarning("remove: file non rimosso correttamente")
                printWarning("Risposta del server: " + response)
            else:
                printConfirm("Risposta corretta: " + response)
                printConfirm("Numero Copie: " + numeroCopie)
        except socket.timeout:
            printError("NESSUNA RISPOSTA RICEVUTA DAL SERVER")
    else:
        stringError = "rimuoviFile: il file " + file + " che si vuole rimuovere non eiste nel path"
        printError(stringError)

def ipDivide(ipPeer):
    ipv4=ipPeer.ljust(15)
    ipv6=ipPeer.rjust(39)
    return ipv4,ipv6

#se mando *, restituisce tutti i file trovati
#IL FILENAME DEVE ESSERE RJUST ALTRIMENTI WINDOWS SI PIANTA E FA STORIE CON ESTENSIONE
def ricerca(sock, sessionID, stringa):
    fileToFind = stringa.rjust(20)
    msg = "FIND" + str(sessionID) + str(fileToFind)
    sock.send(msg.encode())
    # cotrollo risposta AFIN[4].idmd5[3].altrielementi
    listaMd5, listaFilename, listaIP, listaPorte = parseString(sock)

    # SE I PRECEDENTI NON SONO VALIDI ESCI E NON FARE SCELTA MENU (Nel caso il server vada in errore)
    if listaMd5 == [] or listaFilename == [] or listaIP == [] or listaPorte == []:
        printWarning("ricerca: File non trovato")
    else:
        md5, nome, ipPeer, portaPeer = sceltaMenu(listaMd5, listaFilename, listaIP, listaPorte)
        print("Porta peer: " + str(portaPeer))
        print("Download del file " + nome.strip() + " dal peer " + ipPeer + ":" + portaPeer)

        ipv4,ipv6=ipDivide(ipPeer)
        if (random.random() > 0.5 and random.random() < 0.9):
            ipPeer=ipv4
        elif(random.random() < 0.5):
            ipPeer = ipv6

        ipPeer = removeZeroIpAddress(ipPeer)
        print(ipPeer)
        downloadP2P(ipPeer,portaPeer,md5)
        if peerDownload(ipPeer, portaPeer, md5, nome):
            printConfirm("Il file è stato salvato con successo!")
            infoServer(sock, sessionID, md5)
        else:
            printError("File non scaricato correttamente")

def downloadP2P(ip_peer, porta_peer, filemd5):
    p2psocket = creazioneSocket(ip_peer, porta_peer)
    pacchetto = "RETR" + filemd5
    p2psocket.send(pacchetto.encode())
    return p2psocket


# Funzione che apre la socket con il peer da dove scaricare
def peerDownload(ipdownload, portdownload, md5, filename):
    # path = 'download'
    # Se non è già presente aggiungo alla fine della stringa il separatore (/ o \\ a seconda del OS)
    # if path[-1] != os.sep: path += os.sep
    # fd = os.open(path+filename, os.O_WRONLY | os.O_CREAT, 777)
    try:
        fd = os.open(filename, os.O_WRONLY | os.O_CREAT, 777)
    except OSError:
        printError('peerDownload: Impossibile creare il file: ' + filename.strip() + ' | Controlla di avere i permessi')
        return False

    socketp2p = downloadP2P(ipdownload, portdownload, md5)

    rispostapeer = socketp2p.recv(10).decode()
    printResponse("rispostaPeer: " + rispostapeer)
    if not rispostapeer:
        printError("peerDownload: Errore ricezione pacchetto download dal peer")
        return False

    comandopeer = rispostapeer[0:4]
    if comandopeer != "ARET":
        printError("peerDownload: Risposta errata del peer")
        return False

    # Determino il numero di chunk
    nchunk = int(rispostapeer[4:10])

    # Ricevo il file
    i = 0
    while i < nchunk:
        lenchunk = socketp2p.recv(5).decode()
        while len(lenchunk) < 5:
            lenchunk = lenchunk + socketp2p.recv(1).decode()
        lenchunk = int(lenchunk)
        data = socketp2p.recv(lenchunk)
        while len(data) < lenchunk:
            data = data + socketp2p.recv(1)
        os.write(fd, data)
        i = i + 1

    os.close(fd)
    socketp2p.close()  # chiudo la socket con il peer da cui ho effettuato il download
    return True


# notifica di avvenuto download
def infoServer(sock, sessionID, fileMD5):
    msg = "DREG" + str(sessionID) + str(fileMD5)
    sock.send(msg.encode())
    # controllo risposta
    response = sock.recv(9).decode()
    printResponse('infoServer: ' + response)
    numdown = response[5:7]  # AADD
    if not response.startswith('ADRE'):
        printConfirm("NOTIFICA AL SERVER NON AVVENUTA CORRETTAMENTE")
    if len(response) != 9:
        printError("Lunghezza risposta non corretta: " + str(len(response)))
        printWarning("RISPOSTA: " + response)
    else:
        printConfirm("Notifica al server eseguita correttamente")
        printConfirm("Numero download: " + str(numdown))
        sock.close()


def logout(sock, sessionid):
    msg = "LOGO" + str(sessionid)
    sock.send(msg.encode())
    try:
        response = sock.recv(7).decode()
        printResponse('logout: ' + response)
        if response.startswith('ALGO') is False:
            printError("logout: Logout fallito")
            return False
        elif len(response) != 7:
            printError("logout: Lunghezza risposta non corretta: " + str(len(response)))
            return False
        else:
            printConfirm("logout: Logout eseguito correttamente")
            sock.close()
            return True
    except socket.timeout:
        printError("logout: Nessuna risposta ricevuta dal server")


class peerServer(threading.Thread):
    host = '::0'
    port = 50005
    maxconn = 10
    clients = {}

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        s = None
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
            printError('peerServer: Non sono riuscito ad aprire la socket in ascolto')
            printError('peerServer: Termino il processo')
            os._exit(0)

        printConfirm('peerServer: Avviato correttamente')
        printConfirm('peerServer: In ascolto sulla porta: ' + str(self.port))

        while 1:
            try:
                # Attendo una connessione
                (conn, addr) = s.accept()
                # Costruisco un identificatore per la connessione
                cid = str(addr[0]) + ':' + str(addr[1])
                printConfirm('peerServer: Connesso a ' + cid)
                # Avvio un thread per gestire la connessione
                peerServer.clients[cid] = peerUpload(cid, conn, peerServer)
                peerServer.clients[cid].start()
            except socket.error:
                break


class peerUpload(threading.Thread):
    id = ''
    socket = ''
    server = None

    def __init__(self, id, socket, server):
        threading.Thread.__init__(self)
        self.id = id
        self.socket = socket
        self.server = server

    def run(self):
        trasferimentocompletato = True
        socketp2p = self.socket

        identificativo = socketp2p.recv(4).decode()
        if not identificativo:
            printError('peerUpload[' + self.id + ']: Problemi di ricezione pacchetto RETR')
            self.close()
            sys.exit(1)

        if identificativo != 'RETR':
            printError('peerUpload[' + self.id + ']: Identificativo RETR non ricevuto')
            self.close()
            sys.exit(1)

        filemd5 = socketp2p.recv(32).decode()
        print('Richiesto file: ' + identificativo + filemd5)
        filename = trovaFile(fileAggiunti, filemd5)
        if filename is None:
            self.close()
            sys.exit(1)

        try:
            fd = os.open(filename, os.O_RDONLY)
        except OSError:
            printWarning('peerUpload[' + self.id + ']: File ' + filename + ' non più presente sul disco')
            self.close()
            sys.exit(1)

        filesize = os.fstat(fd)[stat.ST_SIZE]

        # Calcolo i chunk
        nchunk = filesize / 4096
        # Verifico se il file si divide esattamente nei chunk
        if (filesize % 4096) != 0:
            nchunk = nchunk + 1

        nchunk = int(float(nchunk))
        # Invio identificativo al peer
        pacchetto = "ARET" + str(nchunk).zfill(6)
        socketp2p.send(pacchetto.encode())

        printConfirm(
            'peerUpload[' + self.id + ']: Trasferimento in corso di ' + filename + ' [BYTES ' + str(filesize) + ']')

        i = 0
        while i < nchunk:
            buf = os.read(fd, 4096)
            if not buf:
                break
            sbuf = len(buf)
            sbuf = str(sbuf).zfill(5)
            sendbytes = socketp2p.send(sbuf.encode())
            if sendbytes != len(sbuf):
                trasferimentocompletato = False
                break
            sendbytes = socketp2p.send(buf)
            if sendbytes != len(buf):
                trasferimentocompletato = False
                break
            i = i + 1

        os.close(fd)
        if trasferimentocompletato:
            printConfirm('peerUpload: Trasferimento completato di ' + str(filename))
        else:
            printError('peerUpload[' + self.id + ']: Non sono riuscito ad inviare i dati sulla socket')
            printError('peerUpload[' + self.id + ']: Errore trasferimento di ' + str(filename))
        self.close()

    def close(self):
        printConfirm('peerUpload[' + self.id + ']: Disconnessione da ' + self.id)
        self.socket.close()
        # Elimino il client dalla lista di client connessi in peerServer
        #ASPETTA UN INVIO PRIMA DI RIMOSTRARE IL MENU
        del peerServer.clients[self.id]


if __name__ == "__main__":
    # Gestore del SIGINT da tastiera
    signal.signal(signal.SIGINT, signalHandler)

    # Avvio processo server in ascolto per scambio file p2p
    s = peerServer()
    s.start()
    time.sleep(0.5)
    sessionID = None

    #inizializzo i valori

    # Debug
    # fileAggiunti.append(salvaFileAggiunti('crash.jpg', '1c3f60a268cd166d867f34196f1b985c'))


    while 1:

        # Aspetto mezzo secondo prima di stampare a video il menù di scelta
        time.sleep(0.5)
        print(bcolors.WARNING + bcolors.BOLD    + "      ____           ____ _ _            _	" + bcolors.ENDC)
        print(bcolors.FAIL + bcolors.BOLD       + " _ __|___ \ _ __    / ___| (_) ___ _ __ | |_ " + bcolors.ENDC)
        print(bcolors.OKBLUE + bcolors.BOLD     + "|  _ \ __) |  _ \  | |   | | |/ _ \  _ \| __|" + bcolors.ENDC)
        print(bcolors.OKGREEN + bcolors.BOLD    + "| |_) / __/| |_) | | |___| | |  __/ | | | |_ " + bcolors.ENDC)
        print(bcolors.WARNING + bcolors.BOLD    + "|  __/_____|  __/   \____|_|_|\___|_| |_|\__|" + bcolors.ENDC)
        print(bcolors.FAIL + bcolors.BOLD       + "|_|        |_|   							\n" + bcolors.ENDC)
        print("< 1 >  LOGIN")
        print("< 2 >  AGGIUNTA FILE")
        print("< 3 >  RIMOZIONE FILE")
        print("< 4 >  RICERCA")
        print("< 5 >  LOGOUT")

        try:
            code = input("\nInserire uno dei precedenti codici per svolgere un'azione:\n")
        except:
            continue

        if code == '1' and sessionID is None:
            peer_socket = connessioneDirectory()
            sessionID = login(peer_socket, ipv4, ipv6, peerServer.port)

        #per evitare il deadlock: se da loggato faccio login, sovrascrivo il sessionid e rimango bloccato

        #controllare di aver fatto il login prima di effettuare altre operazioni
        elif sessionID is None and code != '1':
            printError("Effettuare il login prima di qualsiasi operazione")

        elif code == '2':
            filename = input("Inserire il nome del file che si intende aggiungere: ")
            md5File = aggiuntaFile(peer_socket, sessionID, filename)
            if md5File is not None:
                fileAggiunti.append(salvaFileAggiunti(filename, md5File))

        elif code == '3':
            filename = input("Inserire il nome del file che si intende rimuovere: ")
            rimuoviFile(peer_socket, sessionID, filename)

        elif code == '4':
            filename = input("Inserire il nome del file che si intende cercare: ")
            ricerca(peer_socket, sessionID, filename)

        elif code == '5':
            result = logout(peer_socket, sessionID)
            if result:
                os._exit(0)
