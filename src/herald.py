#!/usr/bin/python3

import socket
import select
import string
import sys
import threading
import json
from collections import deque

testQ = deque([])
qlock = threading.Condition()
testers = []
tlock = threading.Condition()

rePorts = []
killPorts = []
running = True
#k for kill, c for recieve, s for sends
k = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);
c = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);
r = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);
s = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);

class dispenserThread (threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
  def run(self):
    while True:
      qlock.acquire()
      while True:
        l = len(testQ)
        if(l > 0):
          break
        qlock.wait()
      sub_ID = testQ.popleft()
      qlock.release()
      tester = -1
      tlock.acquire()
      while True:
        try:
          tester = testers.index(0)
        if(tester > -1)
          break
        tlock.wait()
      testers[tester] = int(sub_ID)
      tlock.release()
      s.connect('\0recvPort' + tester)
      s.send('{"sub_ID":' + sub_ID + '}'.encode())
      s.close()
      

def init():
  for i in range(sys.argv[1])
    try:
      #clean out old processes
      k.connect('\0killPort' + i)
      k.send('{"state":"die"}')
      k.close()
      print('Closed existing testing process. Either port conflict, or improper shutdown.')
    rePorts.append(socket.socket(socket.AF_UNIX,socket.SOCK_STREAM))
    rePorts[i].bind('\0rePort' + str(i))
    rePorts[i].listen(1)
    testers.append(0)
    dthread = dispenserThread()
    dthread.start()

c.bind("\0recvPort")
k.bind("\0killPort")
c.listen(10)
k.listen(1)
while running:
	readlist,writelist,exceptlist = select.select([c,k,r],[],[])
	for avail in readlist:
		if avail is c:
			h = c.accept()[0]
			msg = h.recv(256)
			h.close()
      dmsg = msg.decode()
      sub_ID = json.loads(dmsg)["sub_ID"]
      
      #TESTING LINE
      sub_ID = 83
      
      qlock.acquire()
      testQ.append(sub_ID)
      qlock.release()
      dlock.notify()
		elif avail is k:
			print("Recieved kill signal")
			remv = k.accept()[0]
			for j in range(sys.argv[1]):
				o = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);
				o.connect('\0killPort' + j)
				o.send('{"state":"die"}'.encode())
				o.close()
			k.close()
			exit()
		elif avail is r:
			s = r.accept()[0]
			msg = s.recv(256)
      dmsg = msg.decode()
      sub_ID = json.loads(dmsg)["sub_ID"]
      tlock.acquire()
      try:
        idx = testers.index(int(sub_ID))
        testers[idx] = 0
      except ValueError:
        print("Error: a test was reported completed, but no record of it being started.")
			s.close