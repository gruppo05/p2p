import socket
import sqlite3

IP = "127.0.0.1"
PORT = 3000
BUFF_SIZE = 4

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

		data = str(connection.recv(BUFF_SIZE))
		print "Ricevuto", data
		if data == "LOGI":
			print "Start login"
			
			#Inserimento test
			c.execute("INSERT INTO user VALUES('789', '127.2.2.1', '8080')")

			c.execute("SELECT * FROM user")
			for row in c:
			  print(row)
			  
		if data == "DELF":
			print "Delete file"
		if data == "FIND":
			print "Find file name"
		if data == "ADDF":
			print "Add file"
		if data == "LOGO":
			print "Log out"
		if data == "DREG":
			print "Download"
    except:
    	print "Errore lato server"
    finally:
    	connection.close()
    	
    	
    	











































