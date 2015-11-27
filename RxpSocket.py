__author__ = 'jli'
import socket
import md5
import os
from random import randint
import time
import thread
import threading


MAXSEQNUM = pow(2,32) - 1
HEADERSIZE = 131
DATASIZE = 300
PACKETSIZE = HEADERSIZE + DATASIZE + 16


class RxpSocket(object):
	def __init__(self, debug):

		self.d = debug

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.timeout = 0
		self.rcvWindow = 9000
		self.windowSize = 3
		self.ackNumber = 0

		self.seqNumber = randint(0, pow(2,32) - 1)
		self.seqNumber = 10

		self.nextSeqNumber = self.seqNumber

		self.seqNumArr = []

		self.prevData = 0

		self.portNumber = 0
		self.hostAddress = 0
		self.emuPort = 0



		self.states = {
			"Connected": False,
			"Accepting": False

		}


	# close connection
	def close(self):
		return

	# receive from server
	def recv(self, bufsize):
		if self.d: print "Ready to receive file"

		realData = []
		bufferLeft = bufsize

		rcvData = ""
		finishedAll = False

		while not finishedAll:

			windowData = []
			windowError = False
			windowEnd = False
			waitTillFirst = True
			self.seqNumArr = []
			firstLoop = True

			while not windowEnd:
				try:
					if waitTillFirst:
						self.socket.settimeout(None)
						waitTillFirst = False
					else: self.socket.settimeout(1)
					data, addrs = self._recvAndAckNum(PACKETSIZE)
					rcvHeader, rcvData = self._decodeHeader(data)
					self.prevData = data

					if self.d: print "received data", rcvHeader["seqNum"], "next seq", self.nextSeqNumber
					self.seqNumArr.append(rcvHeader["seqNum"])



					#check for corruption
					if not self._checkChecksum(rcvHeader["checksum"],data[:-len(rcvData)]):
						if self.d: print "packet corrupted"
						windowError =True

					# check if first packet has the correct seq number
					if firstLoop:
						if self.nextSeqNumber != rcvHeader["seqNum"]:
							if self.d: print "next seqNum is not correct", self.nextSeqNumber, rcvHeader["seqNum"]
							windowError = True



					# check for end of window
					if (len(rcvData) > 5 and rcvData[-5:] == ":END:") :
						if self.d: print "End of window detected"
						windowEnd = True

					#if this is the last packet in the window, don't include the end pointer
					if windowEnd:
						windowData.append(rcvData[:-5])
					else:
						windowData.append(rcvData)

					# check if packets are in the right order
					if windowEnd:
						if len(self.seqNumArr) > 1:
							if self.d: print "seqNumArr", self.seqNumArr
							for i in range (0, len(self.seqNumArr) - 1):
								if self.seqNumArr[i] + 1 != self.seqNumArr[i + 1]:
									if self.d: print "Out of order packets", self.seqNumArr[i] + 1, self.seqNumArr[i + 1]
									windowError = True
									break


					bufferLeft -= len(rcvData)
					self.rcvWindow = bufferLeft
					if self.rcvWindow < 0:
						self.rcvWindow = 12
					#if self.d: print "remaining buffer space:",bufferLeft

				except socket.timeout:
					if self.d: print "Did not receive data from client"
					windowError =True

				# if finished and no error, send ACK
				# if finished and error, dont send ack, delete data, set error to false
				if not windowError and windowEnd:
					if self.d: print "Received all of window, acknowledging"
					if self.d: print "self seqNumARr", self.seqNumArr, "ack", self.ackNumber

					self.nextSeqNumber = self.ackNumber

					header = self._createPacket("ACK", None)
					self.socket.sendto(header, (self.hostAddress, self.emuPort))
					break
				elif windowError:
					if self.d: print "Error in sending window"
					windowError = False
					windowData = []
					windowEnd = False
					waitTillFirst = True
					firstLoop = True

					self.seqNumArr = []

					continue
				firstLoop = False

			realData.extend(windowData)

			if (len(rcvData) > 16 and rcvData[-16:] == "::ENDFILE:::END:") and not windowError:
				if self.d: print "End of file"
				finishedAll = True

		# remove endfile pointer
		realData = "".join(realData)
		realData = realData[:-11]

		foo = open("foo.txt", "w+")
		foo.write(realData)
		foo.close()

		return realData

	# send data
	def send(self, data):

		realData = data + "::ENDFILE::"

		dataIndex = 0

		# listen to server
		#threadListen = ThreadingExample(self)
		self.socket.settimeout(1)
		if self.d: print "starting"
		while dataIndex < len(realData):
			if self.d: print "Next window group"

			# make first window of packets
			windowData = realData[dataIndex:(self.windowSize * DATASIZE) + dataIndex]

			packetData = []
			for i in range(0, len(windowData), DATASIZE):
				packetData.append(windowData[i:i+DATASIZE])

			dataIndex += (self.windowSize * DATASIZE)


			# attach header
			fullPacketArr = []
			endIndex = 1
			for pData in packetData:
				if endIndex % self.windowSize == 0 or packetData.index(pData) == len(packetData) - 1:
					fullPacketArr.append(self._createPacket("", pData + ":END:"))
				else:
					fullPacketArr.append(self._createPacket("", pData))
				endIndex += 1

			nextGroup = fullPacketArr

			packetsAcked = False
			while not packetsAcked:

				# if no ACK, resend
				for packet in nextGroup:
					#time.sleep(.1)
					if self.d: print "\tsending packet"

					self.socket.sendto(packet, (self.hostAddress, self.emuPort))

				try:
					if self.d: print "now waiting for ACK"
					data, addrs = self._recvAndAckNum(PACKETSIZE)
					rcvHeader, rcvData = self._decodeHeader(data)

					# check for corruption
					if not self._checkChecksum(rcvHeader["checksum"],data):
						if self.d: print "packet corrupted"
						continue

					# check for ACK flag
					if not rcvHeader["flags"] == 0b010:
						if self.d: print "Flag is NOT an ACK"
						continue
					else:
						if self.d: print "Flag is an ACK"
						packetsAcked = True

				except socket.timeout:
					if self.d: print "No ACK recevied"
					continue

		return

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
					self.nextSeqNumber = rcvHeader["seqNum"] + 2


					# check for SYNACK flag
					if rcvHeader["flags"] == 0b110:
						if self.d: print "Flag is SYNACK"
						goodRes = True

				except socket.timeout:
					continue
				header = self._createPacket("ACK", None)
				self.socket.sendto(header, (self.hostAddress, self.emuPort))
			# set server rcvWindow
			# ackDone = False
			# while not ackDone:
			#
			# 	header = self._createPacket("ACK", None)
			# 	self.socket.sendto(header, (self.hostAddress, self.emuPort))
			#
			# 	if self.d: print "Sending ACK to", self.hostAddress, self.emuPort
			#
			# 	# check if server is still sending info => no ack received
			# 	try:
			# 		self.socket.settimeout(1)
			# 		data, addrs = self._recvAndAckNum(PACKETSIZE)
			# 		rcvHeader, rcvData = self._decodeHeader(data)
			#
			# 		if rcvHeader["flags"] == 0b110:
			# 			if self.d: print "ACK not received, trying again"
			#
			# 	except socket.timeout:
			# 		if self.d: print "ACK was received"
			# 		ackDone = True





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

		if self.d:
			if len(data) > 30:
				print "HEADER INFO FOR:", flag, data[:30]
			else:
				print "HEADER INFO FOR:", flag, data

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

		if self.d: print "\t data size:", len(data)

		# calculate sequence number
		# if len(data) > 0:
		# 	self.seqNumber = self.seqNumber + len(data)
		# elif flag == "ACK":
		# 	self.seqNumber = self.seqNumber
		# else:
		# 	self.seqNumber += 1

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
		#split = [ int(value[i:i+16],2) for i in range(0, len(value), 16)]
		split = []

		for i in range(0, len(value), 16):
			#print value[i:i+16] + "\n"
			split.append(int(value[i:i+16],2))

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

	# receive data and calculate next ack number
	def _recvAndAckNum(self, size):

		data, addrs = self.socket.recvfrom(size)
		seqNum = int(data[32:64],2)

		# if len(data) > HEADERSIZE:
		# 	self.ackNumber = seqNum + len(data) - HEADERSIZE
		# else:
		# 	self.ackNumber = seqNum + 1
		#
		# if self.ackNumber > MAXSEQNUM:
		# 	self.ackNumber = self.ackNumber - MAXSEQNUM

		self.ackNumber = seqNum + 1

		return data, addrs

	# #TODO: create packets.
	# def createPackets(data):
	# 	# read all the data from a file and break into groups
	# 	# while(nextData):
	# 	# 	packetData.append(nextData)
	# 	# 	nextData = readFile.read(DATASIZE)
	# 	# readFile.close()
	# 	#
	# 	# return packetData
	# 	return