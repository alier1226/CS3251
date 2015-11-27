__author__ = 'alier'

from RxpSocket import RxpSocket
from RxpServerSocket import RxpServerSocket
import sys

class fxaserver:

    def _receive(self, s):
        print "_receive function"
        timeout = 0

        while 1:

            try:
                full_msg = ''
                while 1:
                    msg = self.s.recv(2048)
                    # print(msg[-5:]+"loop msg")
                    if msg == None:
                        # print("Can't get message from server")
                        self.STATE = 'welcome'
                        return None
                    else:
                        full_msg = full_msg+msg
                        if len(full_msg)>=5 and full_msg[-5:] == "/.END":
                            # print("cant find end?????")
                            break
                if(len(full_msg)>0):
                    # print("full message here: " + full_msg[0:-5])
                    return full_msg[0:-5]
                else:
                    return None

            except Exception, e:
                print "failed to receive message. please try again later" + e
                timeout = timeout+1
                if(timeout > self.MAXTIMEOUT):
                    print "time out. please try again later"
                    return None

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
        self.command = ''
        self.postrequest = False
        self.postfile = ''
        self.getfile = ''


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
                self.s.listen()

                while not self.s.states["Connected"]:
                    try:
                        self.s.accept()
                        print("A client has connected")
                    except Exception,e:
                        print("waiting for client")

                    #client
                    while(1):
                        foo = self._receive(self.s)
                        print "received command from client: "+foo
                        if foo == None or len(foo) == 0:
                            print "command from client is none"
                        else:
                            msg = foo.split(" ")
                            print("asdfasdf"+foo + "command")
                            #if post request command
                            if msg[0] == "pr" and self.postrequest == False:
                                self.postrequest = True
                                self.postfile = msg[1]
                                print "Recieved post request from client"
                                print "The post file is "+self.postfile
                                foo = "p /.END"
                                # TODO: only for debug. delete it when send returns boolean
                                self.s.send(foo)
                                # if self.s.send(foo):
                                #     print "Send post request confirmation successfully."
                                # else:
                                #     print "Can't send post request confirmation back to client. Please try again later"

                            # if post actual file command
                            elif msg[0] == "pm" and self.postrequest == True:
                                print "Received post file from client"
                                self.postrequest = False
                                try:
                                    readFile = open(str(self.postfile), "w")
                                    self.data = foo[3:]
                                    readFile.write(self.data)
                                    readFile.close()
                                    print("downloaded "+self.postfile+" from client successfully")
                                except Exception, e:
                                    print "unable to get the file from client. Please try again later"
                                    print e

                            # if get request command
                            elif msg[0] == "gr":
                                print "Received get file request from client"
                                self.getfile = msg[1]
                                print "get file: "+ self.getfile
                                try:
                                    readFile = open(str(self.getfile),"rb")
                                    self.data = 'gcompleted'
                                    self.data += readFile.read()
                                    self.data += '/.END'
                                    # TODO: only for debug.
                                    self.s.send(self.data)
                                    # if not self.s.send(self.data):
                                    #     print "Can't send the file to client"
                                except Exception,e:
                                    print "Unable to send the file to client. Please try again later"
                                    print e
                                    self.data = 'gfailed/.END'
                                    self.s.send(self.data)


                            #not post/get command
                            else:
                                print "Unknown command from the client"




server = fxaserver()
server.main()