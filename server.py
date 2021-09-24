#  coding: utf-8 
import socketserver
import sys, os, datetime
from urllib.parse import unquote

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# Copyright 2021 Tianying Xia
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        # 1 self.data = self.request.recv(1024).strip()
        '''
        self.full_data = b''
        while True:
            data = self.request.recv(1024)
            if not data:
                break
            self.full_data += data # b-String '''
        self.full_data = self.request.recv(1024)
        self.full_data_string = self.full_data.strip().decode() # String 
        #print(self.full_data_string)
        self.full_data_line_list = self.full_data_string.split('\r\n') # List 
        #print(self.full_data_line_list)
        
        # Start handling Request-Line 
        self.close_connection = False
        self.status_code = None
        self.request_line = self.full_data_line_list[0] # String 
        if not self.request_line:
            self.close_connection = True # Receive nothing 
            return
        #print(self.request_line)
        self.command = None
        self.path = None
        self.request_line_words = self.request_line.split()
        if len(self.request_line_words) == 0:
            self.status_code = 405
        if len(self.request_line_words) >= 3: # Check components amount 
            #print(self.request_line_words)
            version = self.request_line_words[-1]
            try:
                if not version.startswith('HTTP/'):
                    raise ValueError
                base_version_number = version.split('/', 1)[1]
                if base_version_number != '1.1': # HTTP 1.1 compliant webserver
                    raise ValueError
            except (ValueError, IndexError):
                #print('Not HTTP 1.1')
                self.status_code = 405
        if len(self.request_line_words) == 2:
            self.status_code = 405
        self.command, self.path = self.request_line_words[:2]
        self.path = 'www' + unquote(self.path)
        if self.command != 'GET':
            self.status_code = 405
        
        # Handle path 
        self.se_body = ''
        if self.status_code != 405:
            file_path = None
            redirect_path = None
            content_type = None
            if self.path.endswith('/'):
                file_path = self.path + 'index.html'
                if os.path.exists(file_path):
                    rfile = open(file_path, mode='r')
                    self.se_body += rfile.read()
                    rfile.close()
                    self.status_code = 200
                    content_type = 'text/html'
                else:
                    self.status_code = 404
            else:
                if os.path.exists(self.path):
                    file_path = self.path
                    rfile = open(file_path, mode='r')
                    self.se_body += rfile.read()
                    rfile.close()
                    self.status_code = 200
                    if file_path.endswith('.html'):
                        content_type = 'text/html'
                    elif file_path.endswith('.css'):
                        content_type = 'text/css'
                    else:
                        content_type = 'application/octet-stream'
                else:
                    file_path = self.path + '/index.html'
                    if os.path.exists(file_path):
                        self.status_code = 301
                        redirect_path = file_path
                    else: 
                        self.status_code = 404
        
        # Response 
        self.response_str = None
        status = None
        
        if self.status_code == 200:
            status = 'OK'
            self.response_str = version + ' ' + str(self.status_code) + ' ' + status + '\r\n' + 'Date: ' + str(datetime.datetime.now()) + '\r\n' + 'Content-Type: ' + content_type + '\r\n' + 'Content-Length: ' + str( len(self.se_body) ) + '\r\n' + 'Connection: ' + 'keep-alive' + '\r\n' +  '\r\n' + self.se_body
            #print(self.response_str)
        
        elif self.status_code == 301:
            status = 'Moved Permanently'
            self.se_body += '''
            <!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
            <html><head>
            <title>301 Moved Permanently</title>
            </head><body>
            <h1>Moved Permanently</h1>
            <p>The document has moved.</p>
            </body></html>
            '''
            self.response_str = version + ' ' + str(self.status_code) + ' ' + status + '\r\n' + 'Date: ' + str(datetime.datetime.now()) + '\r\n' + 'Content-Type: ' + 'text/html' + '\r\n' + 'Content-Length: ' + str( len(self.se_body) ) + '\r\n' + 'Connection: ' + 'close' + 'Location: ' + 'http://' + redirect_path + '\r\n' +  '\r\n' + self.se_body
            #print(self.response_str)
            
        elif self.status_code == 404:
            status = 'Not Found'
            self.se_body += '''
            <!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
            <html><head>
            <title>404 Not Found</title>
            </head><body>
            <h1>Not Found</h1>
            <p>The document is not found.</p>
            </body></html>
            '''
            self.response_str = version + ' ' + str(self.status_code) + ' ' + status + '\r\n' + 'Date: ' + str(datetime.datetime.now()) + '\r\n' + 'Content-Type: ' + 'text/html' + '\r\n' + 'Content-Length: ' + str( len(self.se_body) ) + '\r\n' + 'Connection: ' + 'close' + '\r\n' +  '\r\n' + self.se_body
            #print(self.response_str)
            
        elif self.status_code == 405:
            status = 'Method Not Allowed'
            self.se_body += '''
            <!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
            <html><head>
            <title>405 Method Not Allowed</title>
            </head><body>
            <h1>Method Not Allowed</h1>
            <p>The method is not allowed.</p>
            </body></html>
            '''
            self.response_str = version + ' ' + str(self.status_code) + ' ' + status + '\r\n' + 'Date: ' + str(datetime.datetime.now()) + '\r\n' + 'Content-Type: ' + 'text/html' + '\r\n' + 'Content-Length: ' + str( len(self.se_body) ) + '\r\n' + 'Connection: ' + 'close' + '\r\n' +  '\r\n' + self.se_body
            #print(self.response_str)
        
        # 2 print ("Got a request of: %s\n" % self.data)
        # 3 self.request.sendall(bytearray("OK",'utf-8'))
        
        self.request.sendall( self.response_str.encode() )
        
        

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
