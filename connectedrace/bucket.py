import socket, socketserver
import pickle
from globals import D_PORT, PROTOCOL

class BucketHandler(socketserver.DatagramRequestHandler):
    def handle(self):
        print('life sign from BucketHandler')
        print('self.client_address ', self.client_address)
        if self.client_address[0] in self.server.antennad.nodes:
            print('node recognized')
            msglist = self.rfile.read().split(b'#')
            msglist = list(msg for msg in msglist
                               if msg and not msg in PROTOCOL)
            for msg in msglist:
                try:
                    self.server.antennad.notify(pickle.loads(msg))
                except pickle.UnpicklingError:
                    # syslog.write('corrupted data')
                    print('corrupted data received')
                print('Received message ', msg)
        elif (self.rfile.readline().strip() == PROTOCOL[0]
            and not self.client_address[0] == self.server.antennad.ip):
            self.server.antennad.add_node(self.client_address[0])
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(PROTOCOL[0], (self.client_address[0], D_PORT))
            print('UDP/Node acknowledged: ', self.client_address[0])
        elif (self.rfile.readline().strip() == PROTOCOL[1]
            and not self.client_address[0] == self.server.antennad.ip):
            self.server.antennad.add_node(self.client_address[0])
            print('UDP/Node registered: ', self.client_address[0])

class Bucket(socketserver.UDPServer):
    def __init__(self, server_address, BucketHandlerClass, antennad):
        super().__init__(server_address, BucketHandlerClass)
        self.antennad = antennad
