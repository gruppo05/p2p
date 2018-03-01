import socket
import sqlite3
import random
import string

IP = "127.0.0.1"
PORT = 3000

# Creo DB
conn = sqlite3.connect(':memory:')
print "Creato db %s" % conn
c = conn.cursor()

# Creo tabella user
c.execute("DROP TABLE IF EXISTS user")
c.execute('''CREATE TABLE user
             (SessionID text, IPP2P text, PP2P text)''')
print "Tabella user creata..."

# Creo socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (IP, PORT)
print "Server attivo su %s porta %s" % server_address
sock.bind(server_address)
sock.listen(1)

while True:
    print "In attesa di connessione..."
    connection, client_address = sock.accept()
    
    try:
		print "Connessione da", client_address

		command = str(connection.recv(4))
		
		if command == "LOGI":
			print "Start login"
			
			IPP2P = str(connection.recv(55))
			IPP = str(connection.recv(5))
			
			#Cerco IP utente
			result = c.execute("SELECT SessionID FROM user WHERE IPP2P=?", (IPP2P,))
 			if result.fetchone() is None:
 				print "*************** NON TROVATO ***************"
 				SessionID = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(16)])
 				
 				#Inserimento
				c.execute("INSERT INTO user (SessionID, IPP2P, PP2P) values (?, ?, ?)",
            	(SessionID, IPP2P, IPP))
            	
 			else:
 				print "*************** TROVATO ***************"
 				c.execute("SELECT SessionID FROM user WHERE IPP2P=?", (IPP2P,))
				data = c.fetchone() #retrieve the first row
				SessionID = data[0]
				
			print "SessionID:", SessionID		
			#Da implementare processio di invio del SessionID...
			  
		if command == "DELF":
			print "Delete file"
		if command == "FIND":
			print "Find file name"
		if command == "ADDF":
			print "Add file"
		if command == "LOGO":
			print "Log out"
		if command == "DREG":
			print "Download"
		
		# *************** DA TOGLIERE *********************
		if command == "STAM":
			#Stampo
			c.execute("SELECT * FROM user")
			for row in c:
				print(row)
		# *************************************************
    except:
    	print "Errore lato server"
    finally:
    	connection.close()
    	
    	
    	











































