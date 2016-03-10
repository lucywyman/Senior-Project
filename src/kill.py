#!/usr/local/bin/python3.2
import socket
c = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);
c.connect('\0killPort')
c.send('{"state":"die"}'.encode())