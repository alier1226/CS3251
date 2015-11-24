__author__ = 'jli'

from RxpSocket import RxpSocket
from RxpServerSocket import RxpServerSocket
import sys

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

	#s.send("AliceChpt1.txt")

if __name__ == "__main__":
	main()
