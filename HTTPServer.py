import configparser
import mimetypes
import os, sys
import socket
import threading

# Load the configuration file
config = configparser.ConfigParser()
config.read('conf/httpd.conf')

# pyHTTPServer Class
class PyHTTPServer(object):
    def __init__(self):
        # Init socket
        try:
            # Try to create socket and bind host & port
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((config['pyHTTP']['host'], int(config['pyHTTP']['port'])))    

        except socket.error:
            # Unable to create socket
            print("Error: Can't create socket, port already in use")
            sys.exit()
    
    def srvListen(self):
        # Socket listen
        self.sock.listen(int(config['pyHTTP']['maxOutstandingCon']))
        print("pyHTTP Server running on %s:%s" % (config['pyHTTP']['host'], config['pyHTTP']['port']))

# Main
PyHTTPServer().srvListen()
