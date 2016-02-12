#!/usr/local/bin/python3.2

import socket
import select
import string
import sys
import subprocess
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
    print('Dispenser thread running')
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
        except Exception:
          pass
        if(tester > -1):
          break
        tlock.wait()
      testers[tester] = int(sub_ID)
      tlock.release()
      s.connect('\0recvPort' + str(tester))
      msg = '{"sub_ID":' + str(sub_ID) + '}'
      s.send(msg.encode())
      s.close()
      

def init():
  for i in range(int(sys.argv[1])):
    try:
      #clean out old processes
      k.connect('\0killPort' + str(i))
      k.send('{"state":"die"}')
      k.close()
      print('Closed existing testing process. Either port conflict, or improper shutdown.')
    except Exception:
      pass
    rePorts.append(socket.socket(socket.AF_UNIX,socket.SOCK_STREAM))
    rePorts[i].bind('\0rePort' + str(i))
    rePorts[i].listen(1)
    testers.append(0)
    subprocess.Popen(['./tester.py',str(i)])
  dthread = dispenserThread()
  dthread.daemon = True
  dthread.start()

c.bind("\0recvPort")
k.bind("\0killPort")
r.bind("\0rePort")
c.listen(10)
k.listen(1)
r.listen(int(sys.argv[1]))
init()
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
      qlock.notify()
      qlock.release()
    elif avail is k:
      print("Herald recieved kill signal")
      remv = k.accept()[0]
      for j in range(int(sys.argv[1])):
        o = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);
        o.connect('\0killPort' + str(j))
        o.send('{"state":"die"}'.encode())
        o.close()
      k.close()
      exit()
    elif avail is r:
      rec = r.accept()[0]
      msg = rec.recv(256)
      dmsg = msg.decode()
      sub_ID = json.loads(dmsg)["sub_ID"]
      tlock.acquire()
      try:
        idx = testers.index(int(sub_ID))
        testers[idx] = 0
        print('Submission evaluated.')
      except ValueError:
        print("Error: a test was reported completed, but no record of it being started.")
      tlock.notify()
      tlock.release()
      rec.close