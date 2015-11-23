__author__ = 'jli'
import socket



class RxpSocket(object):
	def __init__(self, debug):

		self.d = debug

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.value = 9
		self.timeout = 0
		self.windowSize = 0
		self.packetSize = 2000

		self.portNumber = None
		self.hostAddress = None

		self.statuses = [
			"Connected",
			"Not_Connected"
		]

		self.state = "Not_Connected"

	# close connection
	def close(self):
		return

	# receive from client
	def recv(self, bufsize):
		return

	# send data
	def send(self, data):
		self.socket.sendto(data, )
		return

	# set the timeout value
	def setTimeout(self, value):
		self.timeout = value

	# set the window size
	def setWindowSize(self, value):
		self.windowSize = value

	def connect(self, addrs, port):
		self.portNumber = port
		self.hostAddress = addrs


	def test(self):
		print "Base"
