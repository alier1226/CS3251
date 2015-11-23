__author__ = 'jli'
import socket
from RxpSocket import RxpSocket


class RxpServerSocket(RxpSocket):

	def __init__(self, debug):

		#call constructor of parent class
		super(RxpServerSocket,self).__init__(debug)
		self.d = debug

	#bind socket to port number
	def bind(self, portNumber):
		self.socket.bind( ('', portNumber) )
		self.portNumber = portNumber


	#listen for potential connections
	def listen(self, backlog):
		self.state = "Listening"
		if self.d: print "State:", self.state
		data, clientAckAddr = self.socket.recvfrom(self.packetSize)


	#accept a client
	def accept(self):
		self.socket.accept()

	def test(self):
		print "Child"