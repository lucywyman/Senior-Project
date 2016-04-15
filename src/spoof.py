#!/usr/local/bin/python3.2

import socket
c = socket.socket(socket.AF_INET,socket.SOCK_STREAM);
c.connect(('127.0.0.1', 9000))      #'\0recvPort')
c.send('{"sub_ID":83}'.encode())