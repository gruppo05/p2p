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
		print "Ricevuto", command
		if command == "LOGI":
			print "Start login"
			
			IPP2P = str(connection.recv(55))
			print "IP client:", IPP2P
			
			IPP = str(connection.recv(5))
			print "Porta client:", IPP
			
			SessionID = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(16)])	
			print SessionID
				
			#Inserimento
			c.execute("INSERT INTO user (SessionID, IPP2P, PP2P) values (?, ?, ?)",
            (SessionID, IPP2P, IPP))
			
			#Stampo
			c.execute("SELECT * FROM user")
			for row in c:
			  print(row)
			  
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
    except:
    	print "Errore lato server"
    finally:
    	connection.close()
    	
    	
    	











































