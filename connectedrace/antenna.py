import socketserver
import socket
import sys
import threading
import re
import pickle
import time
import can

PORT = 5252

class AntennaDaemon:
    def __init__(self, port=PORT, listeners=[], nodes=[]):
        self.port = port

        self.listeners = []
        for l in listeners:
            add_listener(l)

        self.nodes = []
        for n in nodes:
            add_target(n)

        self.cannon = Cannon(self, timeout=2000)

        self.running = threading.Event()
        self.running.set()

        bucket = Bucket(('localhost', port), BucketHandler, self)
        self._server = threading.Thread(target=bucket.serve_forever)
        self._server.daemon = True

        self._server.start()

    def add_listener(self, listener):
        if isinstance(listener, can.Listener):
            self.listeners.append(listener)
        else:
            raise TypeError('Only can.Listeners allowed.')

    def add_node(self, node):
        if re.match(r"(\d{1,3}\.{1}){3}\d{1,3}", n):
            self.nodes.append(n)
        else:
            raise TypeError('Only IPv4 addresses allowed.')

    def notify(self, msg):
        for listener in listeners:
            listener(msg)

class BucketHandler(socketserver.DatagramRequestHandler):
    def handle(self):
        if self.client_address in self.server.antennad.nodes:
            msglist = rfile.read().split(b'#')
            msglist = list(filter(None, msglist))
            for msg in msglist:
                try:
                    print('Received message ', msg)
                    self.server.antennad.notify(pickle.loads(msg))
                except pickle.UnpicklingError:
                    # self.errlog.write('corrupted data')
                    print('corrupted data received')

class Bucket(socketserver.UDPServer):
    def __init__(self, server_address, BucketHandlerClass, antennad):
        super().__init__(server_address, BucketHandlerClass)
        self.antennad = antennad

class Cannon:
    def __init__(self, antennad, port=PORT, timeout=100):
        self.buffer = can.BufferedReader()
        self.antennad = antennad
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.timeout = timeout
        self.projectile = b''
        self.trigger = time.perf_counter()

        self.running = threading.Event()
        self.running.set()

        self._mechanism = threading.Thread(target=self.operate)
        self._mechanism.daemon = True

        self._mechanism.start()

    def fire(self):
        for t in self.antennad.nodes:
            print('Firing projectile ', self.projectile)
            self.sock.sendto(self.projectile, (t, self.port))
        self.projectile = b''
        self.trigger = time.perf_counter()

    def operate(self):
        while self.running.is_set():
            msg = self.buffer.get_message(0)
            if msg:
                self.projectile += b'#'
                self.projectile += pickle.dumps(msg)
                # print('Pickled message ', msg)

            if ((time.perf_counter() - self.trigger) > (self.timeout / 1000)
                and self.projectile ):
                self.fire()
