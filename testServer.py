__author__ = 'jli'

from RxpSocket import RxpSocket
from RxpServerSocket import RxpServerSocket
import sys

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

	newSocket = None
	while not newSocket:
		newSocket, addrs = s.accept()
		if not newSocket:
			print "FxA: Connection not established"

	# listen for next commands
	good = False
	while not good:

		good = newSocket.listen()


if __name__ == "__main__":
	main()