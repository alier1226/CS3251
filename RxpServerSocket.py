__author__ = 'jli'
import socket
from RxpSocket import RxpSocket
from random import randint

MAXSEQNUM = pow(2,32) - 1
HEADERSIZE = 131
PACKETSIZE = HEADERSIZE + 3000

class RxpServerSocket(RxpSocket):

	def __init__(self, debug):

		#call constructor of parent class
		super(RxpServerSocket,self).__init__(debug)
		self.d = debug
		self.seqNumber = randint(0, pow(2,32) - 1)



	#listen for potential connections
	def accept(self, backlog):

		# generate random sequence number
		self.socket.settimeout(None)

		if self.d: print "Server listening for SYN"
		data, clientAddr = self._recvAndAckNum(PACKETSIZE)
		rcvheader = self._decodeHeader(data)



		# check for corruption
		if not self._checkChecksum(rcvheader["checksum"],data):
			if self.d: print "packet corrupted"
			return None, None

		# check for SYN flag
		if rcvheader["flags"] == 0b100:

			self.socket.settimeout(1)
			header = self._createPacket("SYNACK", None)
			if self.d: print "Received SYN, sending SYNACK"

			# keep sending SYNACK until a valid response is heard
			goodRes = False
			loop = 10
			while not goodRes and loop > 0:
				loop += -1
				try:
					if self.d: print "Repeat sending SYNACK to", clientAddr
					self.socket.sendto(header, (self.hostAddress, self.emuPort))
					data, clientAddr = self._recvAndAckNum(PACKETSIZE)
					rcvHeader = self._decodeHeader(data)

					if rcvHeader["flags"] == 0b010:
						goodRes = True

				except socket.timeout:
					continue



			if loop <= 0:
				if self.d: print "Did not receive ACK, handshake complete"
			else:
				if self.d: print "Received ACK, handshake complete"

			self.states["Connected"] = True

			return self, clientAddr

	#accept a client
	def listen(self):
		return



	#Private Functions

