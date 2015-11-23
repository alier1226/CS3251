__author__ = 'jli'
import socket
import md5


class RxpSocket(object):
	def __init__(self, debug):

		self.d = debug

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.value = 9
		self.timeout = 0
		self.windowSize = 0
		self.packetSize = 2000
		self.rcvWindow = 10000
		self.seqNumber = 0
		self.ackNumber = 0

		self.portNumber = None
		self.hostAddress = None
		self.emuPort = None

		self.states = {
			"Connected": False
		}



		#self.socket.settimeout(1)

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
		self.socket.settimeout = value

	# set the window size
	def setWindowSize(self, value):
		self.windowSize = value

	def connect(self, addrs, emuPort, portNumber):

		if not self.states["Connected"]:

			# update variables
			self.portNumber = portNumber
			self.hostAddress = addrs
			self.emuPort = emuPort

			# bind to port
			if self.d: print "Binding server to port", portNumber
			self.socket.bind( ('', self.portNumber) )

			# creating header for SYN packet
			header = self._createPacketHeader("SYN")
			self.socket.settimeout(1)

			# keep sending SYN until server responds
			goodRes = False
			while not goodRes:
				try:
					if self.d: print "Repeat sending SYN to", self.hostAddress, self.emuPort
					self.socket.sendto(header, (self.hostAddress, self.emuPort))

					data, addrs = self.socket.recvfrom(1000)
					rcvHeader = self._decodeHeader(data)
					if self.d: print "Recevied data from server"

					# check for header corruption
					if not self._checkChecksum(rcvHeader["checksum"],data):
						if self.d: print "rcvHeader corrupted"
						continue


					# check for SYNACK flag
					if rcvHeader["flags"] == 0b110:
						if self.d: print "Flag is SYNACK"

						goodRes = True


				except socket.timeout:
					continue

			header = self._createPacketHeader("ACK")
			if self.d: print "Sending ACK to", self.hostAddress, self.emuPort, "handshake complete"
			self.socket.sendto(header, (self.hostAddress, self.emuPort))
			self.states["Connected"] = True
		else:
			print "Already connected"
			return False



	#Private Functions



	def _createPacketHeader(self, data):
		if data == "SYN":
			flags = "100"
		elif data == "ACK":
			flags = "010"
		elif data == "SYNACK":
			flags = "110"
		elif data == "FIN":
			flags = "001"
		else:
			flags = "000"

		header = "" + self._create16bit(self.portNumber)
		header = header + self._create16bit(self.emuPort)
		header = header + self._create32bit(self.seqNumber)
		header = header + self._create32bit(self.ackNumber)
		header = header + self._create16bit(self.rcvWindow)
		header = header + flags
		header = header + self._calculateChecksum(header)

		return header

	def _create16bit(self, value):
		if value > pow(2, 16):
			print "Can't create 16 bits from ", value, "too big"
			return
		else:
			return bin(value)[2:].zfill(16)

	def _create32bit(self, value):
		if value > pow(2, 32):
			print "Can't create 16 bits from ", value, "too big"
			return
		else:
			return bin(value)[2:].zfill(32)

	def _add16Bit(self, num1,num2):
		MOD = 1 << 16
		result = num1 + num2
		if result < MOD:
			return result
		else:
			return (result+1) % MOD

	def _calculateChecksum(self, value):

		# split the value into groups of 16
		split = [ int(value[i:i+16],2) for i in range(0, len(value), 16)]

		# add the groups together
		checksum = 0
		for value in split:
			checksum = self._add16Bit(checksum, value)
		return bin(checksum)[2:].zfill(16)

	def _checkChecksum(self, oldChecksum, newData):

		# check if header is corrupted
		newChecksum = self._calculateChecksum(newData[0:len(newData) - 16])
		newChecksum = int(newChecksum,2)
		if oldChecksum == newChecksum:
			return True
		return False

	def _decodeHeader(self, data):

		sourcePort = int(data[0:16],2)
		destPort = int(data[16:32],2)
		seqNum = int(data[32:64],2)
		ackNum = int(data[64:96],2)
		rcvWindow = int(data[96:112],2)
		flags = int(data[112:115],2)
		checksum = int(data[115:131],2)

		header = {
			"sourcePort": sourcePort,
			"destPort":destPort,
			"seqNum":seqNum,
			"ackNum":ackNum,
			"rcvWindow":rcvWindow,
			"flags":flags,
			"checksum":checksum
		}

		return header