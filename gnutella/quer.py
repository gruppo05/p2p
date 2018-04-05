def querReceiver(self,connection):

    try:
        pktid = connection.recv(16).decode()
        ipp2p = connection.recv(39).decode()
        pp2p = connection.recv(5).decode()
        ttl = connection.recv(2).decode()
        ricerca = = connection.recv(20).decode()

        print "[QUER] Ricevuta da: " + ipp2p + " , con Pktid: " + pktid + " , con TTL: " + ttl + " , ricerca: " + ricerca + " ."

    	#controllo che il pacchetto che mi è arrivato non l'ho già ricevuto
        self.dbReader.execute("SELECT * FROM pacchetto WHERE PacketId = ?", (pktid,))
        data = self.dbReader.fetchOne()

        if data is None:
            #non ho mai ricevuto il pacchetto, prima di andarlo a considerare, lo memorizzo
            self.dbReader.execute("INSERT INTO pacchetto (PacketId)", (pktid,))

            #ora vado avanti con il resto

            #ttl > 1 : decremento ttl poi ripropago (devo fare in modo di non rimandare il pkt a chi ha fatto la richiesta se l'ho tra i vicini
            #ttl = 0 : rispondo solo io alla richiesta se possibile
            if int(ttl)>1:
                ttl = ttl - 1

                #prendo la lista vicini per poi andare a mandare il pacchetto da ritrasmettere
                self.dbReader.execute( "SELECT * FROM vicini " )
                data = self.dbReader.fetchAll()

                for n in data:
                    if data[n][0] != ipp2p and data[n][1] != pp2p: # rimando il pacchetto a tutti tranne quelli che me lo hanno rimandato

			#rnd=random()
			rnd=0.1
			if(rnd < 0.5):
				#ipv4
				print("Connetto ad IPv4: "+data[0][0:15]+" , "+ int(data[1]))
				peer_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
				peer_socket.connect((data[0][0:15],data[1]))
			else:
				print("Connetto con IPv6: "+data[0][16:55]+" , "+data[1])
				peer_socket=socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
				peer_socket.connect((data[0][16:55],data[1]))
			
			msg="QUER"+pktid+ipp2p+pp2p+ttl+ricerca
			print("Invio: "+msg)
			peer_socket.sendall((msg).encode())
			peer_socket.close()
                            
            #ora che ho rimandato il pacchetto, sia in un caso (ttl=1) che l'altro (ttl=0), devo fare la ricerca in mezzo ai miei di file
            
            #ricerco se tra i miei file c'è quello desiderato
	    self.dbReader.execute("SELECT * FROM file WHERE Filename LIKE ?", ('%' + ricerca + '%',))
	    data = self.dbReader.fetchAll()
	    #se NON ho risultati...
	    if data in None:
		print "Nessun dato nel mio fileSystem che contiene: " + ricerca
		return false
	    else
		for n in data:
			#socket_vicini = openConn(ipp2p,pp2p)
			
			#rnd=random()
			rnd=0.1
			if(rnd < 0.5):
				print("Connetto ad IPv4: "+ipp2p+" , "+ int(pp2p))
				peer_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
				peer_socket.connect((ipp2p,int(pp2p)))
			else:
				print("Connetto con IPv6: "+ipp2p+" , "+int(pp2p))
				peer_socket=socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
				peer_socket.connect((ipp2p,int(pp2p)))
			
			msg="AQUE"+pktid+ _MIOIP + _MIAPORTA + filemd5 + ricerca
			print("Invio: "+msg)
			peer_socket.sendall((msg).encode())
			peer_socket.close()
                
                #da definire come ottenere mioIp, miaPorta
                
        else:
            print "Già ricevuto PKT con Pktid: " + pktid + " , non rispondo"




#####funzione ascolto AQUE
def aque(self,connection)
    pktid=connection.recv(16).decode()
    ipp2p=connection.recv(55).decode()
    pp2p=connection.recv(5).decode()
    filemd5=connection.recv(16).decode()
    filename=connection.recv(100).decode()
    #DA RIEMPIRE CON LA INSERT PER IL DB
    self.dbReader.execute(-----------------------)


def querSender(self, connection)
	fileDaCercare = input("Inserisci valore della ricerca:")
	pktid = ### da generare random, vedere la funz di francesco
	ttl = 2
	#faccio la query per trovare tutti i miei vicini
	self.dbReader.execute("SELECT * FROM vicini")
	data = self.dbReader.fetchAll()
		
	for n in data:
		#rnd=random()
			rnd=0.1
			if(rnd < 0.5):
				#ipv4
				print("Connetto ad IPv4: "+data[0][0:15]+" , "+ int(data[1]))
				peer_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
				peer_socket.connect((data[0][0:15],data[1]))
			else:
				print("Connetto con IPv6: "+data[0][16:55]+" , "+data[1])
				peer_socket=socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
				peer_socket.connect((data[0][16:55],data[1]))
			
			msg="QUER"+pktid+ _MIOIP + _MIAPORTA + ttl + fileDaCercare
			print("Invio: "+msg)
			peer_socket.sendall((msg).encode())
			peer_socket.close()