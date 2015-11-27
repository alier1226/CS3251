__author__ = 'jli'
import socket
from RxpSocket import RxpSocket
from random import randint
import time

MAXSEQNUM = pow(2,32) - 1
HEADERSIZE = 131
DATASIZE = 3000
PACKETSIZE = HEADERSIZE + DATASIZE

class RxpServerSocket(RxpSocket):

	def __init__(self, debug):

		#call constructor of parent class
		super(RxpServerSocket,self).__init__(debug)
		self.d = debug
		#self.seqNumber = randint(0, pow(2,32) - 1)
		self.seqNumber = 0
		self.expectedSeq = 0



	#listen for potential connections
	def accept(self):
		if self.states["Accepting"]:
			# generate random sequence number
			if self.d: print "Server listening for SYN"
			data, clientAddr = self._recvAndAckNum(PACKETSIZE)
			rcvheader, rcvData = self._decodeHeader(data)

			# check for corruption
			if not self._checkChecksum(rcvheader["checksum"],data):
				if self.d: print "packet corrupted"
				return None

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
						rcvHeader, rcvData = self._decodeHeader(data)

						if rcvHeader["flags"] == 0b010:
							goodRes = True

					#if ack is corrupt or lost, just assume client sent ACK
					except socket.timeout:
						if self.d: print "Did not receive ACK"
						#return False
						continue

				if loop <= 0:
					if self.d: print "Did not receive ACK, handshake complete"
				else:
					if self.d: print "Received ACK, handshake complete"
					self.nextSeqNumber = rcvHeader["seqNum"] + 1


				self.states["Connected"] = True

				return self
			return None
	#accept a client
	def listen(self):

		self.seqNumber = randint(0, pow(2,32) - 1)
		self.expectedSeq = 0
		self.socket.settimeout(None)
		self.states["Accepting"] = True

		# self.socket.settimeout(None)
		# if self.d: print "Waiting on client command"
		# data, clientAddrs = self._recvAndAckNum(PACKETSIZE)
		# rcvheader, rcvData = self._decodeHeader(data)
		#
		#
		#
		# #check for corruption
		# if not self._checkChecksum(rcvheader["checksum"],data[:-len(rcvData)]):
		# 	if self.d: print "packet corrupted"
		# 	return False
		#
		# # ACK the client command
		# if self.d: print "Data received:", rcvData
		# header = self._createPacket("ACK", None)
		# if self.d: print "Acknowledging client command"
		# self.socket.sendto(header, (self.hostAddress, self.emuPort))
		#
		# _, self.expectedPackets = rcvData.split(":")
		# self.expectedPackets = int(self.expectedPackets)
		# if self.d: print "Expected packets:", self.expectedPackets




	#Private Functions

