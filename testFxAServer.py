__author__ = 'alier'

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
	while not s.accept():
		pass

	#test post
	foo = s.recv(2000)
	msg = foo.split(" ")
	if msg[0] == "pr":
		print "post request"
		foo = "p /.END"
		s.send(foo)
		foo= s.recv(3000)
		msg = foo.split(" ")
		if msg[0] == "pm":
			s.send("pcompleted/.END")

	#test get
	# foo = s.recv(2000)
	# msg = foo.split(" ")
	# if msg[0] == "gr":
	# 	print "get request"
	# 	foo = "gcompleted"+"file"+"\.END"
	# 	s.send(foo)

if __name__ == "__main__":
	main()