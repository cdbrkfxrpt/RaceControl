import socket, socketserver
import sys, time, pickle
from globals import PORT, PROTOCOL

class BridgeHandler(socketserver.StreamRequestHandler):
    def handle(self):
        try:
           protocol_i = PROTOCOL.index(rfile.readline().strip)
        except ValueError:
            # syslog.write('Faulty message received')
            pass

        if protocol_i == 0:
            self.server.antennad.add_node(self.client_address)
            wfile.write(PROTOCOL[1])
            print('Node acknowledged: ', self.client_address)
        elif protocol_i == 1:
            self.server.antennad.add_node(self.client_address)
            print('Node registered: ', self.client_address)
        else:
            # should be ValueError anyway
            pass

class Bridge(socketserver.TCPServer):
    def __init__(self, server_address, BridgeHandlerClass, antennad):
        super().__init__(server_address, BridgeHandlerClass)
        self.antennad = antennad
