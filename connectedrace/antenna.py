import socketserver
import threading

class BridgeHandler(socketserver.DatagramRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]

class Bridge(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass

class Cannon():
    pass

class HanSolo(object):
    def __init__(self, ):
        server = Bridge((host, port), BridgeHandler)
        ip, port = server.server_address

        server_thread = threading.Thread(server.serve_forever)

