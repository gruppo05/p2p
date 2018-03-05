import socket
import sqlite3

class Napster(object):
	def start(self):
		#Clear all the db al primo lancio??
		
		IP = "127.0.0.1"
		PORT = 3000
		
		# Creo DB
		conn = sqlite3.connect(':memory:')
		print "Creato db %s" % conn
		c = conn.cursor()
		
		# Creo tabella user
		c.execute("DROP TABLE IF EXISTS user")
		c.execute('''CREATE TABLE user (SessionID text, IPP2P text, PP2P text)''')
		print "Tabella user creata..."
		
		# Creo socket
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_address = (IP, PORT)
		sock.bind(server_address)
		
		print "Server attivo su %s porta %s" % server_address
		sock.listen(1)
		while True:
			print "In attesa di connessione..."
			connection, client_address = sock.accept()
			
			try:
				print "Connessione da", client_address
				data = str(connection.recv(4))
				print "Ricevuto", data
				if data == "LOGI":
					print "Start login"

					IPP2P = str(connection.recv(55))
					print "IP client:", IPP2P

					IPP = str(connection.recv(5))
					print "Porta client:", IPP

					#Inserimento
					c.execute("INSERT INTO user VALUES('789', '127.2.2.1', '8080')")

					c.execute("SELECT * FROM user")
					for row in c:
						print(row)
						
				if data == "DELF":
					print "Delete file"
				elif data == "FIND":
					print "Find file name"
				elif data == "ADDF":
					print "Add file"
				elif data == "LOGO":
					print "Log out"
				elif data == "DREG":
					print "Download"
			except:
				print "Errore lato server"
			finally:
				connection.close()
				
if __name__ == "__main__":
    nasper = Napster()
nasper.start()










































