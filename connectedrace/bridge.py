import socket, socketserver
import sys, time, pickle
from connectedrace.globals import PROTOCOL

class BridgeHandler(socketserver.StreamRequestHandler):
    def handle(self):
        pass

class Bridge(socketserver.TCPServer):
    def __init__(self, server_address, BridgeHandlerClass, antennad):
        super().__init__(server_address, BridgeHandlerClass)
        self.antennad = antennad
