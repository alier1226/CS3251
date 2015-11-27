__author__ = 'alier'

from RxpSocket import RxpSocket
from RxpServerSocket import RxpServerSocket
import sys

class fxaserver:

    def __init__(self):
        self.FXAPORT = 5000
        self.EMUIP = 8081
        self.EMUPORT = 'localhost'
        self.STATE = 'welcome'
        self.DEBUG = False
        self.s = RxpServerSocket(self.DEBUG)
        self.msg = ''
        self.data =''
        self.MAXTIMEOUT = 3
    def main(self):
        while(1):
            if(self.STATE == 'welcome'):
                if(len(sys.argv)<4):
                    print "invalid command"
                    break
                try:
                    self.FXAPORT = int(sys.argv[1])
                except:
                    print "invalid command"

                if self.FXAPORT%2 != 1:
                    print "Please enter a valid port number that the socket should bind to (must be even)"
                    print "set to default 8081"
                self.EMUIP = sys.argv[2]
                self.EMUPORT = int(sys.argv[3])
                if len(sys.argv) > 4:
                    if ((sys.argv[4] == 'd') or (sys.argv[4] == 'D')):
                        self.DEBUG = True
                    else:
                        print "Invalid debug command"
                self.s = RxpServerSocket(self.DEBUG)
                self.s.bind(self.EMUIP, self.EMUPORT, self.FXAPORT)
                # self.s.listen()

                while not self.s.states["Connected"]:
                    self.s.accept()
                    if not self.s.states["Connected"]:
                        command = raw_input("Welcome. Connection is not established. Please type command:")
                        if command == 'terminate':
                            self.STATE = 'terminate'
                        else:
                            self.msg = command.split(" ")
                            if self.msg[0] == 'window':
                                try:
                                    self.s.setWindowSize(int (self.msg[1]))
                                    self.STATE = 'window'
                                except Exception,e:
                                    print"can't change window size" + e
            if(self.STATE == 'window'):
                print('window size has been set to '+ str(self.s.windowSize))
                self.STATE = 'welcome'
            if(self.STATE == 'terminate'):
                print "terminate server"
                #TODO: close client socket
                self.s.close()

server = fxaserver()
server.main()