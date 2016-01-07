import socketserver
import can
import threading
import re

class AntennaDaemon(object):
    def __init__(self, port=5252, listeners=[], targets=[]):
        self.port = port

        self.listeners = []
        for l in listeners:
            add_listener(l)

        self.targets = []
        for t in targets:
            add_target(t)

        self.bridge = Bridge(('localhost', self.port), BridgeHandler)

    def add_listener(self, listener):
        if isinstance(l, can.Listener):
            self.listeners.append(l)
        else:
            raise TypeError('Only can.Listeners allowed.')

    def add_target(self, target):
        if re.match(r"(\d{1,3}\.{1}){3}\d{1,3}", t):
            self.targets.append(t)
        else:
            raise TypeError('Only IPv4 addresses allowed.')



class BridgeRequestHandler(socketserver.DatagramRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]

class BridgeHandler(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass

class Bridge(object):
    def __init__(self)

class HanSolo(object):
    def __init__(self, ):
        server = Bridge((host, port), BridgeHandler)
        ip, port = server.server_address

        server_thread = threading.Thread(server.serve_forever)
