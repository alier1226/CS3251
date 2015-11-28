* Your team member names and email addresses

Jingyuan Hu, djyhu@gatech.edu

Jack Li, jli439@gatech.edu

* Class name, section, date and assignment title

CS 3251, Section A, Programming Assignment 2, Nov 28

* Names and descriptions of all files submitted

FxAClient.py : Client side of file transfer application

FxAServer.py : Server side of file transfer application

RxPServerSocket.py: Server socket

RxPSocket.py:Reliable transport protocol socket

NetEmu: simulator provided by professors


* Detailed instructions for compiling and running your client and server programs
Your updated protocol and API description with sufficient detail such that somebody else could implement your protocol

You will need three consoles to run the program.

Go to the folder and

1. in the first console: python NetEmu.py 5000

2. in the second console: python FxAServer.py 8081 localhost 5000

3. in the third console: python FxAClient.py 8080 localhost 5000

4. add -D or -d at the end of command to switch to debug mode

5. On client side, there are several commands: connect, get F, post F, window W, and disconnect. Follow the instructions printed on console.

6. On server side, you can type window W and terminate at any time. Follow the instructions printed on console.


* Any known bugs, limitations of your design or program

1. Cannot handle multiple clients

2. 

* You can read our documentation on https://docs.google.com/document/d/1yfl6SzNZw_GZuktf727YjCzSV7xYUU4iiTpC4nhiLWM/edit?usp=sharing
