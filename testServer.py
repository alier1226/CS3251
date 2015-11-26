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

	newSocket = None
	while not s.accept():
		pass

	foo = s.recv(3000)
	if foo == "SENDING DATA":
		print "Client is sending data"
		d = s.recv(3000)

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