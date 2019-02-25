import configparser
import datetime
import errno
import mimetypes
import os
import socket
import sys
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
            self.allowedMethods = config['pyHTTP']['allowMethods'].split(',')

        except socket.error:
            # Unable to create socket
            print("Error: Can't create socket, port already in use")
            sys.exit()
    
    def srvListen(self):
        # Socket listen
        self.sock.listen(int(config['pyHTTP']['maxOutstandingCon']))
        print("pyHTTP Server running on %s:%s" % (config['pyHTTP']['host'], config['pyHTTP']['port']))
        
        while True:
            try:
                # Accept connection
                c, addr = self.sock.accept()
                #print("Connection Accepted")

                # Set timeout
                c.settimeout((int(config['pyHTTP']['conTimeout']) / threading.active_count()) if config['pyHTTP']['dynamicTimeout'] == 'true' else  int(config['pyHTTP']['conTimeout']))

                # Accept connection & create thread
                threading.Thread(target = self.request,args = (c,addr)).start()
            except:
                c.close()
        
    def request(self, c, address):
        while True:
            try:
                # Receive & parse request
                requestStr = self.parseRequest(c.recv(int(config['pyHTTP']['recvBuffer'])).decode())
                if requestStr:
                    req, head, body = requestStr

                    # Detect if keep-alive
                    closeConn = True if head.get('Connection') != 'keep-alive' else False

                    # If method NOT allowed close connection
                    if (req.get('method') not in self.allowedMethods):
                         # Return error
                        c.sendall(req.get('version').encode() + " 405 Method Not Allowed\r\n\r\n405 - Method not allowed")
                        c.close()
                        break

                    # Determine method (e.g. GET, POST, PUT, DELETE)
                    if (req.get('method') == "GET"):
                    # GET method
                        req['resource'] = '/index.html' if req.get('resource') == '/' else req.get('resource')

                        # Try to open the resource if not trow exception
                        try:
                            with open(config['pyHTTP']['rootDir'] + req.get('resource')) as f:
                                fCont = f.read()
                            response = " 200 OK"
                        except IOError as x:
                            # If file can't be open
                            
                            if x.errno == errno.ENOENT:
                                response = " 404 Not Found"
                                fCont = "File not found" 
                            elif x.errno == errno.EACCES:
                                response = " 401 Unauthorized"
                                fCont = "Action requires user authentication"
                            else:
                                response = " 500 Internal server error"
                                fCont = "Internal server error"
                        
                        # Prepare head
                        cDate = datetime.datetime.now().strftime("%a, %d %b %Y %H:%I:%S %Z") #get current date
                        cHead = "\r\nDate: %s\r\nContent-Type: %s \r\n\r\n" % (cDate, mimetypes.guess_type(config['pyHTTP']['rootDir'] + req.get('resource'))[0])
                        
                         # Response to client
                        c.sendall(req.get('version').encode() + response.encode() + cHead + fCont)
                    
                    elif (req.get('method') == "HEAD"):
                    # HEAD method
                        req['resource'] = '/index.html' if req.get('resource') == '/' else req.get('resource')

                        # Try to open the resource if not trow exception
                        try:
                            with open(config['pyHTTP']['rootDir'] + req.get('resource')) as f:
                                response = " 200 OK"
                        except IOError as x:
                            if x.errno == errno.ENOENT:
                                response = " 404 Not Found"
                                fCont = "File not found" 
                            elif x.errno == errno.EACCES:
                                response = " 401 Unauthorized"
                                fCont = "Action requires user authentication"
                            else:
                                response = " 500 Internal server error"
                                fCont = "Internal server error"
                        
                        # Prepare head
                        cDate = datetime.datetime.now().strftime("%a, %d %b %Y %H:%I:%S %Z") #get current date
                        cHead = "\r\nDate: %s\r\nContent-Type: %s \r\n\r\n" % (cDate, mimetypes.guess_type(config['pyHTTP']['rootDir'] + req.get('resource'))[0])
                        
                         # Response to client
                        c.sendall(req.get('version').encode() + response.encode() + cHead + fCont)                            
                    
                    
                    # If required, close connection
                    if closeConn:
                        c.close()
            except:
                # Timeout
                c.close()
                return False

    def parseRequest(self, rStr):
    # Parse request, header, & body
        try:
            if len(rStr) > 1: 
                # Get body
                s, b = rStr.split('\r\n\r\n')
                # Get request (method, resource, HTTP version)
                s = s.split('\r\n')
                r, h  = ({},{})            
                r['method'], r['resource'], r['version'] = s[0].split(' ', 2)

                s = s[1:]
                for f in s:
                    key, value = f.split(':', 1)
                    h[key] = value
                return(r, h, b)
            else:  
                # Empty request
                return False
        except:
            # Invalid request
            return False

# Main
PyHTTPServer().srvListen()