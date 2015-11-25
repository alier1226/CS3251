__author__ = 'jli'
import socket
import md5
import os
from random import randint


MAXSEQNUM = pow(2,32) - 1
HEADERSIZE = 131
PACKETSIZE = HEADERSIZE + 3000

class RxpSocket(object):
	def __init__(self, debug):

		self.d = debug

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.timeout = 0
		self.windowSize = 1
		self.rcvWindow = 10000
		self.ackNumber = 0
		self.seqNumber = randint(0, pow(2,32) - 1)
		self.nextSeqNumber = self.seqNumber

		self.portNumber = 0
		self.hostAddress = 0
		self.emuPort = 0

		# generate random sequence number

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

		# tell server that its sending a file
		goodRes = False
		self.socket.settimeout(1)
		header = self._createPacket(000, "GET")
		while not goodRes:
			try:
				if self.d: print  "Repeat telling server its going to send a file"
				self.socket.sendto(header, (self.hostAddress, self.emuPort))

				data, addrs = self._recvAndAckNum(PACKETSIZE)
				rcvHeader, rcvData = self._decodeHeader(data)
				if self.d: print  "Received data from server"


				# check for corruption
				if not self._checkChecksum(rcvHeader["checksum"],data):
					if self.d: print "packet corrupted"
					continue

				print rcvHeader
				if rcvHeader["flags"] == 0b010:
					goodRes = True
					if self.d: print "flag is ACK"


			except socket.timeout:
				continue


		packets = []

		readFile = open(fileName, "rb")
		nextData = readFile.read(PACKETSIZE)

		while(nextData):
			packets.append(nextData)
			nextData = readFile.read(PACKETSIZE)

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



			# creating header for SYN packet
			header = self._createPacket("SYN", None)

			# set timeout so that it will keep trying to send SYN
			self.socket.settimeout(1)

			# keep sending SYN until server responds
			goodRes = False
			while not goodRes:
				try:
					if self.d: print "Repeat sending SYN to", self.hostAddress, self.emuPort
					self.socket.sendto(header, (self.hostAddress, self.emuPort))
					#self._sendAndSeqNum(header, (self.hostAddress, self.emuPort))


					data, addrs = self._recvAndAckNum(PACKETSIZE)
					rcvHeader, rcvData = self._decodeHeader(data)
					if self.d: print "Recevied data from server"

					# check for corruption
					if not self._checkChecksum(rcvHeader["checksum"],data):
						if self.d: print "packet corrupted"
						continue


					# check for SYNACK flag
					if rcvHeader["flags"] == 0b110:
						if self.d: print "Flag is SYNACK"

						goodRes = True

				except socket.timeout:
					continue


			header = self._createPacket("ACK", None)
			if self.d: print "Sending ACK to", self.hostAddress, self.emuPort, "handshake complete"
			self.socket.sendto(header, (self.hostAddress, self.emuPort))
			self.states["Connected"] = True
			return True
		else:
			print "Already connected"
			return False



#########Private Functions###########

	def _createPacket(self, flag, data):

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

		header = header + self._calculateChecksum(header)
		if self.d: print "\t checkSum:", int(self._calculateChecksum(header),2)

		# calculate sequence number
		if len(data) > 0:
			self.seqNumber = self.seqNumber + len(data)
		elif flag == "ACK":
			self.seqNumber = self.seqNumber
		else:
			self.seqNumber += 1
		# wrap sequence number if it goes past max value
		if self.seqNumber > MAXSEQNUM:
			self.seqNumber = self.seqNumber - MAXSEQNUM



		return header + data

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
		b = bin(checksum)[2:].zfill(16)
		b = b.replace('0','x')
		b = b.replace('1','0')
		b = b.replace('x','1')
		#perform 1st complement
		return b
	

	def _checkChecksum(self, oldChecksum, newData):

		# check if packet is corrupted
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
		data = data[131:]

		header = {
			"sourcePort": sourcePort,
			"destPort":destPort,
			"seqNum":seqNum,
			"ackNum":ackNum,
			"rcvWindow":rcvWindow,
			"flags":flags,
			"checksum":checksum
		}

		return header, data

	# # send data and calculate next seq number
	# def _newSeqNum(self, data):
	# 	if len(data) > HEADERSIZE:
	# 		self.seqNumber = self.seqNumber + len(data) - HEADERSIZE
	# 	else:
	# 		self.seqNumber += 1
	# 	# wrap sequence number if it goes past max value
	# 	if self.seqNumber > MAXSEQNUM:
	# 		self.seqNumber = self.seqNumber - MAXSEQNUM
	#
	# 	return

	# receive data and calculate next ack number
	def _recvAndAckNum(self, size):

		data, addrs = self.socket.recvfrom(size)
		seqNum = int(data[32:64],2)

		if len(data) > HEADERSIZE:
			self.ackNumber = seqNum + len(data) - HEADERSIZE
		else:
			self.ackNumber = seqNum + 1

		if self.ackNumber > MAXSEQNUM:
			self.ackNumber = self.ackNumber - MAXSEQNUM

		return data, addrs