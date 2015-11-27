__author__ = 'jli'

from RxpSocket import RxpSocket
from RxpServerSocket import RxpServerSocket
import sys
import time
def main():

	print "hello server starting"

	fxaPort = int(sys.argv[1])
	emuIp = sys.argv[2]
	emuPort = int(sys.argv[3])

	debug = False
	if len(sys.argv) == 5:
		debug = True


	s = RxpServerSocket(debug)
	s.bind(emuIp, emuPort, fxaPort)

	s.listen()

	newSocket = None
	while not newSocket:
		newSocket = s.accept()


	foo = s.recv(3000)
	s.send("data1")
	s.send("data2")
	s.recv(3000)
	# if foo == "NEED DATA":
	# 	print "Client needs data"
	# 	print "reading file"
	# 	readFile = open("Alice.txt", "rb")
	# 	nextData = readFile.read()
	# 	s.send(nextData)
	# if foo == "SEND DATA":
	# 	print "Client is sending data"
	# 	s.recv(3000)

	# foo = s.recv(3000)
	# if foo == "NEED DATA":
	# 	print "Client needs data"
	# 	print "reading file"
	# 	readFile = open("Alice.txt", "rb")
	# 	nextData = readFile.read()
	#
	# 	s.send(nextData)

	# listen for next commands
	# good = False
	# while True:
	# 	res = s.listen()
	#
	# 	if res == "post":
	# 		s.recv()
	#
	# 	time.sleep(100)

if __name__ == "__main__":
	main()