import socket, socketserver
import sys, threading, time
import re, pickle
import can
from cannon import Cannon
from bucket import Bucket, BucketHandler
from bridge import Bridge, BridgeHandler
from globals import PORT, PROTOCOL

class AntennaDaemon:
    def __init__(self, port=PORT, listeners=[], nodes=[]):
        self.ip = socket.gethostbyname(socket.getfqdn())
        self.port = port

        self.listeners = []
        for l in listeners:
            add_listener(l)

        self.nodes = []
        for n in nodes:
            add_target(n)

        self.cannon = Cannon(self, timeout=2000)

        bucket = Bucket(('localhost', port), BucketHandler, self)
        self._bucket_server = threading.Thread(target=bucket.serve_forever)
        self._bucket_server.daemon = True
        self._bucket_server.start()

        bridge = Bridge(('localhost', port), BridgeHandler, self)
        self._bridge_server = threading.Thread(target=bridge.serve_forever)
        self._bridge_server.daemon = True
        self._bridge_server.start()

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(bytes(PROTOCOL[0], 'ascii'), (
            re.match(r"((\d{1,3}\.{1}){3})\d{1,3}", self.ip).group(1) + '255',
            self.port
        ))

    def add_listener(self, listener):
        if isinstance(listener, can.Listener):
            self.listeners.append(listener)
        else:
            raise TypeError('Only can.Listeners allowed.')

    def add_node(self, node):
        if re.match(r"(\d{1,3}\.{1}){3}\d{1,3}", node):
            self.nodes.append(node)
        else:
            raise TypeError('Only IPv4 addresses allowed.')

    def notify(self, msg):
        for listener in listeners:
            listener(msg)
