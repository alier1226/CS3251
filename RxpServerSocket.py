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

			self.socket.settimeout(None)
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

				noAck = False
				# keep sending SYNACK until a valid response is heard
				goodRes = False
				#loop = 10
				#while not goodRes and loop > 0:
				while not goodRes:
					#loop += -1
					try:
						if self.d: print "Repeat sending SYNACK to", clientAddr
						self.socket.sendto(header, (self.hostAddress, self.emuPort))
						data, clientAddr = self._recvAndAckNum(PACKETSIZE)
						rcvHeader, rcvData = self._decodeHeader(data)





						# check for corruption
						if not self._checkChecksum(rcvHeader["checksum"],data):
							if self.d: print "ACK packet corrupted"
							#return None
							continue

						if rcvHeader["flags"] == 0b010:
							goodRes = True

						if rcvHeader["flags"] == 0:
							if self.d: print "No ACK, but got data, continuing"
							goodRes = True
							noAck = True
							self.nextSeqNumber = rcvHeader["seqNum"]

					except socket.timeout:
						if self.d: print "Did not receive ACK"
						return False

				# if loop <= 0:
				# 	if self.d: print "Did not receive ACK, handshake complete"
				# else:
				# 	if self.d: print "Received ACK, handshake complete"
				# 	print "SETTING NEXT SEQ -----------ACCEPT", rcvHeader["seqNum"] + 1
				# 	self.nextSeqNumber = rcvHeader["seqNum"] + 1

				if self.d: print "Received ACK, handshake complete"
				#print "SETTING NEXT SEQ -----------ACCEPT", rcvHeader["seqNum"] + 1

				if noAck:
					print "SETTING NEXT SEQ -----------ACCEPT", rcvHeader["seqNum"]
					self.nextSeqNumber = rcvHeader["seqNum"]
				else:
					print "SETTING NEXT SEQ -----------ACCEPT", rcvHeader["seqNum"] + 1
					self.nextSeqNumber = rcvHeader["seqNum"] + 1


				self.states["Connected"] = True

				return self
			return None
	#accept a client
	def listen(self):

		self.seqNumber = randint(0, pow(2,32) - 1)
		self.seqNumber = 20
		self.expectedSeq = 0
		self.socket.settimeout(None)
		self.states["Accepting"] = True

	def close(self):


		if self.states["Connected"]:

			header = self._createPacket("FIN", None)

			# set timeout so that it will keep trying to send FIN
			self.socket.settimeout(1)

			# keep sending FIN until responds
			goodRes = False
			while not goodRes:
				try:
					if self.d: print "Repeat sending FIN to", self.hostAddress, self.emuPort
					self.socket.sendto(header, (self.hostAddress, self.emuPort))


					data, addrs = self._recvAndAckNum(PACKETSIZE)
					rcvHeader, rcvData = self._decodeHeader(data)
					if self.d: print "Recevied data from server"

					# check for corruption
					if not self._checkChecksum(rcvHeader["checksum"],data):
						if self.d: print "packet corrupted"
						continue
					# check for fin flag

					if rcvHeader["flags"] == 0b001:
						if self.d: print "Flag is FIN"
						goodRes = True
					else:
						if self.d: print "Flag is NOT FIN"
						continue


					self.nextSeqNumber = rcvHeader["seqNum"] + 1

				except socket.timeout:
					continue
			header = self._createPacket("ACK", None)
			self.socket.sendto(header, (self.hostAddress, self.emuPort))

			if self.d: print "Sending ACK, FIN complete"

			self.states["Connected"] = False

			return True
		else:
			print "Server not connected"
			return False



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

