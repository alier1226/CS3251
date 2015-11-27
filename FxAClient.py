__author__ = 'alier'

from RxpSocket import RxpSocket
from RxpServerSocket import RxpServerSocket
import sys
import time
import os

class fxa_client:

	def __init__(self):

		self.FXAPORT = 5000
		self.EMUIP = 8080
		self.EMUPORT = 'localhost'
		self.STATE = 'welcome'
		self.DEBUG = False
		self.s = RxpSocket(self.DEBUG)
		self.msg = ''
		self.data =''
		self.MAXTIMEOUT = 3

	def _receive(self, s):

		timeout = 0

		while 1:

			try:
				full_msg = ''
				while 1:
					msg = self.s.recv(2048)
					# print(msg[-5:]+"loop msg")
					if msg == None:
						print("Can't get message from server")
						self.STATE = 'welcome'
						return None
					else:
						full_msg = full_msg+msg
						if len(full_msg)>=5 and full_msg[-5:] == "\.END":
							break
				if(len(full_msg)>0):
					# print("full message here: " + full_msg[0:-5])
					return full_msg[0:-5]
				else:
					return None

			except Exception, e:
				print "failed to receive message. please try again later" + e
				timeout = timeout+1
				if(timeout > self.MAXTIMEOUT):
					print "time out. please try again later"
					return None

	def main(self):

		while(1):

			#set up for connect
			if(self.STATE == 'welcome'):
				if(len(sys.argv)<4):
					print "invalid command"
					break
				try:
					self.FXAPORT = int(sys.argv[1])
				except:
					print "invalid command"

				if self.FXAPORT%2 != 0:
					print "Please enter a valid port number that the socket should bind to (must be even)"
					print "set to default 8080"
				self.EMUIP = sys.argv[2]
				self.EMUPORT = int(sys.argv[3])
				if len(sys.argv) > 4:
					if ((sys.argv[4] == 'd') or (sys.argv[4] == 'D')):
						self.DEBUG = True
					else:
						print "Invalid debug command"
				command = raw_input("Welcome. Type connect to establish connection: ")
				if command == 'connect':
					self.s = RxpSocket(self.DEBUG)
					self.s.bind(self.EMUIP, self.EMUPORT, self.FXAPORT)
					if not self.s.connect():
						#this is currently wrong. It should print this when connect fails
						print "can't connect to the server"
						break
					self.STATE = 'connect'
				else:
					print('type connect to establish connection')

			#establish connect
			if(self.STATE == 'connect'):
				self.msg = ''
				self.data = ''
				command = raw_input("It is connected to the server. Please enter a command: ")
				if command == 'disconnect':
					self.s.close()
					self.STATE = 'disconnect'
				else:
					self.msg = command.split(' ')
					if(len(self.msg) == 2):
						if self.msg[0] == 'get':
							self.STATE = 'get'
						elif self.msg[0] == 'post':
							self.STATE = 'post'
						elif self.msg[0] == 'window':
							try:
								self.s.setWindowSize(int (self.msg[1]))
								self.STATE = 'window'
							except Exception,e:
								print"can't change window size" + e
						else:
							print'Invalid command. (get F, post F, window W or disconnect)'
					else:
						print'Invalid command. (get F, post F, window W or disconnect)'

			#if user wants to post
			if(self.STATE == 'post'):
				print("post file: " + str(self.msg[1]) + " request")
				if(not os.path.isfile(str(self.msg[1]))):
					print "This file does not exist"
					self.STATE = 'welcome'
				self.data = "pr " + str(self.msg[1])+"/.END"
				#TODO: delete, only for debug
				self.s.send(self.data)
				# if(not self.s.send(self.data)):
				# 	print "Can't send post request"
				# 	self.STATE = 'connect'
				self.STATE = 'post_request'

			#send file to server
			if(self.STATE == 'post_request'):
				recvMsg = self._receive(self.s)
				# recvMsg = self.s.recv(2000)
				if len(recvMsg) == 0 or recvMsg == None:
					print "Did not receive anything from server. please try again later"
					self.STATE = 'connect'
				if recvMsg[0] != 'p':
					print "Can't process post request. please try again later"
					self.STATE = 'connect'
				else:
					readFile = open(str(self.msg[1]), "rb")
					self.data = 'pm '+ readFile.read()
					self.data = self.data + '/.END'
					readFile.close()
					#TODO: send() needs to return boolean
					if not self.s.send(self.data):
						print "unable to post the file, please try again later"
						self.STATE = 'connect'
					self.STATE = 'post_complete'

			#see if post is successful
			if(self.STATE == 'post_complete'):
				confirm = self._receive(self.s)
				if(confirm != 'pcompleted'):
					print "Failed to post the file, please try again later"
				print "Has posted the file succesfully"
				self.STATE = 'connect'

			#users want to get a file
			if(self.STATE == 'get'):
				print('get file' + str(self.msg[1]))
				self.data = 'gr ' + str(self.msg[1])+ '/.END'
				if not self.s.send(self.data):
					print "Can't send get file: " + str(self.msg[1]) +" request. please try again later"
					self.STATE = 'connect'
				recvMsg = self._receive(self.s)
				if len(recvMsg) == 0 or recvMsg == None:
					print "Can't download the file from the server. please try again later"
					self.STATE = 'connect'
				elif recvMsg[0:10] != "gcompleted":
					print "unable to download the file. please try again later"
				else:
					try:
						readFile = open(str(self.msg[1]), "w")
						self.data = recvMsg[10:]
						readFile.write(self.data)
						readFile.close()
						print("downloaded "+self.msg[1]+" successfully")
					except Exception, e:
						print "unable to write the file."+ e
				self.STATE = 'connect'

			#user wants to change window size
			if(self.STATE == 'window'):
				print('window size has been set to '+ str(self.s.windowSize))
				self.STATE = 'connect'

			#user wants to disconnect
			if(self.STATE == 'disconnect'):
				print('disconnect')
				self.s.close()



my_client = fxa_client()
my_client.main()


