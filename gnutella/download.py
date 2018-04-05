'''Scaricare un file'''

while True:
			print("In attesa di connessione...")
			
			try:
				if command == "1":
					print("primo")
				elif command == "2":
					print("secondo")
				elif command == "3":
					print("Download")
					print("Quale file vuoi scaricare?")
					self.dbReader.execute("SELECT * FROM File WHERE IPP2P != ?", (IP,))
					resultFile = self.dbReader.fetchall()
					
					files[0] = ("0","0","0")
					int i = 1
					for resultFile in resultFile:
						files[i] = (resultFile[0], resultFile[1], resultFile[2])
						print(i + " - " + resultFile[1])
						
					code = input("\n ")	
					
					connection.sendall(("RETR" + files[code][0]).encode())
					
			except:
				print("Errore lato server")
			finally:
				print("\n\n")
				
				
''' inviare un file'''

if command == "RETR"
				
				FileMD5 = connection.recv(55).decode()
				self.dbReader.execute("SELECT Filename FROM File WHERE FileMD5 = ?",(FileMD5,))
				resultFile = self.dbReader.fetchone()
				f = os.open(str(resultFile), os.O_RDONLY)
				
				filesize = os.fstat(fd)[stat.ST.SIZE]
				nChunck = filesize / 4096
				
				if (filesize % 4096)!= 0:
					nChunk = nChunk + 1
				
				nChunk = int(float(nChunk))
				pacchetto = "ARET" + str(nChunk).zfill(6)
				sock.send(pacchetto.encode())
				print ('Trasferimento in corso di ', resultFile, '[BYTES ', filesize, ']')
				
				i = 0
				
				while i < nChunk:
					buf = os.read(fd,4096)
					if not buf: break
					lbuf = len(buf)
					lbuf = str(lBuf).zfill(5)
					sock.send(lBuf.encode())
					sock.send(buf)
					i = i + 1
					
				os.close(fd)
				print('Trasferimento completato.. ')
				
				#chiusura della connessione
				connection.close()
				#chiusura della socket
				sock.close()
				
				
				
				
