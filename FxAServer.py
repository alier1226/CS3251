__author__ = 'alier'

from RxpSocket import RxpSocket
from RxpServerSocket import RxpServerSocket
import sys

class fxaserver:
    def main(self):
        FXAPORT = 5000
        EMUIP = 8081
        EMUPORT = 'localhost'
        STATE = 'welcome'
        DEBUG = False
        s = RxpServerSocket(DEBUG)
        while(1):
            if(STATE == 'welcome'):
                if(len(sys.argv)<4):
                    print "invalid command"
                    break
                try:
                    FXAPORT = int(sys.argv[1])
                except:
                    print "invalid command"

                if FXAPORT%2 != 1:
                    print "Please enter a valid port number that the socket should bind to (must be even)"
                    print "set to default 8081"
                EMUIP = sys.argv[2]
                EMUPORT = int(sys.argv[3])
                if len(sys.argv) > 4:
                    if ((sys.argv[4] == 'd') or (sys.argv[4] == 'D')):
                        DEBUG = True
                    else:
                        print "Invalid debug command"
                s = RxpServerSocket(DEBUG)
                s.bind(EMUIP, EMUPORT, FXAPORT)
                while not s.states["Connected"]:
                    s.accept()
                    if not s.states["Connected"]:
                        print "FxA: Connection not established, trying again"

                while True:
                    res = s.listen()
                    if res == "post":
                        s.recv()
                    print "next"
                    return
server = fxaserver()
server.main()