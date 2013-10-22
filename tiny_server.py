#!/bin/python
import sys
import socket

class HTTPServer(object):
    
    def __init__(self, bind_addr, msg='Hello, Nginx!'):
        self.bind_addr = bind_addr
        self.msg = msg 
    
    def start(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print self.bind_addr
            self.sock.bind(self.bind_addr)

        except socket.error, e:
            if self.sock:
                self.sock.close()
            self.sock = None
            raise e
        
        self.sock.listen(5)
        
        while True:
            conn, addr = self.sock.accept()
            try:   
                buf = conn.recv(2048)  
                print buf
                conn.send(self.msg + '\n')  
  
            except socket.timeout, e:  
                raise e 
            finally:
                conn.close()
                          

if (len(sys.argv) < 4):
        print 'params error, please input: python tiny_server 127.0.0.1 8080 "hello, nginx"'
else:
        HTTPServer((sys.argv[1], int(sys.argv[2])), sys.argv[3]).start()
