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
	msg = ''

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
				msg = command.split(' ')
				if(len(msg) == 2):
					if msg[0] == 'get':
						STATE = 'get'
					elif msg[0] == 'post':
						STATE = 'post'
					elif msg[0] == 'window':
						s.setWindowSize(int (msg[1]))
						STATE = 'window'
					else:
						print'Invalid command. (get F, post F, window W or disconnect)'
				else:
					print'Invalid command. (get F, post F, window W or disconnect)'
		if(STATE == 'post'):
			print("post file: " + str(msg[1]))
			if(not os.path.isfile(str(msg[1]))):
				print "This file does not exist"
				STATE == 'welcome'
			print "File", str(msg[1]), "found"
			readFile = open(str(msg[1]), "rb")
		if(STATE == 'get'):
			print('get file' + str(msg[1]))
		if(STATE == 'window'):
			print('window size has been set to '+ str(s.windowSize))
			STATE = 'connect'
		if(STATE == 'disconnect'):
			print('disconnect')
			s.close()



main()


