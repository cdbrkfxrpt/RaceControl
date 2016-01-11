import socket, socketserver
import threading, pickle
import time
import can
from globals import D_PORT, PROTOCOL

class Cannon:
    def __init__(self, antennad, port=D_PORT, timeout=100):
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
        for n in self.antennad.nodes:
            # print('Firing projectile ', self.projectile)
            self.sock.sendto(self.projectile, (n, self.port))
        self.projectile = b''
        self.trigger = time.perf_counter()

    def operate(self):
        while self.running.is_set():
            msg = self.buffer.get_message(0)
            if msg:
                self.projectile += b'#'
                self.projectile += pickle.dumps(msg)

            if ((time.perf_counter() - self.trigger) > (self.timeout / 1000)
                and self.projectile ):
                self.fire()
