#!/usr/bin/python3.4
import socket
c = socket.socket(socket.AF_INET,socket.SOCK_STREAM);
c.connect(('127.0.0.1', 9001))      #'\0killPort')
c.send('{"state":"die"}'.encode())