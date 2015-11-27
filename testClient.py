__author__ = 'jli'

from RxpSocket import RxpSocket
from RxpServerSocket import RxpServerSocket
import sys
import time


def main():

	print "hello client starting"

	fxaPort = int(sys.argv[1])
	emuIp = sys.argv[2]
	emuPort = int(sys.argv[3])

	debug = False
	if len(sys.argv) == 5:
		debug = True



	s = RxpSocket(debug)
	s.bind(emuIp, emuPort, fxaPort)
	s.connect()

	# s.send("SEND DATA")
	# print "reading file"
	# readFile = open("Alice.txt", "rb")
	# nextData = readFile.read()
	# s.send(nextData)

	s.send("NEED DATA")
	s.recv(3000)


	s.send("NEED DATA")
	s.recv(3000)
	s.recv(3000)
	s.send("asdf")

	s.send("HELLo")
	res = s.recv(3000)
	print res
	s.send("WORLD")
	res = s.recv(3000)
	print res

if __name__ == "__main__":
	main()
