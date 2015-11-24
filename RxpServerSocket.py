__author__ = 'jli'
import socket
from RxpSocket import RxpSocket
from random import randint

class RxpServerSocket(RxpSocket):

	def __init__(self, debug):

		#call constructor of parent class
		super(RxpServerSocket,self).__init__(debug)
		self.d = debug



	#listen for potential connections
	def listen(self, backlog):

		# generate random sequence number
		self.seqNumber = randint(0, pow(2,32) - 1)
		self.socket.settimeout(None)

		if self.d: print "Server listening for SYN"
		data, clientAddr = self.socket.recvfrom(self.packetSize)
		rcvheader = self._decodeHeader(data)



		# check for header corruption
		if not self._checkChecksum(rcvheader["checksum"],data):
			if self.d: print "rcvheader corrupted"
			return False

		# check for SYN flag
		if rcvheader["flags"] == 0b100:

			self.socket.settimeout(1)
			header = self._createPacketHeader("SYNACK", None)
			if self.d: print "Received SYN, sending SYNACK"

			# keep sending SYNACK until a valid response is heard
			goodRes = False
			loop = 5
			while not goodRes and loop > 0:
				loop += -1
				try:
					if self.d: print "Repeat sending SYNACK to", clientAddr
					self.socket.sendto(header, (self.hostAddress, self.emuPort))
					data, clientAddr = self.socket.recvfrom(self.packetSize)
					rcvHeader = self._decodeHeader(data)


					# check for header corruption
					if not self._checkChecksum(rcvHeader["checksum"],data):
						if self.d: print "rcvHeader corrupted"
						continue


					# check for ACK flag
					if rcvHeader["flags"] == 0b010:
						goodRes = True


				except socket.timeout:
					continue

			if loop <= 0:
				print "Did not receive last ACK from client, reset connection"
				return None

			if self.d: print "Received ACK, handshake complete"
			self.states["Connected"] = True

			return self.socket, clientAddr

	#accept a client
	def accept(self):
		self.socket.accept()

	#Private Functions

