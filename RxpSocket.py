__author__ = 'jli'
import socket
import md5
import os
from random import randint


class RxpSocket(object):
	def __init__(self, debug):

		self.d = debug

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.timeout = 0
		self.windowSize = 1
		self.rcvWindow = 10000
		self.packetSize = 3000
		self.seqNumber = 0
		self.ackNumber = 0

		self.portNumber = None
		self.hostAddress = None
		self.emuPort = None

		self.states = {
			"Connected": False
		}


	# close connection
	def close(self):
		return

	# receive from server
	def recv(self, bufsize):
		return

	# send data
	def send(self, fileName):

		# check if file exists
		if(not os.path.isfile(fileName)):
			print "This file does not exist"
		if self.d: print "File", fileName, "found"

		# tell other server that its sending a file
		goodRes = False
		while not goodRes:
			try:
				if self.d: print  "Telling server its about to send a file"
			except socket.timeout:
				continue


		packets = []

		readFile = open(fileName, "rb")
		nextData = readFile.read(self.packetSize)

		while(nextData):
			packets.append(nextData)
			nextData = readFile.read(self.packetSize)

		readFile.close()

		print "hello"
	# set the timeout value
	def setTimeout(self, value):
		self.socket.settimeout = value

	# set the window size
	def setWindowSize(self, value):
		self.windowSize = value

	#bind socket to port number
	def bind(self, emuIp, emuPort, portNumber):
		if self.d: print "Binding to port", portNumber
		self.socket.bind( ('', portNumber) )
		self.emuPort = emuPort
		self.portNumber = portNumber
		self.hostAddress = emuIp

	def connect(self):

		if not self.states["Connected"]:

			# generate random sequence number
			self.seqNumber = randint(0, pow(2,32) - 1)

			# creating header for SYN packet
			header = self._createPacketHeader("SYN", None)

			# set timeout so that it will keep trying to send SYN
			self.socket.settimeout(1)

			# keep sending SYN until server responds
			goodRes = False
			while not goodRes:
				try:
					if self.d: print "Repeat sending SYN to", self.hostAddress, self.emuPort
					self.socket.sendto(header, (self.hostAddress, self.emuPort))


					data, addrs = self.socket.recvfrom(self.packetSize)
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

			header = self._createPacketHeader("ACK", None)
			if self.d: print "Sending ACK to", self.hostAddress, self.emuPort, "handshake complete"
			self.socket.sendto(header, (self.hostAddress, self.emuPort))
			self.states["Connected"] = True
		else:
			print "Already connected"
			return False



#########Private Functions###########

	def _createPacketHeader(self, flag, data):

		# check for flags
		if flag == "SYN":
			flags = "100"
		elif flag == "ACK":
			flags = "010"
		elif flag == "SYNACK":
			flags = "110"
		elif flag == "FIN":
			flags = "001"
		else:
			flags = "000"

		# if theres no data, make it an empty string
		if not data:
			data = ""


		if self.d: print "\t HEADER INFO FOR:", flag, data

		# combine all the header information
		header = "" + self._create16bit(self.portNumber)
		if self.d: print "\t portNumber:", self.portNumber

		header = header + self._create16bit(self.emuPort)
		if self.d: print "\t emuPort:", self.emuPort

		header = header + self._create32bit(self.seqNumber)
		if self.d: print "\t seqNumber:", self.seqNumber

		header = header + self._create32bit(self.ackNumber)
		if self.d: print "\t ackNumber:", self.ackNumber

		header = header + self._create16bit(self.rcvWindow)
		if self.d: print "\t rcvWindow:", self.rcvWindow

		header = header + flags
		if self.d: print "\t flags:", flags

		header = header + self._calculateChecksum(header + data)
		if self.d: print "\t checkSum:", int(self._calculateChecksum(header + data),2)

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

		# split the value into groups of 16bit
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

		if self.d: print "Old checksum", oldChecksum, "does not match calculated checksum", newChecksum
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

