#!/usr/bin/python3
import socket
import select
import sys
import subprocess
import time
import json
import shutil
import stat
import string
import os

def query(id):
    # Nathan, I think we should work on this part together
    return {'subFile':'test/dummy.py','testFile':'test/test.py'}

def runProtected(files,sub_ID):
    #will need to be changed when we run it on the vm
    shutil.copy(files['subFile'],'tester0User')
    shutil.copy(files['testFile'],'tester0User')
    shutil.copy('interfaces/py_test_osu.py','tester0User')
    os.chdir('tester0User')
    os.chmod(files['subFile'].split('/')[-1],0o0550)
    os.chmod(files['testFile'].split('/')[-1],0o6550)
    os.chmod('py_test_osu.py',0o0440)
    print('perms set')
    subprocess.call('test.py',stdout=open('tapresult - ' + sub_ID + '.txt','w'),shell=True)
    shutil.copy('tapresult.txt','../results')
    os.unlink(files['subFile'].split('/')[-1])
    os.unlink(files['testFile'].split('/')[-1])
    os.unlink('py_test_osu.py')
    os.unlink('tapresult.txt')
    os.chdir('..')

id = sys.argv[1]
c = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);
k = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);
r = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);
c.bind("\0recvPort" + id)
print("Bound listen port \0recvPort" + id)
k.bind("\0killPort" + id)
c.listen(1)
k.listen(1)
while 1:
    readlist,writelist,exceptlist = select.select([c,k],[],[])
    for avail in readlist:
        #test branch
        if avail is c:
            h = c.accept()[0]
            msg = h.recv(256)
            h.close()
            dmsg = msg.decode()
            sub_ID = json.loads(dmsg)["sub_ID"]
            files = query(sub_ID)
            
            runProtected(files,sub_ID)
            o = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);
            o.connect('\0rePort' + id)
            o.send(msg)
            o.close()
        #kill branch
        elif avail is k:
            print("Recieved kill signal")
            remv = k.accept()[0]
            k.close()
            exit()
            
            
