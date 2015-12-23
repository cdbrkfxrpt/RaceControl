import socketserver
import threading

class BridgeHandler(socketserver.DatagramRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]

class Bridge():
    pass

class CannonHandler(socketserver.DatagramRequestHandler):
    def handle(self):
        pass

class Cannon():
    pass

