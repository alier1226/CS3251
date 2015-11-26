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

	print "reading file"
	readFile = open("Alice.txt", "rb")
	nextData = readFile.read()

	time.sleep(1)
	s.send("SENDING DATA")

	time.sleep(1)
	s.send(nextData)

if __name__ == "__main__":
	main()
