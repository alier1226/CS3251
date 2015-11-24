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

	while not s.states["Connected"]:
		s.listen(5)




if __name__ == "__main__":
	main()