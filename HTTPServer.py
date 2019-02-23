import configparser
import mimetypes
import os, sys
import socket
import threading

# Load the configuration file
config = configparser.ConfigParser()
config.read('conf/httpd.conf')

# pyHTTPServer Class
class PyHTTPServer:
    def __init__(self):
        # Init socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((config['pyHTTP']['host'], int(config['pyHTTP']['port'])))    
        print("pyHTTP Server running on %s:%s" % (config['pyHTTP']['host'], config['pyHTTP']['port']))


# Main

x = PyHTTPServer()
