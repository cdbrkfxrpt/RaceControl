import socket, socketserver
import pickle
from globals import D_PORT, PROTOCOL

class BucketHandler(socketserver.DatagramRequestHandler):
    def handle(self):
        node_msg = self.rfile.read().strip()
        if self.client_address[0] in self.server.antennad.nodes:
            node_msg = node_msg.split(b'#')
            node_msg = list(msg for msg in node_msg
                               if msg and not msg in PROTOCOL)
            for msg in node_msg:
                try:
                    self.server.antennad.notify(pickle.loads(msg))
                except pickle.UnpicklingError:
                    # syslog.write('corrupted data')
                    print('corrupted data received')
                print('Received message ', msg)
        elif (node_msg == PROTOCOL[0]
            and not self.client_address[0] == self.server.antennad.ip):
            self.server.antennad.add_node(self.client_address[0])
            print('UDP/Node acknowledged: ', self.client_address[0])
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(PROTOCOL[1], (self.client_address[0], D_PORT))
        elif (node_msg == PROTOCOL[1]
            and not self.client_address[0] == self.server.antennad.ip):
            self.server.antennad.add_node(self.client_address[0])
            print('UDP/Node registered: ', self.client_address[0])

class Bucket(socketserver.UDPServer):
    def __init__(self, server_address, BucketHandlerClass, antennad):
        super().__init__(server_address, BucketHandlerClass)
        self.antennad = antennad
