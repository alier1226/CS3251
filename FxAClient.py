__author__ = 'alier'

from RxpSocket import RxpSocket
from RxpServerSocket import RxpServerSocket
import sys
import time
import os


HEADERSIZE = 131
DATASIZE = 5000
PACKETSIZE = HEADERSIZE + DATASIZE


def main():
	FXAPORT = 5000
	EMUIP = 8080
	EMUPORT = 'localhost'
	STATE = 'welcome'
	DEBUG = False
	s = RxpSocket(DEBUG)

	while(1):
		#set up for connect
		if(STATE == 'welcome'):
			if(len(sys.argv)<4):
				print "invalid command"
				break
			try:
				FXAPORT = int(sys.argv[1])
			except:
				print "invalid command"

			if FXAPORT%2 != 0:
				print "Please enter a valid port number that the socket should bind to (must be even)"
				print "set to default 8080"
			EMUIP = sys.argv[2]
			EMUPORT = int(sys.argv[3])
			if len(sys.argv) > 4:
				if ((sys.argv[4] == 'd') or (sys.argv[4] == 'D')):
					DEBUG = True
				else:
					print "Invalid debug command"
			command = raw_input("Welcome. Please enter a command: ")
			if command == 'connect':
				s = RxpSocket(DEBUG)
				s.bind(EMUIP, EMUPORT, FXAPORT)
				if not s.connect():
					#this is currently wrong. It should print this when connect fails
					print "can't connect to the server"
					break
				STATE = 'connect'
			else:
				print('type connect to establish connection')

		#establish connect
		if(STATE == 'connect'):
			command = raw_input("It is connected to the server. Please enter a command: ")
			if command == 'disconnect':
				s.close()
				STATE = 'disconnect'
			else:
				temp = command.split(' ')
				if(len(temp) == 2):
					if temp[0] == 'get':
						STATE = 'get'
					elif temp[0] == 'post':
						STATE = 'post'
					elif temp[0] == 'window':
						STATE = 'window'
					else:
						print'Invalid command. (get F, post F, window W or disconnect)'
				else:
					print'Invalid command. (get F, post F, window W or disconnect)'
		if(STATE == 'post'):
			print("post file")
			groupedPackets = createPackets(temp[1])
			s.send(groupedPackets)
		if(STATE == 'get'):
			print('get file')
		if(STATE == 'Window'):
			print('window size')
		if(STATE == 'disconnect'):
			print('disconnect')
		print "main loop done, repeating"
		time.sleep(100)

def createPackets(fileName):
		# check if file exists
		if(not os.path.isfile(fileName)):
			print "This file does not exist"
			return False
		print "File", fileName, "found"

		packetData = []

		readFile = open(fileName, "rb")
		nextData = readFile.read(DATASIZE)

		# read all the data from a file and break into groups
		while(nextData):
			packetData.append(nextData)
			nextData = readFile.read(DATASIZE)
		readFile.close()

		return packetData


main()


