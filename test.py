import asyncore
import socket
from multiprocessing.connection import Listener, Client

class ConnectionListener(asyncore.dispatcher):
	def __init__(self, ln):
		asyncore.dispatcher.__init__(self)
		self.create_socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
		self.set_socket(ln._listener._socket)
	def handle_accepted(self, sock, addr):
		print("Accepted a client!")

if __name__ == "__main__":
	address = ('localhost', 19378)
	try:
		ln = Listener(address)
		x = ConnectionListener(ln)
		while True:
			asyncore.loop()
	except socket.error:
		c = Client(address)
		print("Client is trying to connect")
