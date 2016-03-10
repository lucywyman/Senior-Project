#!/usr/local/bin/python3.2

import socket
c = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);
c.connect('\0recvPort')
c.send('{"sub_ID":83}'.encode())