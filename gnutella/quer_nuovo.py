	'''def attesaRicerca(self)
		while True:
			connection, client_address = self.sock5k1.accept()
			#ricevo AQUE
			print("RICEVO: "+connection.recv(4).decode())

			pktid = connection.recv(16).decode()
			IPP2P = connection.recv(55).decode()
			PP2P = connection.recv(5).decode()
			filemd5 = connection.recv(16).decode()
			filename = connection.recv(100).decode()

			dbReader.execute("INSERT INTO File (Filemd5, Filename, IPP2P) values (?,?,?)",(filemd5,filename,IPP2P))
			#verifico se l'utente che mi ha risposto lo conosco, altrimenti lo aggiungo nel db
			dbReader.execute("SELECT IPP2P FROM user WHERE IPP2P=?",(IPP2P,))
			data = dbReader.fetchone()
			if data in None:
				dbReader.execute("INSERT INTO user (IPP2P,PP2P) values (?,?)",(IPP2P,PP2P))
				print(color.green + "Aggiunto nuovo user" + color.end)
			else:
				print(color.fail + "User già presente" + color.end)
	'''	


------internalserver
				'''if command == "QUER":
					print("Ricevuto comando dal client: "+color.recv+command+color.end)
					threading.Thread(target = self.attesaRicerca, args = (data,addr)).start()					#leggo la ricerca che mi arriva dal client					
					ricerca = self.sockUDP.recvfrom(20)
					myPktid = PktidGenerator()
					TTL = setNumber(2)
					dbReader.execute("SELECT * FROM user")
					resultUser = self.dbReader.fetchall()
					
					for user in resultUser:
						#rnd = random()
						rnd = 0.1
						if(rnd<0.5):
							IPP2P = user[0][0:15]
							IPP2P = splitIp(IPP2P)
		
							#fix problem ipv4
							#IPP2P = ipaddress.ip_address(IPP2P)
							#PP2P=int(user[1])
				
							print("Connetto con IPv4:",IPP2P+"  PORT -> ",PP2P)
				
							peer_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
							peer_socket.connect((IPP2P,PORT))
		
						else:
							IPP2P = user[0][16:55]
							print("Connetto con IPv6:", IPP2P)
							break
							#da testare
							connection=creazioneSocketIPv6(IPP2P,user[1])

						msg="QUER" + myPktid + self.myIPP2P + str(self.myPortQuer).ljust(5) + TTL + ricerca
						print("Invio --> " + color.send + msg + color.end)
						peer_socket.sendall(msg.encode())
						peer_socket.close()

				'''


-----starserver
					
		
				'''
				elif command == "QUER":
					print("QUER")
					pktid = connection.recv(16).decode()
					ipp2p = connection.recv(39).decode()
					pp2p = connection.recv(5).decode()
					ttl = connection.recv(2).decode()
					ricerca = = connection.recv(20).decode()

					print "[QUER] Ricevuta da: " + ipp2p + " , con Pktid: " + pktid + " , con TTL: " + ttl + " , ricerca: " + ricerca + " ."
					#controllo che il pacchetto che mi è arrivato non l'ho già ricevuto
					dbReader.execute("SELECT * FROM pacchetto WHERE PacketId = ?", (pktid,))
        				data = dbReader.fetchOne()
					
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
			
							msg="AQUE"+pktid+ self.myIPP2P.ljust(55) + str(self.myPort).ljust(5) + filemd5 + ricerca
							print("Invio: "+msg)
							peer_socket.sendall((msg).encode())
							peer_socket.close()
				
					else:
					    print "Già ricevuto PKT con Pktid: " + pktid + " , non rispondo"

			'''


