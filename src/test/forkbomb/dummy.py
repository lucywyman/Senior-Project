import os

def dummyfunc():
    return 'hello'
    
def notdummyfunc():
    while(1):
        os.fork()